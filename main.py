from src.file_extract import get_sec_filings_by_company, download_document
from src.normalize_file import clean_file_with_soup
from src.vectorize import process_file
import argparse
import openai
import pinecone
from src.pinecone_util import create_index, upsert_to_vector, check_index, query_index
from src.openai_util import generate_comprehensive_answer
import config.config as config

# Initialize OpenAI and Pinecone with keys from config
openai.api_key = config.OPENAI_API_KEY
index = config.PINECONE_INDEX_NAME

def load_report(cik):
    """
    Downloads the latest 10-K or 10-Q filing for the given CIK from SEC EDGAR.
    Returns the filing's HTML/text content.
    Embeds data into Vectors then uploads it to the index
    """
    earnings_reports = get_sec_filings_by_company(cik)
    print(f"Reports pulled for {cik}:")
    '''for report in earnings_reports:
        print(f"Form: {report['form']}, Filing Date: {report['filing_date']}, Accession: {report['accession_number']}")
        print(f"URL: {report['filing_url']}\n")
        filename = f"{report['form']}-{report['filing_date']}-{report['accession_number']}.txt"
        download_document(report['filing_url'], filename)'''
    #Only want the first report
    report = earnings_reports[0]
    print(f"Form: {report['form']}, Filing Date: {report['filing_date']}, Accession: {report['accession_number']}")
    print(f"URL: {report['filing_url']}\n")
    filename = f"{report['form']}-{report['filing_date']}-{report['accession_number']}.txt"
    download_document(report['filing_url'], f'data/raw/{filename}')


    print(f'Extract text from HTML...')
    clean_file_with_soup(f'data/raw/{filename}', f'data/cleaned/{filename}')

    print(f'Embedding text into vectors...')
    process_file(f'data/cleaned/{filename}', f'data/processed/{filename}')

    create_index(index)

    print(f'Loading vectors into Pinecone')
    upsert_to_vector(index,f'data/processed/{filename}')
    check_index(index)

def query_report(query):
    """
    Encodes the query, retrieves the most relevant chunks from Pinecone,
    builds a prompt using the retrieved context, and queries OpenAI for a comprehensive answer.
    """
    pinecone_retrieval_results = query_index(index, query)
    answer = generate_comprehensive_answer(query, pinecone_retrieval_results, config.OPENAI_API_KEY)
    print("Comprehensive Answer:")
    print(answer)



def main():
    parser = argparse.ArgumentParser(description="Earnings Report Processing Pipeline")
    parser.add_argument("action", choices=["load-report", "query"], help="Action to perform: load-report or query")
    parser.add_argument("value", help="For 'load-report', provide the CIK number; for 'query', provide the query text.")
    args = parser.parse_args()

    if args.action == "load-report":
        load_report(args.value)
    elif args.action == "query":
        query_report(args.value)

if __name__ == "__main__":
    main()