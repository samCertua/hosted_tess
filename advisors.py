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
from logging_util import log_interaction
from urllib.parse import quote_plus
from multiprocessing import Queue


class Advisor:

    def __init__(self, profile, logging_queue: Queue):
        self.prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=self.gen_context(profile),
        )
        self.chain = LLMChain(
            llm=OpenAI(temperature=0.2),
            prompt=self.prompt,
            verbose=True,
            memory=ConversationalBufferWindowMemory(k=2),
        )
        self.logging_queue = logging_queue

    def gen_context(self, profile):
        return "You are an AI expert financial advisor talking to " + profile + \
               "Converse with them in a helpful manner, giving the best financial advice possible using the information " \
               "provided. Do not write questions for them. Do not give specific values, and explain any reasoning:\n" \
               "{history}\n" \
               "Human:{human_input}\n" \
               "AI:"

    def get_response(self, query, profile, session_id):
        resp = self.chain.predict(human_input=query)
        self.logging_queue.put((uuid.uuid4(), session_id, "Advisor",
                                datetime.datetime.now(),
                                self.gen_context(" <profile> "),
                                self.gen_context(profile),
                                query, resp))
        return resp


class AdvisorFewShot:

    def __init__(self, profile, logging_queue: Queue):
        self.prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=self.gen_context(profile),
        )
        self.chain = LLMChain(
            llm=OpenAI(temperature=0.2),
            prompt=self.prompt,
            verbose=True,
            memory=ConversationalBufferWindowMemory(k=2),
        )
        self.logging_queue = logging_queue

    def gen_context(self, profile):
        return "You are an AI expert financial advisor talking to " + profile + \
               "Converse with them in a helpful manner, giving the best financial advice possible using the information " \
               "provided. Do not write questions for them. Do not give specific values, and explain any reasoning. The responses should be in the style of the example conversation:\n" \
               "Example:\n" \
               "Human: How do I think about how much life insurance I need?\n" \
               "AI:  the answer to that question needs to take into account your financial and family profile, " \
               "your goals & objectives, and your time horizon. You have 2 children and a mortgage, " \
               "with some short term credit card debt. Given you can afford it (with excess income after your monthly " \
               "essential spending), " \
               "it might be prudent to buy protection, but this depends on what you want to protect.\n" \
               "{history}\n" \
               "Human:{human_input}\n" \
               "AI:"

    def get_response(self, query, profile, session_id):
        resp = self.chain.predict(human_input=query)
        self.logging_queue.put((uuid.uuid4(), session_id, "Advisor few shot",
                                datetime.datetime.now(),
                                self.gen_context(" <profile> "),
                                self.gen_context(profile),
                                query, resp))
        return resp


class AdvisorCritic:
    def __init__(self, profile, logging_queue: Queue):
        self.initial_prompt = PromptTemplate(
            input_variables=["history", "human_input"],
            template=self.gen_initial_context(profile),
        )
        self.initial_chain = LLMChain(
            llm=OpenAI(temperature=0.2),
            prompt=self.initial_prompt,
            verbose=True,
            memory=ConversationalBufferWindowMemory(k=2),
        )
        self.critic_prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=self.gen_critic_context(),
        )
        self.critic_chain = LLMChain(
            llm=OpenAI(temperature=0.2),
            prompt=self.critic_prompt,
            verbose=True,
            memory=ConversationalBufferWindowMemory(k=2),
        )
        self.prompt = PromptTemplate(
            input_variables=["history", "input"],
            template=self.gen_context(profile),
        )
        self.chain = LLMChain(
            llm=OpenAI(temperature=0.2),
            prompt=self.prompt,
            verbose=True,
            memory=ConversationalBufferWindowMemory(k=2),
        )
        self.logging_queue = logging_queue

    def get_response(self, query, profile, session_id):
        initial_response = self.initial_chain.predict(human_input=query)
        critique = self.critic_chain.predict(input=f'Customer: {query}\nAdvisor: {initial_response}\n')
        response_input = f'Human:{query}\nCritique: {critique}\n'
        resp = self.chain.predict(input=response_input)
        self.logging_queue.put((uuid.uuid4(), session_id, "Advisor with critic",
                                datetime.datetime.now(),
                                self.gen_context(" <profile> ").replace("{input}", response_input),
                                self.gen_context(profile),
                                query, resp))
        return resp

    def gen_initial_context(self, profile):
        return "You are an AI expert financial advisor talking to " + profile + \
               "Converse with them in a helpful manner, giving the best financial advice possible using the information " \
               "provided. Do not write questions for them. Do not give specific values, and explain any reasoning:\n" \
               "{history}\n" \
               "Human:{human_input}\n" \
               "AI:"

    def gen_critic_context(self):
        return "You are training an AI financial advisor. Critique their response to a customer, telling them how they can be more helpful:" \
               "{history}\n" \
               "{input}" \
               "Critique:"

    def gen_context(self, profile):
        return "You are an AI expert financial advisor talking to " + profile + \
               "Converse with them in a helpful manner, giving the best financial advice possible using the information " \
               "provided. Do not write questions for them. Do not give specific values, and explain any reasoning. Also, consider the critique to a previous response given to the human's last statement:\n" \
               "{history}\n" \
               "{input}" \
               "AI:"
