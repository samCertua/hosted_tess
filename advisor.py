import streamlit as st
from streamlit_chat import message
import requests
import os
from langchain import LLMChain
from langchain.chains.conversation.memory import ConversationalBufferWindowMemory
from langchain import OpenAI
from langchain.prompts import PromptTemplate
import uuid
import datetime
import sqlalchemy
from urllib.parse import quote_plus

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]


# st.set_page_config(
#     page_title="Tess",
#     page_icon=":robot:"
# )

st.header("Tess - advice")

if 'session_id' not in st.session_state:
    st.session_state["session_id"] = uuid.uuid4()

if 'generated' not in st.session_state:
    st.session_state['generated'] = []

if 'past' not in st.session_state:
    st.session_state['past'] = []

if 'profile' not in st.session_state:
    st.session_state["profile"] = "a 40 year old man living in the United Kingdom. He earns £60,000 a year and has a" \
           "mortgage that costs £2000 a month. He spends £800 a month on groceries and £1100 a month on eating out/takeaway." \
           "He spends £80 a month on petrol, £400 a year on car insurance and £60 a month on public transport. He also spends" \
           "£2000 a year on health insurance. Other expenses include gambling and the gym."


def gen_context():
    return "You are an AI expert financial advisor talking to " +st.session_state["profile"]+\
           "They are looking for financial advice " \
           "to secure them and their families' future. Respond to the human as an expert financial advisor," \
           " don't write inputs for them, use the information provided about them, and explain " \
           "your reasoning/calculations:\n" \
           "{history}\n" \
           "Human:{human_input}\n" \
           "AI:"


prompt = PromptTemplate(
    input_variables=["history", "human_input"],
    template=gen_context(),
)

if "chain" not in st.session_state:
    st.session_state["chain"] = chat_chain = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=prompt,
        verbose=True,
        memory=ConversationalBufferWindowMemory(k=2),
    )

context = st.expander(label="User profile")
chat = st.container()


def update_profile():
    st.session_state["profile"] = st.session_state["profile_area"]
    st.session_state['generated'] = []
    st.session_state['past'] = []
    prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=gen_context(),
    )
    st.session_state["chain"] = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=prompt,
        verbose=True,
        memory=ConversationalBufferWindowMemory(k=2),
    )


c_input = context.text_area("Describe a user", value = st.session_state["profile"],max_chars=2048, on_change=update_profile, key="profile_area")

def log_interaction(id, session_id, service, timestamp, context, message, response):
    host = st.secrets["db_url"]
    user = st.secrets["db_user"]
    password = st.secrets["db_password"]
    db_name = st.secrets["db_name"]
    password_cleaned_host = "postgresql://" + user + ":%s@" + host + "/" + db_name
    url = password_cleaned_host % quote_plus(password)
    engine = sqlalchemy.create_engine(url)
    conn = engine.connect()
    query = f'INSERT INTO playground.tess_logging (id, session_id, service, timestamp, context, message, response) ' \
            f'VALUES  (%s, %s, %s, TIMESTAMP %s, %s, %s, %s)'
    result = conn.execute(query, (id, session_id, service, timestamp, context, message, response))

with chat:
    # message("Context (what the bot is being told): ")
    # message(gen_context())
    message("Hi, I'm your new financial advisor. How can I help you")


def advisor_conversation(query):
    return st.session_state["chain"].predict(human_input=query)

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
        output = advisor_conversation(user_input)
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output)
        log_interaction(id=uuid.uuid4(), session_id=st.session_state["session_id"], service="Advisor",
            timestamp=datetime.datetime.now(), context=gen_context(), message=user_input, response=output)

# if user_input:
#     output = advisor_conversation(user_input)
#
#     st.session_state.past.append(user_input)
#     st.session_state.generated.append(output)

if st.session_state['generated']:
    for i in range(len(st.session_state['generated'])):
        with chat:
            message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))




