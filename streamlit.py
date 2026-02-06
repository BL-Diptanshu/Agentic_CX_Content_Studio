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
                
                # Store payload in session state for regeneration
                st.session_state.last_payload = payload
                
                with st.spinner("Creating campaign and generating content..."):
                    try:
                       
                        # Use orchestration endpoint with CrewAI
                        response = requests.post("http://localhost:8000/api/v1/orchestrate/campaign", json=payload)
                        
                        if response.status_code == 200:
                            data = response.json()
                            campaign_id = data.get('campaign_id')
                            result_str = data.get('result', '')
                            
                            # Store campaign data in session state
                            st.session_state.current_campaign = {
                                'campaign_id': campaign_id,
                                'campaign_name': campaign_name,
                                'brand': brand,
                                'data': {
                                    'result': result_str,
                                    'campaign_id': campaign_id
                                }
                            }
                            
                            st.success(f"✅ Campaign '{campaign_name}' created successfully! ID: {campaign_id}")
                            
                        else:
                            st.error(f"Error creating campaign: {response.status_code} - {response.text}")
                    except requests.exceptions.ConnectionError:
                        st.error("Failed to connect to backend API. Is the server running?")
                    except Exception as e:
                        st.error(f"An unexpected error occurred: {str(e)}")
    
    # Display results if campaign was created
    if 'current_campaign' in st.session_state and st.session_state.current_campaign:
        st.markdown("---")
        st.header("📊 Generated Content")
        
        campaign_data = st.session_state.current_campaign
        data = campaign_data.get('data', {})
        
        # Extract text and image from orchestration result
        result_str = data.get('result', '')
        
        # Parse result to extract image URL
        import re
        image_url = ''
        text_content = result_str
        
        # Look for URLs in the result
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+'
        urls = re.findall(url_pattern, result_str)
        
        if urls:
            # Assume first URL is the image
            image_url = urls[0]
            # Remove URL from text
            text_content = result_str.replace(image_url, '').strip()

        
        # Side-by-side layout
        col_text, col_image = st.columns(2)
        
        with col_text:
            st.subheader("📝 Generated Text")
            if text_content:
                st.markdown(text_content)
            else:
                st.info("No text content available. The content may still be generating or there was an issue.")
                # Show raw data for debugging
                if st.checkbox("Show raw data"):
                    st.json(data)
        
        with col_image:
            st.subheader("🖼️ Generated Image")
            if image_url:
                try:
                    st.image(image_url, use_column_width=True, caption="Generated Marketing Image")
                except Exception as e:
                    st.error(f"Failed to load image: {str(e)}")
                    st.write(f"Image URL: {image_url}")
            else:
                st.info("No image available. The image may still be generating or there was an issue.")
        
        # Action buttons
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        
        with col_btn1:
            if st.button("🔄 Regenerate", key="regenerate_btn", help="Generate new content with the same inputs"):
                if 'last_payload' in st.session_state:
                    with st.spinner("Regenerating content..."):
                        try:
                            response = requests.post("http://localhost:8000/api/v1/start_campaign", 
                                                   json=st.session_state.last_payload)
                            
                            if response.status_code == 200:
                                data = response.json()
                                campaign_id = data.get('campaign_id')
                                
                                # Update session state with new data
                                st.session_state.current_campaign = {
                                    'campaign_id': campaign_id,
                                    'campaign_name': st.session_state.last_payload['campaign_name'],
                                    'brand': st.session_state.last_payload['brand'],
                                    'data': data
                                }
                                
                                st.success("✨ Content regenerated successfully!")
                                st.rerun()
                            else:
                                st.error(f"Regeneration failed: {response.status_code}")
                        except Exception as e:
                            st.error(f"Regeneration error: {str(e)}")
        
        with col_btn2:
            if st.button("✅ Save & Accept", key="save_btn", help="Approve and save this content"):
                campaign_id = campaign_data.get('campaign_id')
                if campaign_id:
                    # TODO: ML Engineer 1 to create this endpoint
                    # For now, just show confirmation
                    st.success(f"✅ Campaign {campaign_id} approved and saved!")
                    st.balloons()
                    
                    # Optional: Clear current campaign after saving
                    # st.session_state.current_campaign = None
                else:
                    st.error("No campaign ID found")
        
        # Generation details
        st.markdown("---")
        with st.expander("📋 Generation Details"):
            st.write(f"**Campaign ID:** {campaign_data.get('campaign_id', 'N/A')}")
            st.write(f"**Campaign Name:** {campaign_data.get('campaign_name', 'N/A')}")
            st.write(f"**Brand:** {campaign_data.get('brand', 'N/A')}")
            
            if 'created_at' in data:
                st.write(f"**Generated:** {data['created_at']}")
            
            st.write("**Full Response:**")
            st.json(data)


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


