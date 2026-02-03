import streamlit as st
import json
import time

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
                
                with st.spinner("Simulating submission to backend..."):
                    time.sleep(1) 
                    st.success(f"Campaign '{campaign_name}' captured successfully!")
                    st.info("Payload ready for Backend API:")
                    st.json(payload)

elif page == "View Campaigns":
    st.header("Existing Campaigns")
    st.info("This feature requires Backend Integration (ML Engineer 1).")
