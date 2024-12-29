import io
from google.cloud import storage
from datetime import datetime

def upload_to_gcs(content, bucket_name, destination_blob_name):
    """Uploads content directly to the specified Google Cloud Storage bucket."""
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    # Convert string content to bytes
    content_bytes = content.encode('utf-8')

    # Upload from a string buffer
    blob.upload_from_string(content_bytes, content_type='text/markdown')

    print(f"Content uploaded to {destination_blob_name} in bucket {bucket_name}.")

def write_and_upload_markdown_content(content, filename, bucket_name="tebtech_logging_data"):
    """Uploads the given content as a markdown file to Google Cloud Storage.

    Args:
        content: The string content to upload.
        filename: The base filename to save the file as (without extension).
        bucket_name: The name of the GCS bucket to upload to.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    full_filename = f"{filename}_{timestamp}.md"
    
    # Upload to GCS
    upload_to_gcs(content, bucket_name, full_filename)

def write_and_upload_rag_markdown_content(rag_data, filename, bucket_name="tebtech_logging_data"):
    # Check the type and content of rag_data
    if isinstance(rag_data, str):
        print("Unexpected string data:", rag_data)
        return

    # Extract the relevant information from the rag_data
    context = rag_data.get('context', [])
    answer = rag_data.get('answer', 'No answer found')

    # Start creating the markdown content
    markdown_content = "# Extracted Information\n\n"

    # Add the answer to the markdown content
    markdown_content += f"## Answer\n\n{answer}\n\n"

    # Add the context documents to the markdown content
    markdown_content += "## Context Documents\n\n"
    for doc in context:
        page_content = doc.page_content
        metadata = doc.metadata
        file_name = metadata.get('filename', 'Unknown file')
        page_number = metadata.get('page_number', 'Unknown page number')
        
        markdown_content += f"### Document from {file_name} (Page {page_number})\n\n"
        markdown_content += f"{page_content}\n\n"
    
    # Upload the markdown content
    write_and_upload_markdown_content(markdown_content, filename, bucket_name)

def write_and_upload_documents_to_markdown(documents, filename, bucket_name="tebtech_logging_data"):
    """Uploads the given list of documents as a markdown file to Google Cloud Storage.

    Args:
        documents: The list of documents to write to the file. Each document should have 'page_content' and 'metadata' attributes.
        filename: The base filename to save the file as (without extension).
        bucket_name: The name of the GCS bucket to upload to.
    """
    markdown_content = ""
    for doc in documents:
        for key, value in doc.metadata.items():
            markdown_content += f"**{key.capitalize()}:** {value}\n"
        markdown_content += "\n"
        markdown_content += doc.page_content
        markdown_content += "\n\n---\n\n"
    
    write_and_upload_markdown_content(markdown_content, filename, bucket_name)