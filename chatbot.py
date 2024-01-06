from langchain.chains import ConversationalRetrievalChain
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import LlamaCpp
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.memory import ConversationBufferMemory
from langchain.document_loaders import PyPDFLoader
from langchain.document_loaders import TextLoader
from langchain.llms import Ollama
import pickle
import subprocess
import platform
import os
import tempfile
import uuid


class Chat:
    MAX_MESSAGES = 15
    EMBEDDINGS_FILE = "embeddings.pkl"
    def __init__(self):
        self.chat_id = str(uuid.uuid4())
        self.history = []
        self.chain = None
        self.message_count = 0

    def __del__(self):
        print(f"Object {self.chat_id} destroyed")

    def create_embeddings(chunks, embedding_model, storing_path="vectorstore"):
        vectorstore = FAISS.from_documents(chunks, embedding_model)
        vectorstore.save_local(storing_path)
        return vectorstore

    def conversation_chat(self, query):
        try:
            result = self.chain({"question": query, "chat_history": self.history})
            self.history.append((query, result["answer"]))
            self.message_count += 1
            return result["answer"]
        except:
            return "Error 500: Failed to Initialize the model due to system constraints"

    def create_conversational_chain(self, vector_store):
        try:
            llm = Ollama(model="mistral", temperature=0.5)
        except Exception as e:
            try:
                system_platform = platform.system()

                if system_platform == "Linux" or system_platform == "Darwin":
                    subprocess.run(["ollama", "pull", "mistral"], check=True)
                elif system_platform == "Windows":
                    subprocess.run(["ollama.bat", "pull", "mistral"], check=True)
                else:
                    print("Unsupported operating system.")
                    return
            except Exception as e:
                print(f"Error installing Mistral model: {e}")

        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

        self.chain = ConversationalRetrievalChain.from_llm(llm=llm, chain_type='stuff',
                                                           retriever=vector_store.as_retriever(search_kwargs={"k": 2}),
                                                           memory=memory)


    def create_chat(self, file_path):
        text_chunks_file_path = 'text_chunks.pkl'
        if os.path.exists(text_chunks_file_path):
            with open(text_chunks_file_path, 'rb') as text_chunks_file:
                text_chunks = pickle.load(text_chunks_file)
        else:
            text = []
            with open(file_path, 'rb') as file:
                file_extension = os.path.splitext(file.name)[1]

                loader = None
                if file_extension == ".pdf":
                    loader = PyPDFLoader(file_path)
                elif file_extension == ".txt":
                    loader = TextLoader(file_path)

                if loader:
                    text.extend(loader.load())


            text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
            text_chunks = text_splitter.split_documents(text)

            with open(text_chunks_file_path, 'wb') as text_chunks_file:
                pickle.dump(text_chunks, text_chunks_file)

        embeddings_file_path = 'embeddings.pkl'
        if os.path.exists(embeddings_file_path):
            with open(embeddings_file_path, 'rb') as embeddings_file:
                embeddings = pickle.load(embeddings_file)
        else:
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                            model_kwargs={'device': 'cpu'})
            with open(embeddings_file_path, 'wb') as embeddings_file:
                pickle.dump(embeddings, embeddings_file)
        vector_store_file = "vector_store"
        if os.path.exists(vector_store_file):
            vector_store = FAISS.load_local(vector_store_file, embeddings=embeddings)
        else:
            vector_store = FAISS.from_documents(text_chunks, embedding=embeddings)
            vector_store.save_local(vector_store_file)

        self.create_conversational_chain(vector_store)

    def rename_chat(self, new_chat_id):
        self.chat_id = new_chat_id

    def save_chat_history(self):
        if self.message_count >= self.MAX_MESSAGES:
            self.delete_chat()
            print("Chat deleted after reaching the maximum number of messages.")
            exit()
        else:
            # I will implement chat saving logic here, will prolly back it all up into a database
            print(f"Chat {self.chat_id} history saved!")


def main():
    chat = Chat()
    chat.create_chat(file_path='data/medquad.txt')
    
    while True:
        user_input = input("You: ")
        if not user_input or user_input=="exit":
            break  

        output = chat.conversation_chat(user_input)

        print(f"Bot: {output}")


if __name__ == "__main__":
    main()