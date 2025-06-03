import requests
import folium
from folium.plugins import MarkerCluster
import webbrowser

# --- Constants and configs ---

HIGH_RISK_COUNTRIES = {"North Korea", "Iran", "Syria", "Sudan", "Cuba", "Russia"}
MAX_RAW_SCORE = 100  # Define max raw score to normalize to 100 scale

# --- Helper functions ---

def fetch_sanctions_entities(name):
    """
    Simulated sanctions lookup for entity 'name'.
    In a real project, connect to sanctions API or database.
    Here we return a dummy list with sample data.
    """
    print(f"Fetching sanctions info for '{name}'...")
    # Example dummy response
    return [
        {
            "name": "Microsoft Corporation",
            "sanctioned": False,
            "country": "United States",
            "entity_type": "company"
        },
        {
            "name": "Fake Sanctioned Entity",
            "sanctioned": True,
            "country": "Iran",
            "entity_type": "company"
        }
    ]


def fetch_entities_by_name(name):
    query = f"""
    [out:json][timeout:1800];
    (
      node["name"~"{name}", i];
      node["operator"~"{name}", i];
      node["brand"~"{name}", i];

      way["name"~"{name}", i];
      way["operator"~"{name}", i];
      way["brand"~"{name}", i];

      relation["name"~"{name}", i];
      relation["operator"~"{name}", i];
      relation["brand"~"{name}", i];
    );
    out center;
    """
    print(f"Sending Overpass query for '{name}' entities worldwide...")
    try:
        url = "https://overpass-api.de/api/interpreter"
        response = requests.get(url, params={'data': query}, timeout=180)
        response.raise_for_status()
        data = response.json()
        print(f"✅ Retrieved {len(data['elements'])} elements.")
        return data['elements']
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching data: {e}")
        return []


def create_entity_map(elements, entity_name, map_filename=None):
    if not elements:
        print("No elements to display on map.")
        return

    if not map_filename:
        map_filename = f"{entity_name.replace(' ', '_').lower()}_entities_map.html"

    # Default center: Microsoft HQ
    map_center = [47.6401, -122.1296]  # Redmond, WA
    my_map = folium.Map(location=map_center, zoom_start=2)
    cluster = MarkerCluster().add_to(my_map)

    for el in elements:
        lat = el.get("lat")
        lon = el.get("lon")
        if not lat or not lon:
            center = el.get("center")
            if center:
                lat = center.get("lat")
                lon = center.get("lon")

        if lat and lon:
            name = el.get("tags", {}).get("name", "Facility")
            folium.Marker([lat, lon], popup=name).add_to(cluster)

    my_map.save(map_filename)
    print(f"🗺️ Map saved as: {map_filename}")
    webbrowser.open(map_filename)


def get_latest_sec_filing(cik):
    """
    Fetch latest 10-K or 10-Q filing from SEC EDGAR for the company with given CIK.
    CIK must be zero-padded to 10 digits.
    """
    print(f"Fetching latest SEC filing for CIK {cik}...")
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {
        'User-Agent': 'your-email@example.com'  # Change this to your email as per SEC policy
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        filings = data.get('filings', {}).get('recent', {})
        forms = filings.get('form', [])
        dates = filings.get('filingDate', [])
        accession_numbers = filings.get('accessionNumber', [])

        for i, form in enumerate(forms):
            if form in ['10-K', '10-Q']:
                filing_date = dates[i]
                accession = accession_numbers[i].replace('-', '')
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json"
                return {
                    "form": form,
                    "date": filing_date,
                    "url": filing_url
                }
        print("No recent 10-K or 10-Q filings found.")
        return None
    except Exception as e:
        print(f"Error fetching SEC filing: {e}")
        return None


def score_entity(entity, osm_elements, filing_info=None):
    score = 0
    if entity.get('sanctioned'):
        score += 50

    country = entity.get('country')
    if country and country in HIGH_RISK_COUNTRIES:
        score += 30

    if entity.get('entity_type') == 'company':
        score += 10

    num_facilities = len(osm_elements) if osm_elements else 0
    score += num_facilities

    if filing_info:
        score -= 20

    return max(score, 0)


def normalize_score(raw_score, max_raw=MAX_RAW_SCORE):
    normalized = (raw_score / max_raw) * 100
    return min(round(normalized, 2), 100)


# --- Main pipeline ---

def aml_pipeline(entity_name, cik=None):
    print(f"\n=== Starting AML pipeline for '{entity_name}' ===")

    sanctions_results = fetch_sanctions_entities(entity_name)
    osm_elements = fetch_entities_by_name(entity_name)
    create_entity_map(osm_elements, entity_name)

    filing = None
    if cik:
        filing = get_latest_sec_filing(cik)
        if filing:
            print(f"Latest SEC filing: {filing['form']} on {filing['date']}")
            print(f"Documents URL: {filing['url']}")
        else:
            print("No filings found.")

    print("\nRisk Scoring:")
    for entity in sanctions_results:
        raw_score = score_entity(entity, osm_elements, filing)
        normalized = normalize_score(raw_score)
        print(f"- {entity['name']} Risk Score: {normalized} / 100")

    print(f"=== AML pipeline complete for '{entity_name}' ===\n")


# --- Run example for Microsoft ---

if __name__ == "__main__":
    # Microsoft CIK padded to 10 digits
    MICROSOFT_CIK = "0000789019"
    aml_pipeline("Microsoft", MICROSOFT_CIK)
