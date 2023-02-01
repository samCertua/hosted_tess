from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

session = {"counter": 0}

@app.get("/increment")
def read_root():
    session["counter"]+=1
    return session["counter"]

# pinecone.init(
#         api_key=os.environ["PINECONE"]
#     )
# print(pinecone.Index('tess').describe_index_stats())
# index = pinecone.Index('tess')
#
# logging_queue = Queue()
# logging_worker = Thread(target=logging_thread, args=(logging_queue,))
# logging_worker.start()
#
# if not os.path.exists("./node_dictionary.json"):
#     build_dict()
# with open('node_dictionary.json', 'rb') as fp:
#     node_dictionary = pickle.load(fp)


class Message(BaseModel):
    distributor: str
    message: str


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}




# @app.post("/message")
# def message(message: Message):
#     output = ask_tess(logging_queue, session["session_id"], message.message,
#                       index,  node_dictionary,
#                       session["past"], session["generated"], PROMPT,
#                       message.distributor)
#     response = Response(output)
#     Response.se
#     session["past"].append(message.message)
#     session["generated"].append(output)
#     session.modified = True
#     return output