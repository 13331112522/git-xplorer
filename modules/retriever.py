import os
import glob
from tqdm import tqdm
from typing import List
from dotenv import load_dotenv
from multiprocessing import Pool
from typing_extensions import Annotated
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter, NLTKTextSplitter
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_nomic.embeddings import NomicEmbeddings
from langchain_community.embeddings import GPT4AllEmbeddings
from langchain_community.embeddings import QianfanEmbeddingsEndpoint


from langchain.chains import RetrievalQA
#from langchain_community.llms import OpenAI
from langchain_openai import OpenAI
import pickle
#from autogen.cache import Cache
from langchain_community.document_loaders import (
    CSVLoader,
    EverNoteLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredEPubLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    UnstructuredODTLoader,
    UnstructuredPowerPointLoader,
    UnstructuredFileLoader,
)
load_dotenv()

source_directory = os.environ.get('SOURCE_DIRECTORY')
embeddings_model_name = os.environ.get('EMBEDDINGS_MODEL_NAME')
chunk_size = os.environ.get('CHUNK_SIZE')
chunk_overlap = os.environ.get('CHUNK_OVERLAP')
folder=os.environ.get('DB')
embeddings = NomicEmbeddings(model=embeddings_model_name)
#embeddings = GPT4AllEmbeddings()
#embeddings = QianfanEmbeddingsEndpoint(
#    qianfan_ak="***",
#    qianfan_sk="***",
#)

LOADER_MAPPING = {
    ".csv": (CSVLoader, {}),
    ".doc": (UnstructuredFileLoader, {}),
    ".docx": (UnstructuredFileLoader, {}),
    ".enex": (EverNoteLoader, {}),
    ".epub": (UnstructuredEPubLoader, {}),
    ".html": (UnstructuredHTMLLoader, {}),
    ".md": (UnstructuredMarkdownLoader, {}),
    ".odt": (UnstructuredODTLoader, {}),
    ".pdf": (PyPDFLoader, {}),
    ".ppt": (UnstructuredPowerPointLoader, {}),
    ".pptx": (UnstructuredPowerPointLoader, {}),
    ".txt": (TextLoader, {"encoding": "utf8"}),
    # Add more mappings for other file extensions and loaders as needed
}

class RETRIEVER():

    def load_single_document(self, file_path: str) -> List[Document]:
#    print("hello")
        ext = "." + file_path.rsplit(".", 1)[-1]
    
        if ext in LOADER_MAPPING:
            loader_class, loader_args = LOADER_MAPPING[ext]
            loader = loader_class(file_path, **loader_args)
        
            return loader.load()

        raise ValueError(f"Unsupported file extension '{ext}'")

    def load_documents(self, source_dir: str, ignored_files: List[str] = []) -> List[Document]:
        """
        Loads all documents from the source documents directory, ignoring specified files
        """
        all_files = []
        for ext in LOADER_MAPPING:
            all_files.extend(
                glob.glob(os.path.join(source_dir, f"**/*{ext}"), recursive=True)
           )
        filtered_files = [file_path for file_path in all_files if file_path not in ignored_files]
    
        with Pool(processes=os.cpu_count()) as pool:
        #with Pool(processes=1) as pool:
            results = []
            with tqdm(total=len(filtered_files), desc='Loading new documents', ncols=80) as pbar:
           
                for j, docs in enumerate(pool.imap_unordered(self.load_single_document, filtered_files)):
                    #print(docs)
                    results.extend(docs)
                    pbar.update()

        return results

    def process_documents(self, ignored_files: List[str] = []) -> List[Document]:
        """
        Load documents and split in chunks
        """
        print(f"Loading documents from {source_directory}")

        documents = self.load_documents(source_directory, ignored_files)
        #documents = load_documents(source_directory)
        if not documents:
            print("No new documents to load")
            exit(0)
        print(f"Loaded {len(documents)} new documents from {source_directory}")

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=int(chunk_size), chunk_overlap=int(chunk_overlap))
        #print(chunk_size, chunk_overlap)
        texts = text_splitter.split_documents(documents)
        print(f"Split into {len(texts)} chunks of text (max. {chunk_size} tokens each)")
        return texts


    def save_db(self, folder):
    
    # Check if the folder already exists
        if not os.path.exists(folder):
            print("Creating new vectorstore")
            # Process the documents and create embeddings
            texts = self.process_documents()
            print(f"Creating embeddings. May take some minutes...")
            # Create the database using the embeddings
            db = FAISS.from_documents(texts, embeddings)
            # Save the database to the specified folder
            db.save_local(folder)
            print(f"Ingestion complete! You can now query your visual documents")


    def retrieve_db(self, question, folder):
        i=2
        j=0
        results=""
        #loading the vectorstore
    
        db=FAISS.load_local(folder, embeddings, allow_dangerous_deserialization = True)
        #with open(f"{folder}/index.pkl", 'rb') as f:
        #    db = pickle.load(f, allow_dangerous_deserialization=True)
    
        retriever = db.as_retriever(search_kwargs={"k": i})
        #qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=True)
        docs = retriever.get_relevant_documents(question)
        #results=RetrievalQA.from_llm(llm=llm, retriever=retriever)
        for j in range(i-1):
            results=results+"/n"+docs[j].page_content
        #print(results)
        #results=qa("evolution of apple")
        #input()
        return results