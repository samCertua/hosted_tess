import datetime
from fastapi import FastAPI, Cookie, Response
from pydantic import BaseModel, BaseSettings
import os
from agents.t_and_c import ask_tess
from utils.document_uploader import build_dict
import pinecone
import pickle
import uuid
from multiprocessing import Queue
from utils.garbage_collection import garbage_collection
import openai
from typing import Optional
from threading import Thread


class Settings(BaseSettings):
    openai_key: str
    pinecone_key: str

settings = Settings()
app = FastAPI()

sessions = {}
garbage_collector = Thread(target=garbage_collection, args=(sessions,))
garbage_collector.start()

openai.api_key = settings.openai_key
PROMPT = "Using only the information found in exerts and their given context, answer the query. If the information is not in the exert, answer that you are unsure, if it is, support you answer with quotes directly from the exert.\n"

pinecone.init(
        api_key=settings.pinecone_key
    )
print(pinecone.Index('tess').describe_index_stats())
index = pinecone.Index('tess')

logging_queue = Queue()
# logging_worker = Thread(target=logging_thread, args=(logging_queue,))
# logging_worker.start()

if not os.path.exists("./node_dictionary.json"):
    build_dict()
with open('node_dictionary.json', 'rb') as fp:
    node_dictionary = pickle.load(fp)


class Message(BaseModel):
    distributor: str
    message: str

@app.post("/message")
def message(message: Message, session_id: Optional[str] = Cookie(None)):
    set_cookie = False
    if not session_id or session_id not in sessions.keys():
        session_id = str(uuid.uuid4())
        sessions[session_id] = {"past": [], "generated": [], "last_active": datetime.datetime.now()}
        set_cookie = True
        print("session_created")
    output = ask_tess(logging_queue, session_id, message.message,
                      index,  node_dictionary,
                      sessions[session_id]["past"], sessions[session_id]["generated"], PROMPT,
                      message.distributor)
    response = Response(output)
    if set_cookie:
        response.set_cookie(key="session_id", value=session_id)
    sessions[session_id]["past"].append(message.message)
    sessions[session_id]["generated"].append(output)
    sessions[session_id]["last_active"] = datetime.datetime.now()
    return response
