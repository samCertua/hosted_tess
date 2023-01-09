from gpt_index import GPTTreeIndex, SimpleDirectoryReader, GPTSimpleVectorIndex, GPTListIndex, Document
import os
from langchain import OpenAI, ConversationChain, PromptTemplate, LLMChain
from langchain.chains.conversation.memory import ConversationalBufferWindowMemory
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
    # documents = SimpleDirectoryReader('scratch/data').load_data()
    # index = GPTSimpleVectorIndex(documents)
    # index.save_to_disk('policy_docs_vector.json')
    new_index = GPTSimpleVectorIndex.load_from_disk('policy_docs_vector.json')
    print(new_index.query("What are the cancellation terms?").response)
    pass

def multi_doc():
    doc_paths = os.listdir('scratch/data')
    docs = []
    for d in doc_paths:
        nodes = SimpleDirectoryReader('scratch/data/'+d).load_data()
        index = GPTSimpleVectorIndex(nodes)
        index.set_text(f'The following is a document for insurance distributor {d[:4]}, summarised by the following:\n'+
            index.query(
            "What is a summary of this document?",
            response_mode="tree_summarize"
        ).response)
        docs.append(index)
    top_index = GPTListIndex(docs)
    top_index.set_text("The following are policy documents from different insurance distributors. Answer the questions using only information found in the documents.")
    top_index.save_to_disk('policy_docs_vector.json')
    new_index = GPTListIndex.load_from_disk('policy_docs_vector.json')
    # print(new_index.query("What are the cancellation terms?", mode="recursive").response)
    query_configs = [
        {
            "index_struct_type": "list",
            "query_mode": "default",
            "query_kwargs": {}
        },
        {
            "index_struct_type": "weaviate",
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