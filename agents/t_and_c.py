import os
import openai
import textwrap
import pinecone
import uuid
import pickle
from typing import List
import streamlit as st
from streamlit_chat import message
from transformers import GPT2TokenizerFast
import datetime
from multiprocessing import Queue

openai.api_key = st.secrets["openai"]
# PROMPT = "Using only the information found in exerts and their given context, answer the query. If the information is not in the exert, answer that you are unsure.\n"
PROMPT = "Using only the information found in exerts and their given context, answer the query. If the information is not in the exert, say that you are unable to answer, if it is, support your answer with quotes directly from the exert.\n"


def build_gpt_query(paragraphs, query, user_policy_info, user_messages, ai_messages, prompt):
    '''
    Add the paragraphs most relevant to the query and a query to a message to be sent to GPT
    '''
    gpt_query = user_policy_info + prompt + "\n"
    for i in range(len(paragraphs)):
        gpt_query += f'Exert {paragraphs[i]}:\n'
    if len(ai_messages)>1:
        gpt_query += f'Query: {user_messages[-2]}\n'
        gpt_query += f'Response: {ai_messages[-2]}\n'
        gpt_query+=f'Query: {user_messages[-1]}\n'
        gpt_query+=f'Response: {ai_messages[-1]}\n'
    if len(ai_messages)==1:
        gpt_query+=f'Query: {user_messages[-1]}\n'
        gpt_query+=f'Response: {ai_messages[-1]}\n'
    gpt_query += f'Query: {query}\nResponse:'
    return gpt_query

def embed_query(query, user_messages, ai_messages):
    new_query = ""
    if len(ai_messages)>1:
        new_query += f'Query: {user_messages[-2]}\n'
        new_query += f'Response: {ai_messages[-2]}\n'
        new_query+=f'Query: {user_messages[-1]}\n'
        new_query+=f'Response: {ai_messages[-1]}\n'
    if len(ai_messages)==1:
        new_query+=f'Query: {user_messages[-1]}\n'
        new_query+=f'Response: {ai_messages[-1]}\n'
    new_query += f'Query: {query}'
    embedded_query = openai.Embedding.create(
        input=new_query,
        model="text-embedding-ada-002"
    )['data'][0]['embedding']
    return embedded_query

def distributor_matches(index, query, distributors, number_of_results):
    results = []
    # print(index)
    # print(query)
    # print(distributors)
    for d in distributors:
        matches = index.query(
            vector=query,
            top_k=1,
            include_metadata=True,
            filter={
                "distributor": {"$eq": d.lower()}
            },
        )["matches"]
        results.append(matches[0])
    results = sorted(results, key=lambda d: d['score'], reverse=True)
    return results[:number_of_results]

def ask_tess(logging_queue, session_id,  query, index, chunks_dict, user_messages, ai_messages, prompt, distributor = None, user_policy_info = ""):
    embedded_query = embed_query(query, user_messages, ai_messages)
    if distributor is None:
        service = "T&C admin"
        # matches = distributor_matches(index, embedded_query, distributors, number_of_results=5)
        matches = index.query(
            vector=embedded_query,
            top_k=5,
            include_metadata=True,
        )["matches"]
    else:
        service = "T&C customer"
        matches = index.query(
            vector=embedded_query,
            top_k=5,
            include_metadata=True,
            filter={
                "distributor": {"$in": [distributor.lower(), "all"]}
            },
        )["matches"]
    paragraphs = [chunks_dict[i["id"]] for i in matches]
    gpt_query = build_gpt_query(paragraphs, query, user_policy_info, user_messages, ai_messages, prompt)
    response = openai.Completion.create(model="text-davinci-003", prompt=gpt_query, temperature=0.2, max_tokens=500)
    logging_queue.put((uuid.uuid4(), session_id, service,
                            datetime.datetime.now(),
                            prompt,
                            query, response["choices"][0].text, gpt_query))
    return response["choices"][0].text




