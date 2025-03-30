from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import json
import time
import config.config as config

# 1. Initialize Pinecone with your API key and environment
my_api_key = config.PINECONE_API_KEY
#index_name = "earnings-report-index"

def create_index(index_name):
    # Set the index name and embedding dimension (e.g., 384 for all-MiniLM-L6-v2)
    pc = Pinecone(api_key=my_api_key)
    embedding_dimension = 384

    # 2. Create the index if it doesn't exist
    if index_name not in pc.list_indexes():
        pc.create_index(index_name, dimension=embedding_dimension, 
                        metric="cosine", 
                        spec=ServerlessSpec(
                        cloud="aws",
                        region=config.PINECONE_ENVIRONMENT
                    ) )
        print(f"Index '{index_name}' created.")
    else:
        print(f"Index '{index_name}' already exists.")

def upsert_to_vector(index_name, filepath):
    # Connect to the index
    pc = Pinecone(api_key=my_api_key)
    index = pc.Index(index_name)

    # Wait for the index to be ready
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)
    print(f"Index: {index_name} up and ready")
    # 3. Read your embeddings from a JSON Lines file and upsert them
    # Each line in the file should be a JSON object with keys: "chunk_index", "chunk_text", "embedding"
    input_file = filepath
    vectors = []

    print('creating json file')
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            record = json.loads(line)
            # Use the chunk index as a string ID; you can adjust if you have a different identifier.
            vector_id = str(record["chunk_index"])
            vector = record["embedding"]
            # Optionally, attach metadata such as the chunk text for later retrieval
            metadata = {"chunk_text": record["chunk_text"]}
            vectors.append((vector_id, vector, metadata))
    print('json created. starting batches')
    # Upsert in batches to avoid memory issues (batch size can be adjusted)
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)
        print(f"Upserted batch {i // batch_size + 1} of {((len(vectors) - 1) // batch_size) + 1}")

    print("All embeddings upserted to Pinecone.")

def check_index(index_name):
    pc = Pinecone(api_key=my_api_key)
    index = pc.Index(index_name)
    print(index.describe_index_stats())

def query_index(index_name, query):
    pc = Pinecone(api_key=my_api_key)
    index = pc.Index(index_name)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    # Wait for the index to be ready
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)
    print(f"Index: {index_name} up and ready")

    query_embedding = model.encode([query])[0].tolist()

    # Now query your Pinecone index with the local embedding
    results = index.query(vector=query_embedding, top_k=3, include_values=False, include_metadata=True)
    #print(results)

    return results
