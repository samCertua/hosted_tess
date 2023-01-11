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


def lang_chain_documents():
    doc_paths = os.listdir('scratch/data')
    texts = []
    for d in doc_paths:
        with open(f'scratch/data/{d}/{d}.txt', encoding="utf-8") as f:
            text = f'The following is a document from the company {d}:\n'+ f.read()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts.extend(text_splitter.split_text(text))
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    chain = load_qa_chain(OpenAI(temperature=0), chain_type="map_reduce")
    i = input()
    while i != "Exit":
        docs = docsearch.similarity_search(i)
        chain({"input_documents": docs, "question": i}, return_only_outputs=True)
        i = input()
    pass

def lang_chain_documents_vector_db():
    doc_paths = os.listdir('scratch/data')
    texts = []
    for d in doc_paths:
        with open(f'scratch/data/{d}/{d}.txt', encoding="utf-8") as f:
            text = f'The following is a document from the company {d}:\n'+ f.read()
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        texts.extend(text_splitter.split_text(text))
    embeddings = OpenAIEmbeddings()
    docsearch = FAISS.from_texts(texts, embeddings)
    qa = VectorDBQA.from_llm(llm=OpenAI(), vectorstore=docsearch)
    i = input()
    while i != "Exit":
        qa.run(i)
        i = input()
    pass

def gen_context():
    return "You are talking to a 40 year old man living in the united kingdom. He earns £60,000 a year and has a" \
           "mortgage that costs £2000 a month. He spends £800 a month on groceries and £1100 a month on eating out/takeaway." \
           "He spends £80 a month on petrol, £400 a year on car insurance and £60 a month on public transport. He also spends" \
           "£2000 a year on health insurance. Other expenses include gambling and the gym. He is looking for financial advice" \
           "to secure his and his families' future. Answer the following questions as a financial advisor:\n" \
           "{history}\n" \
           "Q:{human_input}\n" \
           "A:"
def chain(context: str):
    prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=context,
    )
    chat_chain = LLMChain(
        llm=OpenAI(temperature=0),
        prompt=prompt,
        # verbose=True,
        memory=ConversationalBufferWindowMemory(k=2),
    )
    i = input()
    while i !="Exit":
        print(chat_chain.predict(human_input=i))
        i = input()

def single_doc():
    documents = SimpleDirectoryReader('scratch/data/bequest').load_data()
    index = GPTSimpleVectorIndex(documents)
    index.save_to_disk('policy_docs_vector.json')
    new_index = GPTSimpleVectorIndex.load_from_disk('policy_docs_vector.json')
    i = input()
    while i != "Exit":
        print(new_index.query(i).response)
        i = input()
    pass

def multi_doc():
    doc_paths = os.listdir('scratch/data')
    docs = []
    for d in doc_paths:
        nodes = SimpleDirectoryReader('scratch/data/'+d).load_data()
        index = GPTSimpleVectorIndex(nodes)
        # index.set_text(f'The following is a document for insurance distributor {d}, summarised by the following:\n'+
        #     index.query(
        #     "What is a summary of this document?",
        #     response_mode="tree_summarize"
        # ).response)
        index.set_text(f'The following is a document for insurance distributor {d}.\n')
        docs.append(index)
    top_index = GPTSimpleVectorIndex(docs)
    top_index.set_text("The following are policy documents from different insurance distributors. Answer the questions using only information found in the documents.")
    top_index.save_to_disk('policy_docs_vector.json')
    new_index = GPTSimpleVectorIndex.load_from_disk('policy_docs_vector.json')
    # print(new_index.query("What are the cancellation terms?", mode="recursive").response)
    query_configs = [
        {
            "index_struct_type": "simple_dict",
            "query_mode": "retrieve",
            "query_kwargs": {}
        },
        {
            "index_struct_type": "simple_dict",
            "query_mode": "default",
            "query_kwargs": {}
        }
    ]
    i = input()
    while i != "Exit":
        print(new_index.query(i, mode="recursive", query_configs=query_configs).response)
        i = input()
    pass

if __name__ == '__main__':
    # chain(gen_context())
    multi_doc()
    # single_doc()
    # lang_chain_documents()