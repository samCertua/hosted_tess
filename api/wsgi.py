from flask import Flask, request, session
import os
from agents.t_and_c import ask_tess
from agents.advice import get_advice, get_suggested_goals
from advisors import FinancialGoalsAdvisor
from document_uploader import build_dict
import pinecone
import pickle
import uuid
from threading import Thread
from multiprocessing import Queue
from logging_util import logging_thread
import openai

openai.api_key = os.environ['OPENAI_API_KEY']
PROMPT = "Using only the information found in exerts and their given context, answer the query. If the information is not in the exert, answer that you are unsure, if it is, support you answer with quotes directly from the exert.\n"


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = 'super secret key'

    pinecone.init(
        api_key=os.environ["PINECONE"]
    )
    print(pinecone.Index('tess').describe_index_stats())
    index = pinecone.Index('tess')

    logging_queue = Queue()
    logging_worker = Thread(target=logging_thread, args=(logging_queue,))
    logging_worker.start()

    if not os.path.exists("./node_dictionary.json"):
        build_dict()
    with open('node_dictionary.json', 'rb') as fp:
        node_dictionary = pickle.load(fp)


    @app.route("/", methods=["GET"])
    def health_check_live():
        if 'session_id' not in session:
            session["session_id"] = uuid.uuid4()

        if 'generated' not in session:
            session['generated'] = []

        if 'past' not in session:
            session['past'] = []

        return "healthy", 200



    @app.route("/faq_message", methods=["POST"])
    def faq_message():
        if 'session_id' not in session:
            session["session_id"] = uuid.uuid4()
        if 'generated' not in session:
            session['generated'] = []
        if 'past' not in session:
            session['past'] = []
        distributor = request.json["distributor"]
        user_message = request.json["message"]
        output = ask_tess(logging_queue, session["session_id"], user_message,
                          index,  node_dictionary,
                          session["past"], session["generated"], PROMPT,
                          distributor)
        session["past"].append(user_message)
        session["generated"].append(output)
        session.modified = True
        return output

    @app.route("/advisor_message", methods=["POST"])
    def advisor_message():
        profile = request.json["profile"]
        if "suggested_goals" not in session:
            if 'session_id' not in session:
                session["session_id"] = uuid.uuid4()
            if 'generated' not in session:
                session['generated'] = []
            if 'past' not in session:
                session['past'] = []
            session["suggested_goals"] = get_suggested_goals(profile)
            session.modified = True
            return session["suggested_goals"]
        else:
            user_message = request.json["message"]
            output = get_advice(user_message, profile, session["session_id"], session["past"], session["generated"],
                                session["suggested_goals"], logging_queue)
            session["past"].append(user_message)
            session["generated"].append(output)
            session.modified = True
            return output



    return app

if __name__ == "__main__":
    # Init Flask App context
    flask_app = create_app()
    flask_app.config["DEBUG"] = False
    print("Created app, running flask")
    flask_app.run(port=1010, host="0.0.0.0", threaded=True)
