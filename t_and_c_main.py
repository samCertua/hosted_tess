import os
import streamlit as st
from streamlit_chat import message
import requests
from agents.t_and_c import ask_tess
from utils.document_uploader import build_dict
import pinecone
import pickle
from multiprocessing import Queue
import uuid

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]

# if 'initialised' not in st.session_state:
#     populate_pinecone()
#     st.session_state['initialised'] = True

st.set_page_config(
    page_title="Administrator Tess",
)

st.header("Administrator Tess")

if 'session_id' not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'node_dictionary' not in st.session_state:
    if not os.path.exists("./node_dictionary.json"):
        build_dict()
    with open('node_dictionary.json', 'rb') as fp:
        st.session_state['node_dictionary'] = pickle.load(fp)
    # print(st.session_state['node_dictionary'])

if 'index' not in st.session_state:
    pinecone.init(
        api_key=st.secrets["pinecone"]
    )
    print(pinecone.Index('tess').describe_index_stats())
    st.session_state["index"] = pinecone.Index('tess')

if 'distributors' not in st.session_state:
    st.session_state["distributors"] = os.listdir('./scratch/data')
    print(st.session_state["distributors"])

if "logging_queue" not in st.session_state:
    st.session_state["logging_queue"] = Queue()
    # logging_worker = Thread(target=logging_thread, args = (st.session_state["logging_queue"],))
    # logging_worker.start()

if "prompt" not in st.session_state:
    st.session_state["prompt"] = "Using only the information found in exerts and their given context, answer the query. If the information is not in the exert, answer that you are unsure, if it is, support you answer with quotes directly from the exert.\n"


def query(payload):
    response = requests.post("http://localhost:8501/", json=payload)
    return response.json()


def get_text():
    input_text = st.text_input("You: ", key="input")
    return input_text

chat = st.container()
with chat:
    message("Hi, I'm Tess. I will answer questions about policy documents for assurity, bequest, golden charter, and money for them.", avatar_style="initials", seed="Tess")


with st.form("form", clear_on_submit=True) as f:
    user_input = get_text()
    submitted = st.form_submit_button("Send")
    if submitted:
        with chat:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="initials",
                        seed="Certua")
                message(st.session_state["generated"][i], key=str(i), avatar_style="initials", seed="Tess")
            message(user_input, is_user=True, key='temp_user', avatar_style="initials", seed="Certua")
        output = ask_tess(st.session_state["logging_queue"], st.session_state["session_id"], user_input, st.session_state.index,
                          st.session_state.node_dictionary, st.session_state.past, st.session_state.generated, st.session_state["prompt"])
        with chat:
            message(output, key="temp_output", avatar_style="initials", seed="Tess")
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

# user_input = get_text()
#
# if user_input:
#     output = ask_tess(user_input)
#
#     st.session_state.past.append(user_input)
#     st.session_state.generated.append(output)

# if st.session_state['generated']:
#     del st.session_state['temp_user']
#     for i in range(len(st.session_state['generated'])):
#         with chat:
#             message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="initials", seed="Certua")
#             message(st.session_state["generated"][i], key=str(i), avatar_style="initials", seed="Tess")
    # with chat:
    #     message(st.session_state["generated"][i], key=str(i), avatar_style="initials", seed="Tess")

