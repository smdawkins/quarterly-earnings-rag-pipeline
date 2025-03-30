# config.py
import os

# Replace these placeholder strings with your actual API keys and configuration.
OPENAI_API_KEY = "your_openai_api_key_here"
PINECONE_API_KEY = "your_pinecone_api_key_here"
PINECONE_ENVIRONMENT = "your_pinecone_environment_here"  # e.g., "us-west1-gcp"
PINECONE_INDEX_NAME = "your-index-name"  # Name of your Pinecone index
SEC_EMAIL_AGENT = "put-in-your-email"

# Folders for storing data locally
DATA_FOLDER = "data"
RAW_FOLDER = os.path.join(DATA_FOLDER, "raw")
CLEAN_FOLDER = os.path.join(DATA_FOLDER, "clean")
PROCESSED_FOLDER = os.path.join(DATA_FOLDER, "processed")
