import streamlit as st
import requests
import sys
import os

# Add root directory to path for local execution if needed
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from frontend.components.claim_upload import render_upload_section
from frontend.components.results_view import render_results

# Read API_URL from Streamlit secrets if deployed, else fallback to localhost
if "API_URL" in st.secrets:
    API_URL = st.secrets["API_URL"]
else:
    API_URL = "http://localhost:8000/api/v1/analyze"

st.set_page_config(page_title="Multi-Agent Policy Engine", layout="wide")
st.title("Policy-Aware Multi-Agent RAG Claim Decision Engine")

st.markdown("""
This system evaluates health insurance claims against specific policy limits and rules.
It enforces strict citation matching and prioritizes abstention (`NEEDS_REVIEW`) over hallucinations.
""")

claim_data = render_upload_section()

if claim_data:
    if st.button("Run Analysis", type="primary"):
        with st.spinner("Agents are analyzing the claim..."):
            try:
                # Expecting 'case_id' in claim_data or auto-generating one
                case_id = claim_data.get("case_id", "CASE_UPLOAD")
                payload = {
                    "case_id": case_id,
                    "claim_data": claim_data
                }
                
                resp = requests.post(API_URL, json=payload)
                if resp.status_code == 200:
                    render_results(resp.json())
                else:
                    st.error(f"API Error: {resp.text}")
            except Exception as e:
                st.error(f"Connection Error: Is the FastAPI backend running? ({e})")
