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

openai.api_key = st.secrets["openai"]


def doc_chunker(doc_text, chunk_size, overlap) -> List:
    '''
    Split a document into chunks. Currently just breaks on characters. In future it would be good to upgrade to sentences
    or paragraphs
    '''
    # chunks = textwrap.wrap(doc_text,2000)
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    tokens = tokenizer.encode(doc_text)
    chunks = []
    i = 0
    while i + chunk_size < len(tokens):
        chunks.append(tokenizer.decode(tokens[i:i + chunk_size]))
        i += chunk_size - overlap
    chunks.append(tokenizer.decode(tokens[i:]))
    return chunks


# def summarise_doc(chunks, context):
#     initial_chunk_context = "Summarize the following start of a  "+context+":\n"+chunks[0]
#     summary = openai.Completion.create(model="text-davinci-003", prompt=initial_chunk_context, temperature=0.2)
#     summary.choices[0].text
#     for c in chunks[1:]:
#         subsequent_chunk_context = "A "+context+" that started with information summarised in the following way:" + summary + \
#                                    "Write a summary for the summarised text and the following exert that comes after " \
#                                    "the summarised text:\n"+c
#         summary = openai.Completion.create(model="text-davinci-003", prompt=subsequent_chunk_context, temperature=0.2)
#     return summary

def init_pinecone(embedding_size):
    '''
    Return an empty pinecone index
    :param embedding_size: The size of the openai embedding
    :return: A pinecone index object
    '''
    pinecone.init(
        api_key=st.secrets["pinecone"]
    )
    if 'openai' not in pinecone.list_indexes():
        pinecone.create_index('openai', dimension=embedding_size)
        index = pinecone.Index('openai')
    else:
        index = pinecone.Index('openai')
        index.delete(delete_all=True)
    return index


def add_context(chunks, context):
    return [context + c for c in chunks]


def embed(chunks):
    '''
    Create embedding representations of chunks of text
    '''
    embedded_chunks = []
    for c in chunks:
        response = openai.Embedding.create(
            input=c,
            model="text-embedding-ada-002"
        )
        embedded_chunks.append(response['data'][0]['embedding'])
    return embedded_chunks


def create_structures(chunks, embedded_chunks, chunk_metadata):
    '''
    Create a dictionary of chunks of texts indexed by guuids and a list of guuid chunk embedding tuples to be used
    by pinecone. The guuids link the chunks of text to their embeddings.
    '''
    ids = [str(uuid.uuid4()) for i in range(len(chunks))]
    chunks_dict = {}
    embedding_tuples = []
    for i, c, e, m in zip(ids, chunks, embedded_chunks, chunk_metadata):
        chunks_dict[i] = c
        embedding_tuples.append((i, e, m))
    return chunks_dict, embedding_tuples


def build_gpt_query(paragraphs, query):
    '''
    Add the paragraphs most relevant to the query and a query to a message to be sent to GPT
    '''
    gpt_query = "Using only the information found in exerts and their given context, answer the query. If the information is not in the exert, answer that you are unsure.\n"
    for i in range(len(paragraphs)):
        gpt_query += f'Exert {paragraphs[i]}:\n'
    gpt_query += f'Query: {query}'
    return gpt_query


def populate_pinecone():
    '''
    Chunk up all documents, add context to the chunks, and store the embeddings in pinecone with keys that can index
    a dictionary to retrieve the source text
    '''
    all_chunks = []
    chunk_metadata = []
    for f in os.listdir('./scratch/data'):
        with open(f'./scratch/data/{f}/{f}.txt', 'r', encoding='utf-8') as fp:
            text = fp.read()
        context = f'The following is an exert from a document outlining terms and conditions for a life insurance product from the distributor {f}:\n'
        chunks = doc_chunker(text, 500, 150)
        chunks = add_context(chunks, context)
        all_chunks.extend(chunks)
        chunk_metadata.extend([{"distributor": f} for c in chunks])
    embedded_chunks = embed(all_chunks)
    chunks_dict, embedding_tuples = create_structures(all_chunks, embedded_chunks, chunk_metadata)
    index = init_pinecone(len(embedded_chunks[0]))
    index.upsert(embedding_tuples)
    with open('./scratch/chunk_dictionary.json', 'wb') as fp:
        pickle.dump(chunks_dict, fp)
    return chunks_dict, index


def distributor_matches(index, query, distributors, number_of_results, chat):
    results = []
    # print(index)
    # print(query)
    # print(distributors)
    for d in distributors:
        print(d)
        matches = index.query(
            vector=query,
            top_k=1,
            include_metadata=True,
            filter={
                "distributor": {"$eq": d}
            },
        )["matches"]
        print(matches)
        with chat:
            message(matches[0]["id"])
        results.append(matches[0])
    results = sorted(results, key=lambda d: d['score'], reverse=True)
    return results[:number_of_results]

def ask_tess(query, index, distributors, chunks_dict, chat):
    embedded_query = openai.Embedding.create(
        input=query,
        model="text-embedding-ada-002"
    )['data'][0]['embedding']
    # matches = index.query(
    #     vector=embedded_query,
    #     top_k=5,
    #     include_metadata=True
    # )["matches"]
    matches = distributor_matches(index, embedded_query, distributors, number_of_results=5, chat=chat)
    paragraphs = [chunks_dict[i["id"]] for i in matches]
    gpt_query = build_gpt_query(paragraphs, query)
    response = openai.Completion.create(model="text-davinci-003", prompt=gpt_query, temperature=0.2, max_tokens=500)
    return response["choices"][0].text


