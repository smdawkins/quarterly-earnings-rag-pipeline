import json
from sentence_transformers import SentenceTransformer

def process_file(filepath, output_file, max_words=300):
    """
    Processes a large text file by reading it line by line, splitting it into chunks of a specified
    number of words (default 300), vectorizing each chunk, and appending the results to an output file.
    
    Args:
        filepath (str): Path to the input text file.
        output_file (str): Path to the output file (JSON Lines format).
        max_words (int): Maximum number of words per chunk (default is 300).
    """
    # Load the SentenceTransformer model (this model can be changed as needed)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    chunk_index = 0
    current_words = []
    
    # Open the input file for reading and the output file in append mode
    with open(filepath, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
        for line in infile:
            # Split the line into words; assumes the file is already cleaned
            words = line.strip().split()
            for word in words:
                current_words.append(word)
                # When we reach the max_words, create a chunk
                if len(current_words) >= max_words:
                    chunk_text = " ".join(current_words)
                    # Generate the embedding for the current chunk (processing one chunk at a time)
                    embedding = model.encode([chunk_text])[0].tolist()
                    # Build the data dictionary for this chunk
                    data = {
                        "chunk_index": chunk_index,
                        "chunk_text": chunk_text,
                        "embedding": embedding
                    }
                    # Append the data as a JSON line
                    outfile.write(json.dumps(data) + "\n")
                    chunk_index += 1
                    current_words = []  # Reset for the next chunk
        
        # Process any remaining words that didn't fill up a complete chunk
        if current_words:
            chunk_text = " ".join(current_words)
            embedding = model.encode([chunk_text])[0].tolist()
            data = {
                "chunk_index": chunk_index,
                "chunk_text": chunk_text,
                "embedding": embedding
            }
            outfile.write(json.dumps(data) + "\n")
            chunk_index += 1
    
    print(f"Processing complete. {chunk_index} chunks written to {output_file}")

# Example usage:
# process_file("cleaned_10q.txt", "embedding_data.jsonl")
