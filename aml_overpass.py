import requests
import folium
from folium.plugins import MarkerCluster
import webbrowser

def fetch_microsoft_entities():
    query = """
    [out:json][timeout:1800];
    (
      node["name"~"Microsoft", i];
      node["operator"~"Microsoft", i];
      node["brand"~"Microsoft", i];

      way["name"~"Microsoft", i];
      way["operator"~"Microsoft", i];
      way["brand"~"Microsoft", i];

      relation["name"~"Microsoft", i];
      relation["operator"~"Microsoft", i];
      relation["brand"~"Microsoft", i];
    );
    out center;
    """
    print("Sending Overpass query for 'Microsoft' entities worldwide...")
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

def create_map(elements, map_filename="microsoft_entities_map.html"):
    if not elements:
        print("No elements to display on map.")
        return

    # Use a default center (Microsoft HQ)
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
            name = el.get("tags", {}).get("name", "Microsoft Facility")
            folium.Marker([lat, lon], popup=name).add_to(cluster)

    my_map.save(map_filename)
    print(f"🗺️ Map saved as: {map_filename}")
    webbrowser.open(map_filename)

# Run the script
elements = fetch_microsoft_entities()
create_map(elements)
