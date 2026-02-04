import streamlit as st
import json
import time
import requests

st.set_page_config(page_title="Agentic CX Content Studio", layout="wide")

st.title("Agentic CX Content Studio")
st.markdown("---")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create Campaign", "View Campaigns"])

if page == "Create Campaign":
    st.header("Create New Marketing Campaign")
    
    with st.form("campaign_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            campaign_name = st.text_input("Campaign Name", placeholder="e.g., Summer Sale 2024")
            brand = st.text_input("Brand Name", placeholder="e.g., Acme Corp")
            
        with col2:
            objective = st.text_area("Campaign Objectives", placeholder="Increase brand awareness...")
            target_audience = st.text_input("Target Audience", placeholder="e.g., Tech enthusiasts, Gen Z")
            
        other_inputs = st.text_area("Additional Inputs (JSON format optional)", placeholder='{"key": "value"}')
        
        submitted = st.form_submit_button("Create Campaign")
        
        if submitted:
            if not campaign_name or not brand:
                st.error("Campaign Name and Brand are required!")
            else:
                inputs = {"target_audience": target_audience}
                if other_inputs:
                    try:
                        extra_inputs = json.loads(other_inputs)
                        inputs.update(extra_inputs)
                    except json.JSONDecodeError:
                        st.warning("Invalid JSON in Additional Inputs. Ignoring extra inputs.")

                payload = {
                    "campaign_name": campaign_name,
                    "brand": brand,
                    "objective": objective,
                    "inputs": inputs
                }
                
                with st.spinner("Submitting to backend..."):
                    try:
                       
                        response = requests.post("http://localhost:8000/api/v1/start_campaign", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            st.success(f"Campaign '{campaign_name}' created successfully! ID: {data.get('campaign_id')}")
                            st.json(data)
                        else:
                            st.error(f"Error creating campaign: {response.status_code} - {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Failed to connect to backend API. Is the server running?")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")

elif page == "View Campaigns":
    st.header("Existing Campaigns")
    
    if st.button("Refresh Campaigns"):
        st.session_state.get("refresh", 0)

    try:
        response = requests.get("http://localhost:8000/api/v1/campaigns/")
        if response.status_code == 200:
            campaigns = response.json()
            if campaigns:
                st.dataframe(campaigns)
                
                # Optional: Detailed view
                st.subheader("Details")
                
                # Create friendly display names: "Campaign Name (Brand)"
                campaign_options = {}
                for c in campaigns:
                    display_name = f"{c['campaign_name']} ({c['brand']})"
                    campaign_options[display_name] = c['campaign_id']
                
                selected_display = st.selectbox(
                    "Select Campaign to view details", 
                    list(campaign_options.keys())
                )
                
                if selected_display:
                    campaign_id = campaign_options[selected_display]
                    selected_campaign = next((c for c in campaigns if c['campaign_id'] == campaign_id), None)
                    st.json(selected_campaign)
            else:
                st.info("No campaigns found.")
        else:
            st.error(f"Failed to fetch campaigns. Status: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error("Failed to connect to backend API. Is the server running?")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")


