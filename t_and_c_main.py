import pyarrow.lib
import streamlit as st
from streamlit_chat import message
import requests
from t_and_c import ask_tess

st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

st.header("Streamlit Chat - Demo")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

def query(payload):
	response = requests.post("http://localhost:8501/", json=payload)
	return response.json()

def get_text():
    input_text = st.text_input("You: ", key="input")
    return input_text


user_input = get_text()

if user_input:
    output = ask_tess( user_input)

    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])-1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
message("Hi, I'm Tess. I will answer questions about policy documents.")