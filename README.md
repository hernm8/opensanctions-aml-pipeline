# OpenSanctions AML Pipeline Project

## Overview

This project implements an AML (Anti-Money Laundering) pipeline that integrates multiple data sources and APIs to perform sanctions screening, entity location mapping, and SEC filing retrieval. It combines data from OpenSanctions, OpenStreetMap (via Overpass API), and the SEC EDGAR API to provide a comprehensive risk assessment for entities such as companies.

## Features

- **Sanctions Data Lookup:** Uses OpenSanctions API to identify sanctioned entities.
- **Entity Location Mapping:** Queries OpenStreetMap data via Overpass API to map entity locations worldwide.
- **SEC Filings Retrieval:** Fetches the latest 10-K and 10-Q filings from the SEC EDGAR database.
- **Risk Scoring:** Combines sanctions status, country risk, entity type, and geographic footprint to compute a risk score.
- **Interactive Maps:** Visualizes entities and facilities using Folium with clustered markers.
- **Pipeline Integration:** Scripts can be run independently or combined in a pipeline to automate the entire process.

## Repository Structure

\\\
opensanctions-aml-pipeline/
│
├── opensanctions.py           # OpenSanctions API integration script
├── kyb_open_sanc.py           # KYB (Know Your Business) and sanctions screening script
├── aml_overpass.py            # Overpass API queries and Folium map generation
├── test_api_opensanc.py       # Testing and example scripts for OpenSanctions API
├── main_pipeline.py           # (Optional) main script to run all components in sequence
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
└── data/                      # Folder for output files (maps, reports, etc.)
\\\

## Usage

1. Clone the repository:

\\\ash
git clone https://github.com/yourusername/opensanctions-aml-pipeline.git
cd opensanctions-aml-pipeline
\\\

2. (Optional) Create and activate a virtual environment:

\\\ash
python -m venv venv
source venv/bin/activate      # Linux/Mac
.\venv\Scripts\activate       # Windows PowerShell
\\\

3. Install dependencies:

\\\ash
pip install -r requirements.txt
\\\

4. Run individual scripts or the full pipeline:

\\\ash
python opensanctions.py
python kyb_open_sanc.py
python aml_overpass.py
python test_api_opensanc.py
\\\

Or run the full pipeline:

\\\ash
python main_pipeline.py
\\\

## Dependencies

- \equests\
- \olium\
- \webbrowser\ (standard library)

## Contributing

Contributions welcome! Please submit pull requests or open issues.

## License

MIT License

---

## Contact

Michael Hernandez  
Email: your-email@example.com  
LinkedIn: https://www.linkedin.com/in/yourprofile/
