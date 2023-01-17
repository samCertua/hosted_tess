import streamlit as st
from streamlit_chat import message
import requests
import os
from langchain import LLMChain
from langchain.chains.conversation.memory import ConversationalBufferWindowMemory
from langchain import OpenAI
from langchain.prompts import PromptTemplate

os.environ['OPENAI_API_KEY'] = st.secrets["openai"]


st.set_page_config(
    page_title="Streamlit Chat - Demo",
    page_icon=":robot:"
)

st.header("Streamlit Chat - Demo")

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
           "They are looking for financial advice" \
           "to secure them and their families' future. Respond to the human as and expert financial advisor, and don't write inputs for them:\n" \
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




