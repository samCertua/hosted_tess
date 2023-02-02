import pickle

import streamlit as st
import openai
from transformers import GPT2TokenizerFast
from typing import List
import pinecone
import json
import sqlalchemy
from urllib.parse import quote_plus
import uuid
import os

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

def init_pinecone(embedding_size):
    '''
    Return an empty pinecone index
    :param embedding_size: The size of the openai embedding
    :return: A pinecone index object
    '''
    pinecone.init(
        api_key=st.secrets["pinecone"]
    )
    if 'tess' not in pinecone.list_indexes():
        pinecone.create_index('tess', dimension=embedding_size)
        index = pinecone.Index('tess')
    else:
        index = pinecone.Index('tess')
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
    chunk_dicts = []
    embedding_tuples = []
    for i, c, e, m in zip(ids, chunks, embedded_chunks, chunk_metadata):
        chunk_dicts.append({"id": i, "distributor": m["distributor"], "node_text": c, "embedding": json.dumps(e)})
        embedding_tuples.append((i, e, m))
    return chunk_dicts, embedding_tuples

def add_document(document: str, context = None):
    with open("./data/"+document, 'r', encoding='utf-8') as fp:
        text = fp.read()
    distributor = document.replace(".txt","")
    if context is None:
        context = f'The following is an exert from a document outlining terms and conditions for a life insurance product from the distributor {distributor}:\n'
    chunks = doc_chunker(text, 500, 150)
    chunks = add_context(chunks, context)
    chunk_metadata = [{"distributor": distributor.lower()} for c in chunks]
    embedded_chunks = embed(chunks)
    chunk_dicts, embedding_tuples = create_structures(chunks, embedded_chunks, chunk_metadata)
    index = init_pinecone(len(embedded_chunks[0]))
    index.upsert(embedding_tuples)
    host = st.secrets["db_url"]
    user = st.secrets["db_user"]
    password = st.secrets["db_password"]
    db_name = st.secrets["db_name"]
    password_cleaned_host = "postgresql://" + user + ":%s@" + host + "/" + db_name
    url = password_cleaned_host % quote_plus(password)
    engine = sqlalchemy.create_engine(url)
    conn = engine.connect()
    for c in chunk_dicts:
        query = f'INSERT INTO public.node_dictionary (id, distributor, node_text, embedding) ' \
                f'VALUES  (%s, %s, %s, %s)'
        result = conn.execute(query, (c["id"], c["distributor"], c["node_text"], c["embedding"]))

    return index

def build_dict():
    host = st.secrets["db_url"]
    user = st.secrets["db_user"]
    password = st.secrets["db_password"]
    db_name = st.secrets["db_name"]
    password_cleaned_host = "postgresql://" + user + ":%s@" + host + "/" + db_name
    url = password_cleaned_host % quote_plus(password)
    engine = sqlalchemy.create_engine(url)
    conn = engine.connect()
    query = f'select * from public.node_dictionary'
    result = conn.execute(query).all()
    dicts = [r._asdict() for r in result]
    node_dict = {}
    for d in dicts:
        node_dict[str(d["id"])] = d["node_text"]
    with open("./node_dictionary.json", "wb") as wr:
        pickle.dump(node_dict, wr)
    wr.close()
    with open("./node_dictionary_str.json", "w") as wr:
        wr.write(json.dumps(node_dict))
    wr.close()

def reinit_pinecone():
    host = st.secrets["db_url"]
    user = st.secrets["db_user"]
    password = st.secrets["db_password"]
    db_name = st.secrets["db_name"]
    password_cleaned_host = "postgresql://" + user + ":%s@" + host + "/" + db_name
    url = password_cleaned_host % quote_plus(password)
    engine = sqlalchemy.create_engine(url)
    conn = engine.connect()
    query = f'select * from public.node_dictionary'
    result = conn.execute(query).all()
    dicts = [r._asdict() for r in result]
    embedding_tuples = []
    for d in dicts:
        embedding_tuples.append((str(d["id"]), json.loads(d["embedding"]), {"distributor": d["distributor"]}))
    pinecone.init(
        api_key=st.secrets["pinecone"]
    )
    index = pinecone.Index('tess')
    index.delete(deleteAll=True)
    index.upsert(embedding_tuples)

def main():
    # for f in os.listdir('./data'):
    #     add_document(f)
    # add_document("MHFAE.txt")
    # add_document("MRSL.txt", context=f'The following is an exert from a document outlining key facts for a life insurance product from the distributor MRSL:\n')
    # build_dict()
    reinit_pinecone()


if __name__ == '__main__':
    main()