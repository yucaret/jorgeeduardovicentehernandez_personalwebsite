import sett
import os
import csv

import requests
import openai

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from langchain import OpenAI

# The embedding engine that will convert our text to vectors
from langchain.embeddings.openai import OpenAIEmbeddings

from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.vectorstores import FAISS

from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import AgentTokenBufferMemory
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent

openai.api_key = sett.openai_api

def get_ubicacion_por_ip(ip):
    url = f"https://ipinfo.io/{ip}/json"
    response = requests.get(url)
    data = response.json()

    return data.get("country", "Desconocido")

def guardar_preguntas_usuarios(ip_usuario, country_usuario, mensaje_usuario, tipo_pregunta, fecha_actual, hora_actual):
    nombre_archivo = sett.preguntas_usuario_archivo

    # Comprobar si el archivo CSV ya existe
    archivo_existe = os.path.isfile(nombre_archivo)

    # Abrir el archivo CSV en modo de escritura
    with open(nombre_archivo, mode='a', newline='') as archivo_csv:
        campos = ['IP', 'COUNTRY', 'MENSAJE', 'TIPOPREGUNTA', 'FECHA', 'HORA']
        escritor_csv = csv.DictWriter(archivo_csv, fieldnames=campos)

        # Si el archivo no existe, escribir la fila de encabezados
        if not archivo_existe:
            escritor_csv.writeheader()

        # Escribir los valores en el archivo CSV
        escritor_csv.writerow({'IP': ip_usuario,
                               'COUNTRY': country_usuario,
                               'MENSAJE': mensaje_usuario,
                               'TIPOPREGUNTA': tipo_pregunta,
                               'FECHA': fecha_actual,
                               'HORA': hora_actual})

def procesar_imagen_barras_tipo_pregunta(ruta_archivo, ruta_imagen):
   # Leer los datos del archivo CSV
    df = pd.read_csv(ruta_archivo)

    # Contar la cantidad de filas por valor de TIPOPREGUNTA
    conteo_por_tipo_pregunta = df['TIPOPREGUNTA'].value_counts()
    
    # Elegir una paleta de colores
    paleta = sns.color_palette("husl", len(conteo_por_tipo_pregunta))

    # Redimensionar la figura (ajusta los números según tu preferencia)
    plt.figure(figsize=(2, 1.5))  # Aquí puedes ajustar el tamaño de la figura

    # Crear el gráfico de barras
    conteo_por_tipo_pregunta.plot(kind='bar', color=paleta)
    plt.xlabel('Tipo de Pregunta', fontsize = 4)
    plt.ylabel('Cantidad', fontsize = 4)

    # Ajustar el tamaño de la fuente
    plt.xticks(fontsize = 2)  # Tamaño de fuente para las etiquetas del eje x
    plt.yticks(fontsize = 2)  # Tamaño de fuente para las etiquetas del eje y
    plt.title('Bar graphic', fontsize=6)  # Tamaño de fuente para el título

    # Guarda el gráfico con el nuevo nombre de archivo
    plt.savefig(ruta_imagen, format='png', dpi=300, bbox_inches='tight', pad_inches=0.1)

def obtener_respuesta_gpt(user_message, conversacion):
    messages = [{'role':'system', 'content':'Responde respetuosamente a la persona que te pregunte algo y al final de tu respuesta siempre di\
                 chapapapapa'}]
    
    messages.append({'role': 'user', 'content': user_message})

    if (len(conversacion)> 0):
        messages.extend(conversacion)

    try:
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages,
            temperature = 0
        ) 
    except Exception as e:
        print('saliendo de  generar_respuesta_chatgpt: error no conecta a chatgpt exception ' + str(e))
        return 'no enviado'
    
    print("saliendo de generar_respuesta_chatgpt")

    return response.choices[0].message["content"]

def get_tipo_pregunta_gpt(user_message):
    # Indicaciones de que tipo de pregunta esta consultado el usuadio
    messages = [{'role':'system', 'content':"Devolver uno de los siguiente valores si el contexto de la pregunta se refiere a:\
                                            - Pide hablar acerca de Jorge, devolver solo 0.\
                                            - Pide hablar de la experiencia laboral o profesional, devolver 1.\
                                            - Pide habla de los datos de contacto, devolver 2.\
                                            - Pide hablar de los estudios y educación realizada, devolver 3.\
                                            - Pide hablar de las Certificaciones, devolver 4.\
                                            - Pide hablar de habilidades tecnicas o skills tecnicos, devolver 5.\
                                            - Pide conocer que idiomas conoce, devolver 6.\
                                            - Pide conocer saber si sabes de analisis de datos, de procesamiento \
                                            de datos, de ciencia de datos, o cualquier tema relacionado a datos; devolver 7.\
                                            - Pide conocer de experiencia en inteligencia artificial, devolver 8.\
                                            - Pide conocer de experiencia en computer vision, devolver 9.\
                                            - Pide conocer de experiencia en chatbots, devolver 10.\
                                            - Pide conocer porqué dices chapapapa, devolver 11.\
                                            - Pide hablar de otras cosas, devolver 12."}]
    
    # Se añade la consulta del usuario
    messages.append({'role': 'user', 'content': user_message})

    # Se envia la pregunta a chatgpt
    try:
        response = openai.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages = messages,
            temperature = 0
        ) 
    except Exception as e:
        print('saliendo de  get_tipo_pregunta_gpt: error no conecta a chatgpt exception ' + str(e))
        return '-1'
    
    print("saliendo de get_tipo_pregunta_gpt")

    # Se retorna la respuesta
    return response.choices[0].message["content"]

def configurar_agente():
    apikey_openai = sett.openai_api
    
    os.environ['OPENAI_API_KEY'] = apikey_openai
    
    llm = OpenAI(temperature = 0, openai_api_key = apikey_openai)
    
    archivo_txt = sett.curriculum_vitae_archivo
    
    # Leer el contenido del archivo
    with open(archivo_txt, 'r', encoding='utf-8') as archivo:
        contenido = archivo.read()
    
    headers_to_split_on = sett.cabeceras_dividir
    
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on = headers_to_split_on
    )
    
    texts = markdown_splitter.split_text(contenido)
    
    embeddings = OpenAIEmbeddings()
    
    db = FAISS.from_documents(texts, embeddings)
    
    retriever = db.as_retriever()
    
    tool = create_retriever_tool(
	    retriever,
	    "curriculum_vitae_jorge_eduardo_vicente_hernandez",
	    "Informacion del curriculum vitae de jorge eduardo vicente hernandez"
	)
    
    tools = [tool]
    
    llm = ChatOpenAI(temperature = 0)
    
    agent_executor = create_conversational_retrieval_agent(llm, tools, verbose=True)
    
    # This is needed for both the memory and the prompt
    memory_key = "history"
    
    memory = AgentTokenBufferMemory(memory_key=memory_key, llm=llm)
    
    system_message = SystemMessage(
        content=(
            sett.contexto_inicial
        )
    )
    
    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=system_message,
        extra_prompt_messages=[MessagesPlaceholder(variable_name=memory_key)]
    )
    
    agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
    
    agent_executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=True, return_intermediate_steps=True)
    
    return agent_executor