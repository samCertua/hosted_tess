from gpt_index import GPTTreeIndex, SimpleDirectoryReader
import os
os.environ['OPENAI_API_KEY'] = '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'

def main():
    # documents = SimpleDirectoryReader('scratch/data').load_data()
    # index = GPTTreeIndex(documents)
    # index.save_to_disk('policy_docs.json')
    new_index = GPTTreeIndex.load_from_disk('policy_docs.json')
    print(new_index.query("What are the cancellation terms?"))
    pass

if __name__ == '__main__':
    main()