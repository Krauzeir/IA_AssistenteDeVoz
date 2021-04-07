import speech_recognition as sr
from nltk import word_tokenize, corpus
import json

IDIOMA_CORPUS = "portuguese"
IDIOMA_FALA = "pt-BR"
CAMINHO_CONFIGURACAO = "config.json"

def iniciar():
    global reconhecedor
    global palavras_da_parada
    
    global nome_assistente
    global perguntas
    global assuntos
    
    reconhecedor = sr.Recognizer()
    palavras_da_parada = set(corpus.stopwords.words(IDIOMA_CORPUS))
    palavras_da_parada.remove("qual")

    
    
    with open(CAMINHO_CONFIGURACAO, "r") as arquivo_configuracao:
        configuracao = json.load(arquivo_configuracao)
        
        nome_assistente = configuracao["nome"]
        perguntas = configuracao["perguntas"]
        assuntos = configuracao["assuntos"]
        
        arquivo_configuracao.close()
    

def escutar_pergunta():
    global reconhecedor
    global palavras_da_parada
    
    pergunta = None
    
    with sr.Microphone() as fonte_audio:
        reconhecedor.adjust_for_ambient_noise(fonte_audio)
        
        print("pergunta alguma coisa sobre marketing ou marketing digital...")
        fala = reconhecedor.listen(fonte_audio)
        
        try:
            pergunta = reconhecedor.recognize_google(fala, language=IDIOMA_FALA)
            pergunta = pergunta.lower()
            
            print("pergunta reconhecida: ", pergunta)
        except sr.UnknownValueError:
            pass
        
    return pergunta

def eliminar_palavras_de_parada(tokens):
    global palavras_da_parada
    
    tokens_filtrados = []
    for token in tokens:
        if token not in palavras_da_parada:
            tokens_filtrados.append(token)
            
    return tokens_filtrados

def tokenizar_pergunta(pergunta):
    global nome_assistente
    
    partes_pergunta = None
    
    tokens = word_tokenize(pergunta, IDIOMA_CORPUS)
    if tokens:
        tokens = eliminar_palavras_de_parada(tokens)
        
        total_tokens = len(tokens)
        if total_tokens >= 3:
            if nome_assistente == tokens[0]:
                partes_pergunta = []
                for i in range(1, total_tokens):
                    partes_pergunta.append(tokens[i])
                    
    return partes_pergunta

def reconhecer_pergunta(partes_pergunta):
    global perguntas
    
    valida = False
    total_partes_pergunta = len(partes_pergunta)
    total_partes_validas = 0
    
    for pergunta_prevista in perguntas:
        partes_previstas = word_tokenize(pergunta_prevista, IDIOMA_CORPUS)
        total_partes_previstas = len(partes_previstas)
        
        if total_partes_previstas <= total_partes_pergunta:
            total_partes_validas = 0
            for i in range(0, total_partes_previstas):
                if partes_previstas[i] == partes_pergunta[i]:
                    total_partes_validas = total_partes_validas + 1
            
            if total_partes_validas == total_partes_previstas:
                valida = True

            
                break
            
    return valida, total_partes_validas

def reconhecer_assunto(partes_assunto):
    global assuntos

    valida = False
    resposta = None
    total_partes_assunto = len(partes_assunto)
    
    for assunto_previsto in assuntos:
        partes_previstas = word_tokenize(assunto_previsto["nome"], IDIOMA_CORPUS)
        total_partes_prevista = len(partes_previstas)
        
        if total_partes_prevista <= total_partes_assunto:
            total_partes_validas = 0
            for i in range(0, total_partes_prevista):
                if partes_previstas[i] == partes_assunto[i]:
                    total_partes_validas =  total_partes_validas + 1
                    
            if total_partes_validas == total_partes_prevista:
                resposta = assunto_previsto["resposta"]
                valida = True
                
                break
                    
    return valida, resposta
    
if __name__ == '__main__':
    iniciar()
        
    continuar = True
    while continuar:
        pergunta = escutar_pergunta()
        
        pergunta_valida, assunto_valida = False, False
        
        if pergunta:
            partes_pergunta = tokenizar_pergunta(pergunta)
            
            if partes_pergunta:
                pergunta_valida, total_partes_reconhecidas = reconhecer_pergunta(partes_pergunta)

                if pergunta_valida:
                    partes_assunto = partes_pergunta[total_partes_reconhecidas:]
                    assunto_valida, resposta = reconhecer_assunto(partes_assunto)
                    
                    if assunto_valida:
                        print("Resposta é:", resposta)
        
        if not (pergunta_valida and assunto_valida):
            print("Não entendi a pergunta. Repita por favor!!")
                        
