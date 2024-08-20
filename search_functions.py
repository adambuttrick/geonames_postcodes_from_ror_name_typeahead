import requests
import streamlit as st

ROR_API_URL = "https://api.ror.org/v2/organizations"
GEONAMES_API_URL = "http://api.geonames.org"

def query_ror_api(query):
    response = requests.get(ROR_API_URL, params={"query": query})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error querying ROR API: {response.status_code}")
        return None


def get_all_names(org):
    names = []
    if 'names' in org:
        for name in org['names']:
            if 'ror_display' in name.get('types', []):
                names.append(name['value'])
        for name in org['names']:
            if 'label' in name.get('types', []) and name['value'] not in names:
                names.append(name['value'])
        for name in org['names']:
            if 'alias' in name.get('types', []) and name['value'] not in names:
                names.append(name['value'])
    return [name for name in names if not name.isupper()]  # Exclude acronyms


def query_geonames_api(query, username):
    params = {
        "q": query,
        "maxRows": 1,
        "username": username
    }
    response = requests.get(f"{GEONAMES_API_URL}/searchJSON", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error querying Geonames API: {response.status_code}")
        return None


def parse_geonames_response(response):
    if not response or "geonames" not in response or len(response["geonames"]) == 0:
        return None

    place = response["geonames"][0]
    return {
        "geonames_id": place["geonameId"],
        "name": place["name"],
        "lat": place["lat"],
        "lng": place["lng"],
        "country": place["countryName"]
    }


def reverse_geocode(lat, lng, username):
    params = {
        "lat": lat,
        "lng": lng,
        "username": username
    }
    response = requests.get(f"{GEONAMES_API_URL}/findNearbyPostalCodesJSON", params=params)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error reverse geocoding: {response.status_code}")
        return None


def parse_reverse_geocode_response(response):
    if not response or "postalCodes" not in response or len(response["postalCodes"]) == 0:
        return None

    postal_code = response["postalCodes"][0]
    return {
        "postal_code": postal_code["postalCode"],
        "place_name": postal_code["placeName"],
        "admin_name1": postal_code["adminName1"],
        "admin_name2": postal_code["adminName2"]
    }


def get_ror_display_name(org):
    for name in org.get("names", []):
        if "ror_display" in name.get("types", []):
            return name["value"]
    return org["names"][0]["value"] if org.get("names") else "Unknown"


def search_ror(query):
    ror_response = query_ror_api(query)
    if ror_response:
        return [(get_ror_display_name(org), org) for org in ror_response.get("items", [])]
    return []
