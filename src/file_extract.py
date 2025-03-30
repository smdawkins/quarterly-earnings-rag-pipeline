import config.config as config
import requests
#Place to pull data files later used for LLM
#Can be used locally but also for upload to cloud
headers = {
    #TODO: find better place to store this
    "User-Agent": config.SEC_EMAIL_AGENT
}

def download_document(url, filename):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        filing_text = response.content
        with open(filename, "wb") as f:
            f.write(filing_text)
        print(f"Downloaded {filename}")
        print("Filing text downloaded successfully.")
    else:
        print("Error downloading filing text.")
        filing_text = ""



def get_sec_filings_by_company(cik):


# Construct the URL to fetch the submissions JSON for JPMorgan Chase
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print("Failed to fetch data from SEC EDGAR.")
        exit()

    data = response.json()

    # The JSON contains a 'filings' section with a 'recent' key holding lists of filing data.
    recent_filings = data.get("filings", {}).get("recent", {})

    forms = recent_filings.get("form", [])
    filing_dates = recent_filings.get("filingDate", [])
    accession_numbers = recent_filings.get("accessionNumber", [])
    primary_document = recent_filings.get("primaryDocument")

    earnings_reports = []
    report_names = []

    # For constructing URLs, the SEC directory uses the numeric CIK (without leading zeros).
    cik_int = str(int(cik))

    # Filter for earnings-related filings (10-K and 10-Q) UPDATE: Removed 10-K as I'm only interested in the most recent quarterly
    for form, filing_date, accession in zip(forms, filing_dates, accession_numbers):
        if form in ["10-Q"]:
            # Remove dashes from the accession number for the URL path
            acc_no_no_dashes = accession.replace("-", "")
            # Construct the URL to the filing text file (this can be modified to point to HTML/XBRL as needed)
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik_int}/{acc_no_no_dashes}/{accession}.txt"
            earnings_reports.append({
                "form": form,
                "filing_date": filing_date,
                "accession_number": accession,
                "filing_url": filing_url
            })
            #report_names.append(f'{cik_int}-{filing_date}-{accession}.txt')

    # Print the latest earnings reports

    return earnings_reports    
    