import streamlit as st
import json

def render_upload_section():
    st.subheader("1. Input Claim Data")
    
    input_method = st.radio("Choose Input Method", ["Upload JSON", "Paste JSON"])
    
    claim_data = None
    if input_method == "Upload JSON":
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
