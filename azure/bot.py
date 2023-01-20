# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
import os
from langchain import OpenAI, ConversationChain, PromptTemplate, LLMChain
from langchain.chains.conversation.memory import ConversationalBufferWindowMemory
from langchain import OpenAI, VectorDBQA
from langchain.prompts import PromptTemplate
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount
os.environ['OPENAI_API_KEY'] = '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'

CONTEXT = "You are talking to a 40 year old man living in the united kingdom. He earns £60,000 a year and has a" \
           "mortgage that costs £2000 a month. He spends £800 a month on groceries and £1100 a month on eating out/takeaway." \
           "He spends £80 a month on petrol, £400 a year on car insurance and £60 a month on public transport. He also spends" \
           "£2000 a year on health insurance. Other expenses include gambling and the gym. He is looking for financial advice" \
           "to secure his and his families' future. Answer the following questions as a financial advisor:\n" \
           "{history}\n" \
           "Q:{human_input}\n" \
           "A:"


def advisor_conversation(context: str, query):
    prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=context,
    )
    chat_chain = LLMChain(
        llm=OpenAI(temperature=0.2),
        prompt=prompt,
        # verbose=True,
        memory=ConversationalBufferWindowMemory(k=2),
    )
    return chat_chain.predict(human_input=query)



class MyBot(ActivityHandler):
    # See https://aka.ms/about-bot-activity-message to learn more about the message and other activity types.

    async def on_message_activity(self, turn_context: TurnContext):
        response = advisor_conversation(CONTEXT, turn_context.activity.text)
        await turn_context.send_activity(response)

    async def on_members_added_activity(
        self,
        members_added: ChannelAccount,
        turn_context: TurnContext
    ):
        for member_added in members_added:
            if member_added.id != turn_context.activity.recipient.id:
                print("Hello and welcome! I'm Tess, you're new financial advisor.")
                await turn_context.send_activity("Hello and welcome! I'm Tess, you're new financial advisor.")
