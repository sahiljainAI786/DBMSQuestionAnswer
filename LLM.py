
import os

import openai
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceInstructEmbeddings, OpenAIEmbeddings
from langchain.vectorstores import FAISS, Pinecone, Chroma
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.embeddings import  OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import RetrievalQA
from langchain.chains.conversation.memory import ConversationBufferWindowMemory

from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()
open_api_key = os.environ.get('OPENAI_API_KEY')
openai.api_key = open_api_key




# template = """ You are expert in genomics and research related to it. Use the following pieces of context to answer the question at the end.
#                 Answers must be 2056 words long and having in proper format. If the answers contains Steps use numbers format to do that. 
#                 If you don't know the answer, just say that you don't know, don't try to make up an answer.
#                 Always say "thanks for asking!" at the end of the answer.
#                 {context}
#                 Question: {question}
#                 Helpful Answer:"""


# template = """You are expert in generating answers from the context. Your task is to generate a proper answer for the user question.\nPay attention if you do not know the answer or not found the answers from the context just say 'I don't know'.Do not try to make answers from your side.User question : {question}\nContext:{context}  """

template = """You are an expert in Database Mangaement system and a professor in this project. Your task is to give user question answer which is related to 'DBMS' Subject. If the question is not related to DBMS just say "I don't know".Give answers from the given context according to the user question.\nThis is the context:{context}\n\nThis is the question:{question}"""
prompt =  PromptTemplate(
    input_variables=["context", "question"], template=template
)

model_name = "gpt-3.5-turbo-16k"


# ['stuff', 'map_reduce', 'refine', 'map_rerank']



class LLM_ANSWER:
  def __init__(self):
    # embdings =  OpenAIEmbeddings(model="text-embedding-ada-002")
    embdings = SentenceTransformerEmbeddings(model_name="embd2_with_embedderHF-all-mpnet-base-v2/sentence-transformers_all-mpnet-base-v2")
    self.db = Chroma(collection_name = "langchain_store",persist_directory= "DB_For_DBMS",embedding_function=embdings)
    llm = OpenAI(model_name=model_name, temperature=0.1,max_tokens=1024, top_p=0.2)  

    # self.memory = ConversationBufferMemory(memory_key="chat_history",
    #                                        return_messages=False,)

    self.window_memory = ConversationBufferWindowMemory(k=3)

    self.chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
    self.qa  = RetrievalQA(combine_documents_chain=self.chain, 
                           retriever=self.db.as_retriever(search_kwargs={"k":15}),
                           memory=self.window_memory)
    # self.qa = RetrievalQA.from_chain_type(self.llm, chain_type="stuff", retriever=self.db.as_retriever(search_kwargs={"k":3}), chain_type_kwargs={"prompt": prompt})

      

  def preprocess_answer(self, query):
    answer = self.qa(query)


    # template = """You are expert in elaborating the answer and formatting the answers in proper format. Your task is to eloborate the answers according to the user question. 
                
    #             Question: {question}

    #             Answer : {answer}

    #             Helpful Answer:"""
    


    # prompt =  PromptTemplate(
    # input_variables=["answer", "question"], template=template)



    # model_name = "gpt-3.5-turbo-16k"
    # llm_3 = OpenAI(model_name=model_name, temperature=0.9,max_tokens=1024, top_p=0.8)
    # llm_chain_3= LLMChain(llm=llm_3, prompt=prompt)

    # print(llm_chain_3(inputs={"question":query, "answer":answer["result"]}))
    return answer         








  def get_answer(self, query):

    # similar_docs = self.give_keywords(query)
    # answer = self.chain.run(input_documents=similar_docs, question=query)



    # answer_1 = self.qa(query)
    answer_1 = self.preprocess_answer(query)


    result  = answer_1["result"] 

    # answer_2 = self.db.similarity_search(query, k=5)

    # result += "\n\n"+""+f"{answer_2}"

    if "thanks for asking" not in result.lower():
      result = result + " " + "Thanks for asking!"

    return result
