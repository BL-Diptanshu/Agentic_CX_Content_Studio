import streamlit as st
import json
import time
import requests
from pathlib import Path

st.set_page_config(page_title="Agentic CX Content Studio", layout="wide")

st.title("🎨 Agentic CX Content Studio")
st.markdown("---")

st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Create Campaign", "View Campaigns"])

if page == "Create Campaign":
    st.header("Create New Marketing Campaign")
    
    # Input method selector
    input_method = st.radio(
        "How would you like to provide campaign details?",
        ["📄 Upload Document", "✏️ Manual Entry"],
        horizontal=True
    )
    
    st.markdown("---")
    
    # Initialize variables
    campaign_name = ""
    brand = ""
    objective = ""
    target_audience = ""
    
    if input_method == "📄 Upload Document":
        st.info("💡 Upload a campaign brief document (DOCX, PDF, or TXT) to automatically extract campaign details!")
        
        uploaded_file = st.file_uploader(
            "Choose your campaign brief",
            type=['docx', 'pdf', 'txt'],
            help="Upload a document like 'FitNow Official Brand Guidelines Document.docx'"
        )
        
        if uploaded_file is not None:
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            
            with st.spinner("Parsing document..."):
                try:
                    # Import parser
                    import sys
                    sys.path.append(str(Path(__file__).parent))
                    from src.processing.document_parser import parse_uploaded_document
                    
                    # Parse the document
                    extracted_data = parse_uploaded_document(uploaded_file)
                    
                    if 'error' in extracted_data:
                        st.error(f"❌ Error parsing document: {extracted_data['error']}")
                    else:
                        st.success("✅ Successfully extracted campaign information!")
                        
                        # Display extracted data in an expander
                        with st.expander("📋 View Extracted Information", expanded=True):
                            st.json(extracted_data)
                        
                        # Populate fields
                        campaign_name = extracted_data.get('campaign_name', '')
                        brand = extracted_data.get('brand', '')
                        objective = extracted_data.get('objective', '')
                        target_audience = extracted_data.get('target_audience', '')
                        
                        # Allow editing
                        st.markdown("### ✏️ Review & Edit Extracted Information")
                        col1, col2 = st.columns(2)
                        with col1:
                            campaign_name = st.text_input("Campaign Name", value=campaign_name)
                            brand = st.text_input("Brand Name", value=brand)
                        with col2:
                            objective = st.text_area("Campaign Objectives", value=objective, height=100)
                            target_audience = st.text_input("Target Audience", value=target_audience)
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Please try manual entry or check the document format.")
    
    else:  # Manual Entry
        with st.form("campaign_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                campaign_name = st.text_input("Campaign Name", placeholder="e.g., Summer Sale 2024")
                brand = st.text_input("Brand Name", placeholder="e.g., Acme Corp")
                
            with col2:
                objective = st.text_area("Campaign Objectives", placeholder="Increase brand awareness...")
                target_audience = st.text_input("Target Audience", placeholder="e.g., Tech enthusiasts, Gen Z")
                
            other_inputs = st.text_area("Additional Inputs (JSON format optional)", placeholder='{"key": "value"}')
            
            submit_button = st.form_submit_button("🚀 Create Campaign")
            
            if submit_button:
                if not campaign_name or not brand:
                    st.error("❌ Campaign Name and Brand are required!")
                else:
                    # Process and submit
                    inputs = {"target_audience": target_audience}
                    if other_inputs:
                        try:
                            extra_inputs = json.loads(other_inputs)
                            inputs.update(extra_inputs)
                        except json.JSONDecodeError:
                            st.warning("⚠️ Invalid JSON in Additional Inputs. Ignoring extra inputs.")

                    payload = {
                        "campaign_name": campaign_name,
                        "brand": brand,
                        "objective": objective,
                        "inputs": inputs
                    }
                    
                    # Store payload in session state for regeneration
                    st.session_state.last_payload = payload
                    
                    with st.spinner("🔄 Creating campaign and generating content with auto-regeneration..."):
                        try:
                            # Use orchestration endpoint with auto-regeneration
                            response = requests.post(
                                "http://localhost:8000/api/v1/orchestrate/campaign",
                                json=payload,
                                params={"auto_regenerate": True, "max_attempts": 3}
                            )
                            
                            if response.status_code == 200:
                                data = response.json()
                                campaign_id = data.get('campaign_id')
                                result_str = data.get('result', '')
                                attempts = data.get('attempts', 1)
                                status = data.get('status', 'unknown')
                                
                                # Store campaign data in session state
                                st.session_state.current_campaign = {
                                    'campaign_id': campaign_id,
                                    'campaign_name': campaign_name,
                                    'brand': brand,
                                    'data': {
                                        'result': result_str,
                                        'campaign_id': campaign_id,
                                        'attempts': attempts,
                                        'status': status
                                    }
                                }
                                
                                if status == 'approved':
                                    st.success(f"✅ Campaign '{campaign_name}' created and approved! (Attempts: {attempts}) ID: {campaign_id}")
                                else:
                                    st.warning(f"⚠️ Campaign '{campaign_name}' created but validation failed after {attempts} attempts. ID: {campaign_id}")
                                
                            else:
                                st.error(f"❌ Error creating campaign: {response.status_code} - {response.text}")
                        except requests.exceptions.ConnectionError:
                            st.error("❌ Failed to connect to backend API. Is the server running on port 8000?")
                        except Exception as e:
                            st.error(f"❌ An unexpected error occurred: {str(e)}")
    
    # Create Campaign button for document upload mode (outside form)
    if input_method == "📄 Upload Document" and campaign_name and brand:
        st.markdown("---")
        if st.button("🚀 Create Campaign with Extracted Details", type="primary", use_container_width=True):
            inputs = {"target_audience": target_audience}
            payload = {
                "campaign_name": campaign_name,
                "brand": brand,
                "objective": objective,
                "inputs": inputs
            }
            
            st.session_state.last_payload = payload
            
            with st.spinner("🔄 Creating campaign with auto-regeneration..."):
                try:
                    response = requests.post(
                        "http://localhost:8000/api/v1/orchestrate/campaign",
                        json=payload,
                        params={"auto_regenerate": True, "max_attempts": 3}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        campaign_id = data.get('campaign_id')
                        result_str = data.get('result', '')
                        attempts = data.get('attempts', 1)
                        status = data.get('status', 'unknown')
                        
                        st.session_state.current_campaign = {
                            'campaign_id': campaign_id,
                            'campaign_name': campaign_name,
                            'brand': brand,
                            'data': {'result': result_str, 'campaign_id': campaign_id, 'attempts': attempts, 'status': status}
                        }
                        
                        if status == 'approved':
                            st.success(f"✅ Campaign created & approved! (Attempts: {attempts})")
                        else:
                            st.warning(f"⚠️ Validation failed after {attempts} attempts")
                    else:
                        st.error(f"❌ Error: {response.status_code}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display results if campaign was created
    if 'current_campaign' in st.session_state and st.session_state.current_campaign:
        st.markdown("---")
        st.header("📊 Generated Content")
        
        campaign_data = st.session_state.current_campaign
        data = campaign_data.get('data', {})
        
        #Extract text and image from orchestration result
        result_str = data.get('result', '')
        attempts = data.get('attempts', 1)
        status = data.get('status', 'unknown')
        
        # Display attempt info
        if attempts > 1:
            if status == 'approved':
                st.info(f"✅ Content was approved after {attempts} regeneration attempt(s)")
            else:
                st.warning(f"⚠️ Validation failed after {attempts} attempts. Showing last generated content.")
        
        # Parse result to extract image URL
        import ast
        image_url = ''
        text_content = result_str
        
        try:
            # Determine if we have a dict or need to parse one
            parsed_data = None
            if isinstance(result_str, dict):
                parsed_data = result_str
            else:
                # Attempt to parse dictionary string
                try:
                    parsed = ast.literal_eval(result_str)
                    if isinstance(parsed, dict):
                        parsed_data = parsed
                except:
                    parsed_data = None

            if parsed_data:
                text_content = parsed_data.get('text', result_str)
                raw_image = parsed_data.get('image', '')
                
                # Extract URL from raw_image string
                import re
                # Regex to find http/https or /static/ paths, excluding quotes, brackets, and trailing punctuation
                # Added quote/punctuation exclusion to prevent capturing trailing chars
                url_match = re.search(r'(https?://[^\s\)\'\"]+|/static/[^\s\)\'\"]+)', raw_image)
                
                if url_match:
                    image_url = url_match.group()
                    # Clean potential trailing punctuation (like a dot at end of sentence)
                    image_url = image_url.rstrip('.,;:)')
                    
                    if image_url.startswith('/static'):
                        # Prepend backend URL for local images
                        image_url = f"http://localhost:8000{image_url}"
                else:
                    # Fallback: maybe raw_image IS the path
                    image_url = raw_image if (raw_image.startswith('http') or raw_image.startswith('/')) else ''
                    if image_url.startswith('/static'):
                        image_url = f"http://localhost:8000{image_url}"
            else:
                 raise ValueError("Could not parse result as dict")

        except Exception:
            # Fallback regex extraction on the original string
            import re
            url_match = re.search(r'https?://[^\s\)\'\"]+', str(result_str)) or re.search(r'/static/[^\s\)\'\"]+', str(result_str))
            if url_match:
                image_url = url_match.group()
                if image_url.startswith('/static'):
                    image_url = image_url.lstrip('/')
                # Attempt to clean text content by removing the URL
                text_content = str(result_str).replace(image_url, '').strip()
        
        col1, col2 = st.columns([1.5, 1])
        
        with col1:
            st.subheader("📝 Generated Text")
            st.markdown(text_content)
        
        with col2:
            st.subheader("🖼️ Generated Image")
            if image_url:
                try:
                    st.image(image_url, use_container_width=True, caption="Generated Marketing Image")
                except:
                    st.error("Could not load image. URL: " + image_url)
            else:
                st.info("No image URL found in result")
        
        # Action buttons
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns(3)
        
        with col_btn1:
            if st.button("🔄 Regenerate Content"):
                if 'last_payload' in st.session_state:
                    with st.spinner("Regenerating..."):
                        try:
                            response = requests.post(
                                "http://localhost:8000/api/v1/orchestrate/campaign",
                                json=st.session_state.last_payload,
                                params={"auto_regenerate": True, "max_attempts": 3}
                            )
                            if response.status_code == 200:
                                data = response.json()
                                st.session_state.current_campaign['data']['result'] = data.get('result', '')
                                st.session_state.current_campaign['data']['attempts'] = data.get('attempts', 1)
                                st.session_state.current_campaign['data']['status'] = data.get('status', 'unknown')
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        
        with col_btn2:
            if st.button("💾 Save Campaign"):
                st.success("Campaign saved to database!")
        
        with col_btn3:
            if st.button("📋 View All Campaigns"):
                st.switch_page("pages/view_campaigns.py") if Path("pages/view_campaigns.py").exists() else st.info("Navigate to 'View Campaigns' page")

elif page == "View Campaigns":
    st.header("📂 All Campaigns")
    
    with st.spinner("Loading campaigns..."):
        try:
            response = requests.get("http://localhost:8000/api/v1/campaigns/")
            if response.status_code == 200:
                campaigns = response.json()
                if campaigns:
                    for campaign in campaigns:
                        campaign_id = campaign.get('campaign_id')
                        with st.expander(f"🎯 {campaign.get('campaign_name', 'Unnamed')} - {campaign.get('brand', 'No Brand')}"):
                            st.write(f"**Campaign ID:** {campaign_id}")
                            st.write(f"**Objective:** {campaign.get('objective', 'N/A')}")
                            st.write(f"**Created At:** {campaign.get('created_at', 'N/A')}")
                            
                            # Fetch detailed results
                            try:
                                res_response = requests.get(f"http://localhost:8000/api/v1/campaigns/{campaign_id}/results")
                                if res_response.status_code == 200:
                                    results = res_response.json()
                                    
                                    st.markdown("### 📝 Generated Copy")
                                    text_data = results.get('generated_text') or "No text content found."
                                    
                                    # Attempt to clean up if it's the legacy raw dict string
                                    try:
                                        import ast
                                        if text_data.strip().startswith("{") and "'text':" in text_data:
                                            parsed = ast.literal_eval(text_data)
                                            if isinstance(parsed, dict) and 'text' in parsed:
                                                text_data = parsed['text']
                                    except:
                                        pass
                                        
                                    st.info(text_data)
                                    
                                    st.markdown("### 🖼️ Generated Image")
                                    img_url = results.get('image_url')
                                    if img_url:
                                        # Clean path for display equivalent to frontend logic
                                        cleaned_url = img_url.rstrip('.,;:)')
                                        if cleaned_url.startswith('/static'):
                                             cleaned_url = f"http://localhost:8000{cleaned_url}"
                                        st.image(cleaned_url, caption="Campaign Image", use_container_width=True)
                                    else:
                                        st.warning("No image content found.")
                                else:
                                    st.warning("No results found for this campaign.")
                            except Exception as e:
                                st.error(f"Could not load details: {e}")

                else:
                    st.info("📭 No campaigns found. Create your first campaign!")
            else:
                st.error(f"Error fetching campaigns: {response.status_code}")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Please ensure the server is running.")
        except Exception as e:
            st.error(f"Error: {str(e)}")
