import requests

def get_latest_filing(ticker):
    # SEC API URL for company filings (EDGAR Search API)
    # Filtering for 10-K and 10-Q filings
    url = f"https://data.sec.gov/submissions/CIK{ticker}.json"
    
    headers = {
        'User-Agent': 'your-email@example.com'  # Replace with your email as per SEC API policy
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    
    filings = data.get('filings', {}).get('recent', {})
    form_types = filings.get('form', [])
    filing_dates = filings.get('filingDate', [])
    accession_numbers = filings.get('accessionNumber', [])
    
    # Find the latest 10-K or 10-Q
    for i, form in enumerate(form_types):
        if form in ['10-K', '10-Q']:
            filing_date = filing_dates[i]
            accession_number = accession_numbers[i].replace('-', '')
            # URL to filing documents index
            filing_url = f"https://www.sec.gov/Archives/edgar/data/{data['cik']}/{accession_number}/index.json"
            print(f"Latest Filing Type: {form}")
            print(f"Filing Date: {filing_date}")
            print(f"Filing Documents Index URL: {filing_url}")
            return filing_url

    print("No recent 10-K or 10-Q filings found.")
    return None

if __name__ == "__main__":
    ticker = "0000789019"  # Microsoft CIK (not ticker symbol) — Need CIK number for this API
    # CIK must be 10 digits, zero padded. For example, MSFT's CIK is 789019 -> padded: 0000789019

    filing_url = get_latest_filing(ticker)
