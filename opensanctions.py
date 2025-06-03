from pprint import pprint
import requests
import json
import csv
from rapidfuzz import fuzz

API_KEY = "your key"
HEADERS = {"Authorization": API_KEY}

def screen_business(name):
    query = {
        "queries": {
            "q1": {
                "schema": "LegalEntity",
                "properties": {"name": [name]}
            }
        }
    }
    response = requests.post("https://api.opensanctions.org/match/default", headers=HEADERS, json=query)
    response.raise_for_status()
    return response.json()["responses"]["q1"]["results"]

def filter_by_similarity(results, target_name, threshold=80):
    filtered = []
    for entity in results:
        raw_name = entity.get("name") or entity.get("properties", {}).get("name", "")
        if isinstance(raw_name, list):
            if any(fuzz.partial_ratio(target_name.lower(), n.lower()) >= threshold for n in raw_name):
                filtered.append(entity)
        else:
            if fuzz.partial_ratio(target_name.lower(), raw_name.lower()) >= threshold:
                filtered.append(entity)
    return filtered

def extract_sanctions(results):
    sanctions_list = []
    for entity in results:
        raw_name = entity.get("name")
        if not raw_name:
            raw_name = entity.get("properties", {}).get("name")

        if isinstance(raw_name, list):
            primary_name = raw_name[0]
            name_aliases_from_name = raw_name[1:]
        else:
            primary_name = raw_name
            name_aliases_from_name = []

        aliases = entity.get("other_names", [])
        alias_names = [alias.get("name") for alias in aliases if alias.get("name")]

        all_aliases = name_aliases_from_name + alias_names

        name = primary_name if primary_name else "N/A"
        aliases_str = "; ".join(all_aliases) if all_aliases else "None"

        country = entity.get("country")
        if not country:
            country = entity.get("properties", {}).get("country", [])
        if isinstance(country, list):
            country = ', '.join(country)
        elif not country:
            country = "N/A"

        sanctions_info = []
        for sanction in entity.get("sanctions", []):
            sanctions_info.append({
                "Authority": sanction.get("authority_name"),
                "Program": sanction.get("program"),
                "Start Date": sanction.get("start_date"),
                "End Date": sanction.get("end_date"),
            })

        entry = {
            "Entity ID": entity.get("id", "N/A"),
            "Name": name,
            "Aliases": aliases_str,
            "Country": country,
            "Sanctioned": entity.get("sanctioned", "N/A"),
            "Sanctions Count": len(entity.get("sanctions", [])),
            "PEP Status": entity.get("pep", "N/A"),
            "Sanctions": sanctions_info if sanctions_info else "None",
            "First Seen": entity.get("first_seen", "N/A"),
            "Last Seen": entity.get("last_seen", "N/A")
        }
        sanctions_list.append(entry)
    return sanctions_list

if __name__ == "__main__":
    business_name = "Microsoft"
    try:
        results = screen_business(business_name)
        
        # Apply fuzzy filtering to narrow results
        filtered_results = filter_by_similarity(results, business_name)
        
        sanctions = extract_sanctions(filtered_results)

        for entry in sanctions:
            print("-" * 40)
            print(f"Entity ID: {entry['Entity ID']}")
            print(f"Name: {entry['Name']}")
            print(f"Aliases: {entry['Aliases']}")
            print(f"Country: {entry['Country']}")
            print(f"Sanctioned: {entry['Sanctioned']}")
            print(f"Sanctions Count: {entry['Sanctions Count']}")
            print(f"PEP Status: {entry['PEP Status']}")
            print("Sanctions:")
            if entry["Sanctions"] == "None":
                print("  None")
            else:
                for s in entry["Sanctions"]:
                    print(f"  Authority: {s['Authority']}")
                    print(f"  Program: {s['Program']}")
                    print(f"  Start Date: {s['Start Date']}")
                    print(f"  End Date: {s['End Date']}")
                    print()
            print(f"First Seen: {entry['First Seen']}")
            print(f"Last Seen: {entry['Last Seen']}")

        # Export to JSON
        with open(f"{business_name}_sanctions.json", "w", encoding="utf-8") as f_json:
            json.dump(sanctions, f_json, indent=2, ensure_ascii=False)

        # Export to CSV
        with open(f"{business_name}_sanctions.csv", "w", encoding="utf-8", newline='') as f_csv:
            writer = csv.writer(f_csv)
            writer.writerow([
                "Entity ID", "Name", "Aliases", "Country",
                "Sanctioned", "Sanctions Count", "PEP Status",
                "Sanction Authority", "Sanction Program", "Start Date", "End Date",
                "First Seen", "Last Seen"
            ])

            for entry in sanctions:
                if entry["Sanctions"] == "None":
                    writer.writerow([
                        entry["Entity ID"], entry["Name"], entry["Aliases"], entry["Country"],
                        entry["Sanctioned"], entry["Sanctions Count"], entry["PEP Status"],
                        "None", "None", "None", "None",
                        entry["First Seen"], entry["Last Seen"]
                    ])
                else:
                    for s in entry["Sanctions"]:
                        writer.writerow([
                            entry["Entity ID"], entry["Name"], entry["Aliases"], entry["Country"],
                            entry["Sanctioned"], entry["Sanctions Count"], entry["PEP Status"],
                            s.get("Authority", "N/A"), s.get("Program", "N/A"),
                            s.get("Start Date", "N/A"), s.get("End Date", "N/A"),
                            entry["First Seen"], entry["Last Seen"]
                        ])
        print(f"\nData exported to '{business_name}_sanctions.json' and '{business_name}_sanctions.csv' (with improved aliases and fuzzy filtering).")

    except Exception as e:
        print(f"Error: {e}")
