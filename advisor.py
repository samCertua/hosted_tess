from gpt_index import GPTTreeIndex, SimpleDirectoryReader, GPTSimpleVectorIndex, GPTListIndex, Document
import os
from langchain import OpenAI, ConversationChain, PromptTemplate, LLMChain
from langchain.chains.conversation.memory import ConversationalBufferWindowMemory
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain import OpenAI, VectorDBQA
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain

os.environ['OPENAI_API_KEY'] = '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'


def gen_context():
    return "You are talking to a 40 year old man living in the united kingdom. He earns £60,000 a year and has a" \
           "mortgage that costs £2000 a month. He spends £800 a month on groceries and £1100 a month on eating out/takeaway." \
           "He spends £80 a month on petrol, £400 a year on car insurance and £60 a month on public transport. He also spends" \
           "£2000 a year on health insurance. Other expenses include gambling and the gym. He is looking for financial advice" \
           "to secure his and his families' future. Answer the following questions as a financial advisor:\n" \
           "{history}\n" \
           "Q:{human_input}\n" \
           "A:"

prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=gen_context(),
    )

chat_chain = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=prompt,
        # verbose=True,
        memory=ConversationalBufferWindowMemory(k=2),
    )

def advisor_conversation(context: str, query):
    return chat_chain.predict(human_input=query)

