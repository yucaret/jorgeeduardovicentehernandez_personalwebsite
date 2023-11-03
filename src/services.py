import sett
import os
import sys

import requests
import json
import time
import openai
import time



#######################

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
#######################

openai.api_key = sett.openai_api

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