from Utilities.config import PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT
import os
from pinecone import Pinecone

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)

def get_namespaces():
    # Get the specific index
    index = pc.Index(PINECONE_INDEX_NAME)
    
    # Get index stats
    stats = index.describe_index_stats()
    
    # Extract namespaces
    namespaces = list(stats['namespaces'].keys())
    
    return namespaces