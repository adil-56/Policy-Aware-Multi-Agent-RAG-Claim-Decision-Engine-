import streamlit as st
import json

def render_upload_section():
    st.subheader("1. Input Claim Data")
    
    input_method = st.radio("Choose Input Method", ["Load Sample Case", "Upload JSON", "Paste JSON"])
    
    claim_data = None
    if input_method == "Load Sample Case":
        try:
            import os
            # Ensure path is correct relative to frontend
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            cases_path = os.path.join(base_dir, "candidate_data", "public_test_cases.json")
            with open(cases_path, "r") as f:
                cases = json.load(f)
            
            case_options = {c["case_id"]: c for c in cases}
            selected_case = st.selectbox("Select a Sample Case to Test", list(case_options.keys()))
            claim_data = case_options[selected_case]
            
            with st.expander("View Case Details"):
                st.json(claim_data)
        except Exception as e:
            st.error(f"Could not load sample cases: {e}")
            
    elif input_method == "Upload JSON":
        uploaded_file = st.file_uploader("Upload Claim JSON", type="json")
        if uploaded_file is not None:
            try:
                claim_data = json.load(uploaded_file)
            except json.JSONDecodeError:
                st.error("Invalid JSON format in file.")
    else:
        json_text = st.text_area("Paste Claim JSON Here", height=200)
        if json_text:
            try:
                claim_data = json.loads(json_text)
            except json.JSONDecodeError:
                st.error("Invalid JSON format.")
                
    return claim_data
