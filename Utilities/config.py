from Utilities.credentials import get_secret, get_configs

variables = get_configs()

OPENAI_API_KEY = get_secret("openai_api_key")
PINECONE_API_KEY = get_secret("pinecone_api_key")
PINECONE_ENVIRONMENT = get_secret("pinecone_environment")
PINECONE_INDEX_NAME = get_secret("pinecone_index_name")