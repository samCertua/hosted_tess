import streamlit as st
from streamlit_chat import message
import requests
import os
import openai
import uuid
from advisors import Advisor, AdvisorCritic, AdvisorFewShot, FinancialGoalsAdvisor, FinancialGoalsAdvisorCritic
from threading import Thread
from multiprocessing import Queue
from logging_util import logging_thread

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]
openai.api_key = st.secrets["openai"]

st.header("Financial goals Tess")

if 'session_id' not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'profile' not in st.session_state:
    st.session_state["profile"] = "a 40 year old man living in the United Kingdom. He earns £60,000 a year and has a " \
                                  "mortgage that costs £2000 a month. He spends £800 a month on groceries and £1100 a month on eating out/takeaway. " \
                                  "He spends £80 a month on petrol, £400 a year on car insurance and £60 a month on public transport. He also spends " \
                                  "£2000 a year on health insurance. Other expenses include gambling and the gym. His average monthly expenditure " \
                                  "is £300 less than income. He has £10000 in savings."

if "logging_queue" not in st.session_state:
    st.session_state["logging_queue"] = Queue()
    logging_worker = Thread(target=logging_thread, args = (st.session_state["logging_queue"],))
    logging_worker.start()

if 'advisor' not in st.session_state:
    st.session_state["advisor"] = FinancialGoalsAdvisor(st.session_state["profile"], st.session_state["logging_queue"])

context = st.expander(label="Settings")
chat = st.container()


def update_profile():
    st.session_state["profile"] = st.session_state["profile_area"]
    update_advisor()

def update_advisor():
    st.session_state['generated'] = []
    st.session_state['past'] = []
    if st.session_state["advisor_model"] == "Standard":
        st.session_state['advisor'] = FinancialGoalsAdvisor(st.session_state["profile"],st.session_state["logging_queue"])
    else:
        st.session_state['advisor'] = FinancialGoalsAdvisorCritic(st.session_state["profile"],st.session_state["logging_queue"])

c_input = context.text_area("User profile", value=st.session_state["profile"], max_chars=2048,
                            on_change=update_profile, key="profile_area")
model_selector = context.selectbox("Advisor model", ["With critic", "Standard"], on_change=update_advisor, key="advisor_model")




with chat:
    # message("Context (what the bot is being told): ")
    # message(gen_context())
    m = "Hi, I'm your new financial advisor. I'm here to help you achieve your financial goals. " \
        "Based on your financial profile, some suggested goals are: "+\
        st.session_state["advisor"].suggested_goals+" What can I help you with?"
    message(m, avatar_style="initials", seed="Tess")


def advisor_conversation(query):
    return st.session_state["advisor"].get_response(query, st.session_state["profile"], st.session_state["session_id"])


def query(payload):
    response = requests.post("http://localhost:8501/", json=payload)
    return response.json()


def get_text():
    input_text = st.text_input("You: ", key="input", )
    return input_text


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
        output = advisor_conversation(user_input)
        with chat:
            message(output, key="temp_output", avatar_style="initials", seed="Tess")
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)

# if user_input:
#     output = advisor_conversation(user_input)
#
#     st.session_state.past.append(user_input)
#     st.session_state.generated.append(output)

# if st.session_state['generated']:
#     for i in range(len(st.session_state['generated'])):
#         with chat:
#             message(st.session_state['past'][i], is_user=True, key=str(i) + '_user', avatar_style="initials", seed="Certua")
#             message(st.session_state["generated"][i], key=str(i), avatar_style="initials", seed="Tess")
