import os
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from Utilities.config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME, variables
from langsmith import Client

# Initialize LangSmith client
langsmith_client = Client()

os.environ['PINECONE_API_KEY'] = PINECONE_API_KEY

llm_max = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
    callbacks=[langsmith_client.get_callback_handler()]  # Add LangSmith callback
)

llm_mini_stream = ChatOpenAI(
    model="gpt-4o-mini",
    streaming=True,
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
    callbacks=[langsmith_client.get_callback_handler()]  # Add LangSmith callback
)

llm_mini = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    openai_api_key=OPENAI_API_KEY,
    callbacks=[langsmith_client.get_callback_handler()]  # Add LangSmith callback
)

def create_retriever(namespace):
    embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY, model="text-embedding-3-large")
    vectorstore = PineconeVectorStore.from_existing_index(index_name=PINECONE_INDEX_NAME, embedding=embeddings, namespace=namespace)
    retriever = vectorstore.as_retriever(search_kwargs={"k": variables["numberOfKwargs"]})
    return retriever

# LangSmith tracing function
def trace_langchain_program(func):
    def wrapper(*args, **kwargs):
        with langsmith_client.trace(
            project_name="TebTech_Manageable",
            tags=["production"],
        ) as tracer:
            result = func(*args, **kwargs)
        return result
    return wrapper