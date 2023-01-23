import pyarrow.lib
import os
import streamlit as st
from streamlit_chat import message
import requests
from t_and_c import ask_tess, populate_pinecone
import pinecone
import pickle

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]

# if 'initialised' not in st.session_state:
#     populate_pinecone()
#     st.session_state['initialised'] = True

st.set_page_config(
    page_title="Tess",
)

st.header("Tess")

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'chunks_dict' not in st.session_state:
    with open('scratch/chunk_dictionary.json', 'rb') as fp:
        st.session_state['chunks_dict'] = pickle.load(fp)
    # print(st.session_state['chunks_dict'])

if 'index' not in st.session_state:
    pinecone.init(
        api_key=st.secrets["pinecone"]
    )
    print(pinecone.Index('openai').describe_index_stats())
    st.session_state["index"] = pinecone.Index('openai')

if 'distributors' not in st.session_state:
    st.session_state["distributors"] = os.listdir('./scratch/data')
    print(st.session_state["distributors"])

if 'selected_distributor' not in st.session_state:
    st.session_state["selected_distributor"] = 'Assurity'

if 'sum_assured' not in st.session_state:
    st.session_state["sum_assured"] = '£150,000'

if 'start_date' not in st.session_state:
    st.session_state["start_date"] = '20/02/2023'

if 'end_date' not in st.session_state:
    st.session_state["end_date"] = '19/02/2065'

if 'policy_term' not in st.session_state:
    st.session_state["policy_term"] = '42 years'

if 'monthly_premium' not in st.session_state:
    st.session_state["monthly_premium"] = '£100'

def query(payload):
    response = requests.post("http://localhost:8501/", json=payload)
    return response.json()


def get_text():
    input_text = st.text_input("You: ", key="input")
    return input_text

def update_policy_info():
    st.session_state["sum_assured"] = st.session_state["sum_assured_box"]
    st.session_state["start_date"] = st.session_state["start_date_box"]
    st.session_state["end_date"] = st.session_state["end_date_box"]
    st.session_state["policy_term"] = st.session_state["policy_term_box"]
    st.session_state["monthly_premium"] = st.session_state["monthly_premium_box"]
    st.session_state['generated'] = []
    st.session_state['past'] = []

def update_selected_distributor():
    st.session_state["selected_distributor"] = st.session_state["select_distributor"]
    st.session_state['generated'] = []
    st.session_state['past'] = []

options = st.expander("Options")

model_selector = options.selectbox("Distributor", st.session_state["distributors"], on_change=update_selected_distributor, key="select_distributor")
sum_assured_box = options.text_input("Sum assured", value=st.session_state["sum_assured"], key="sum_assured_box", on_change=update_policy_info)
start_date_box = options.text_input("Start date", value=st.session_state["start_date"], key="start_date_box", on_change=update_policy_info)
end_date_box = options.text_input("End date", value=st.session_state["end_date"], key="end_date_box", on_change=update_policy_info)
policy_term_box = options.text_input("Policy term", value=st.session_state["policy_term"], key="policy_term_box", on_change=update_policy_info)
monthly_premium_box = options.text_input("Monthly premium", value=st.session_state["monthly_premium"], key="monthly_premium_box", on_change=update_policy_info)

chat = st.container()
with chat:
    message("Hi, I'm Tess. I will answer questions about your policy terms and conditions.")


with st.form("form", clear_on_submit=True) as f:
    user_input = get_text()
    submitted = st.form_submit_button("Send")
    if submitted:
        user_info = f'You are talking to a life insurance policy holder. The policy details are as follows:\n' \
                    f'Sum assured: {st.session_state["sum_assured"]}\n' \
                    f'Start date: {st.session_state["start_date"]}\n' \
                    f'End date: {st.session_state["end_date"]}\n' \
                    f'Policy term: {st.session_state["policy_term"]}\n' \
                    f'Monthly premium: {st.session_state["monthly_premium"]}\n'
        output = ask_tess(user_input, st.session_state.index, st.session_state.distributors, st.session_state.chunks_dict,
                          st.session_state.past, st.session_state.generated,
                          st.session_state.select_distributor, user_info)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

# user_input = get_text()
#
# if user_input:
#     output = ask_tess(user_input)
#
#     st.session_state.past.append(user_input)
#     st.session_state.generated.append(output)

if st.session_state['generated']:

    for i in range(len(st.session_state['generated'])):
        with chat:
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))

