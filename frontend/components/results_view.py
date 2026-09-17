import streamlit as st

def render_results(response: dict):
    st.subheader("2. Decision Engine Results")
    
    # Overview
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Decision Status", response.get("decision", "UNKNOWN"))
    with col2:
        conf = response.get("confidence", 0.0)
        st.metric("Confidence Score", f"{conf * 100:.1f}%")
        
    st.divider()
    
    # Key Findings & Citations
    st.markdown("### Key Findings & Evidence")
    for idx, finding in enumerate(response.get("key_findings", [])):
        supported_str = "✅ Supported" if finding.get("is_supported") else "❌ Unsupported"
        st.markdown(f"**{idx+1}. {finding.get('description')}** ({supported_str})")
        
        with st.expander("View Citations"):
            citations = finding.get("citations", [])
            if not citations:
                st.write("*No citations provided.*")
            for c in citations:
                st.markdown(f"> {c.get('text')}\n\n*Source: {c.get('source')} | Page: {c.get('page')}*")
                
    st.divider()
    
    # Missing Evidence
    missing = response.get("missing_evidence", [])
    if missing:
        st.warning(f"**Missing Required Evidence:** {', '.join(missing)}")
        
    st.divider()
    
    # Validation & Execution Trace
    st.markdown("### Observability & Trace")
    val = response.get("validation", {})
    st.write("**Validation Status:**", "Pass" if val.get("is_valid") else "Fail")
    if val.get("validation_errors"):
        st.error(f"Validation Errors: {val.get('validation_errors')}")
        
    with st.expander("Execution Trace & Latency"):
        trace = response.get("trace", [])
        for step in trace:
            st.text(f"Agent: {step.get('agent')} | Action: {step.get('action')} | Latency: {step.get('total_latency_ms')}ms")
