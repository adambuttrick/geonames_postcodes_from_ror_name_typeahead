import streamlit as st
from streamlit_searchbox import st_searchbox
import pandas as pd
from search_functions import (
    search_ror, get_all_names, query_geonames_api, parse_geonames_response,
    reverse_geocode, parse_reverse_geocode_response, get_ror_display_name
)

def main():
    st.title("ROR-Geonames Typeahead App")
    
    geonames_username = st.text_input("Enter your Geonames username")
    
    if not geonames_username:
        st.warning("Please enter your Geonames username to use the app.")
        return
    
    selected_org = st_searchbox(
        search_function=search_ror,
        placeholder="Search for an organization",
        key="org_search"
    )
    
    if selected_org:
        st.subheader("Organization Details")
        org_df = pd.DataFrame({
            "Name": [get_ror_display_name(selected_org)],
            "ROR ID": [selected_org['id']]
        })
        st.write(org_df.to_html(index=False), unsafe_allow_html=True)
        
        all_names = get_all_names(selected_org)
        
        geonames_match = None
        matched_name = None
        for name in all_names:
            geonames_response = query_geonames_api(name, geonames_username)
            if geonames_response and "geonames" in geonames_response and len(geonames_response["geonames"]) > 0:
                geonames_match = parse_geonames_response(geonames_response)
                matched_name = name
                break
        
        if geonames_match:
            st.subheader("Geonames Details")
            geonames_df = pd.DataFrame({
                "ROR Name": [matched_name],
                "Geonames Name": [geonames_match['name']],
                "Geonames ID": [geonames_match['geonames_id']],
                "Country": [geonames_match['country']],
                "Latitude": [geonames_match['lat']],
                "Longitude": [geonames_match['lng']]
            })
            st.write(geonames_df.to_html(index=False), unsafe_allow_html=True)
            
            reverse_geocode_response = reverse_geocode(geonames_match['lat'], geonames_match['lng'], geonames_username)
            if reverse_geocode_response:
                postal_data = parse_reverse_geocode_response(reverse_geocode_response)
                if postal_data:
                    st.subheader("Postal Code Details")
                    postal_df = pd.DataFrame({
                        "Postal Code": [postal_data['postal_code']],
                        "Place Name": [postal_data['place_name']],
                        "Admin Name 1": [postal_data['admin_name1']],
                        "Admin Name 2": [postal_data['admin_name2']]
                    })
                    st.write(postal_df.to_html(index=False), unsafe_allow_html=True)
        else:
            st.write("No matching Geonames record found.")

if __name__ == "__main__":
    main()