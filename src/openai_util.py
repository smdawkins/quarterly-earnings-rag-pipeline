from openai import OpenAI
import config.config as config
client = OpenAI(api_key=config.OPENAI_API_KEY)

def generate_comprehensive_answer(query, pinecone_results, api_key):
    """
    Combines retrieved chunks into context and uses an LLM to generate a comprehensive answer.
    
    Args:
        query (str): The user's query.
        retrieved_chunks (dict): Results from the Pinecone query containing retrieved chunks.
        api_key (str): Your OpenAI API key.
    
    Returns:
        str: The comprehensive answer generated by the LLM.
    """
    # Combine the text from each retrieved chunk. You might want to limit the total length.
    context_parts = []
    for match in pinecone_results["matches"]:
        # Assuming the chunk text is stored in metadata under "pinecone_results"
        chunk_text = match["metadata"].get("chunk_text", "")
        context_parts.append(chunk_text)
    context = "\n".join(context_parts)
    
    # Construct the prompt for the LLM
    prompt = (
        "You are an expert financial analyst. Based on the following information from earnings reports:\n\n"
        f"{context}\n\n"
        "Please provide a comprehensive answer to the following question:\n"
        f"{query}"
    )
    
    # Call the OpenAI API
    response = client.responses.create(
        model="gpt-4o-mini",  # Or another model like "gpt-3.5-turbo"
        input=[
            {"role": "system", "content": "You are a knowledgeable financial analyst."},
            {"role": "user", "content": prompt}
        ] # Adjust based on how long you want the answer to be
    )
    
    return response.output_text


