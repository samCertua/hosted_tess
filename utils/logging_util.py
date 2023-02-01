import streamlit as st
import sqlalchemy
from urllib.parse import quote_plus
from multiprocessing import Queue


def log_interaction(id, session_id, service, timestamp, prompt, message, response, session_context):
    host = st.secrets["db_url"]
    user = st.secrets["db_user"]
    password = st.secrets["db_password"]
    db_name = st.secrets["db_name"]
    password_cleaned_host = "postgresql://" + user + ":%s@" + host + "/" + db_name
    url = password_cleaned_host % quote_plus(password)
    engine = sqlalchemy.create_engine(url)
    conn = engine.connect()
    query = f'INSERT INTO public.tess_logging (id, session_id, service, timestamp, prompt, message, response, session_context) ' \
            f'VALUES  (%s, %s, %s, TIMESTAMP %s, %s, %s, %s, %s)'
    result = conn.execute(query, (id, session_id, service, timestamp, prompt, message, response, session_context))


def logging_thread(q: Queue):
    while True:
        print("waiting for events")
        interaction = q.get()
        print("Got event")
        id, session_id, service, timestamp, prompt, message, response, session_context = interaction
        log_interaction(id, session_id, service, timestamp, prompt, message, response, session_context)
