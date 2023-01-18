import sqlalchemy
from urllib.parse import quote_plus


def log_interaction(session_id, id, service, timestamp, context, message, response):
    host = "iqdevdw01.cnnbmbxb8uxc.eu-west-1.rds.amazonaws.com"
    user = "kettle"
    password = "dVlastnik0A4#Sim"
    db_name = "simulation"
    password_cleaned_host = "postgresql://" + user + ":%s@" + host + "/" + db_name
    url = password_cleaned_host % quote_plus(password)
    engine = sqlalchemy.create_engine(url)
    conn = engine.connect()
    query = f'INSERT INTO playground.tess_logging (id, session_id, service, timestamp, context, message, response) ' \
            f'VALUES  ({session_id}, {id}, {service}, {timestamp}, {context}, {message}, {response})'
    result = conn.execute(query)
