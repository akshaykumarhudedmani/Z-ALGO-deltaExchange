import streamlit as st

st.set_page_config(
    page_title="TokenIQ Sentinel AI",
    page_icon="🤖",
    layout="wide"
)

# Initialize Session State
if 'authenticated' not in st.session_state:
    # Direct Entry - No password required for the demo
    st.session_state.authenticated = True 
    
if 'kill_switch' not in st.session_state:
    st.session_state.kill_switch = False

# Layout
st.title("🤖 TokenIQ Sentinel AI Terminal")
st.markdown("### Welcome to the Vanguard of Algorithmic Execution.")

st.info("Direct Access Granted. Please navigate to the **Dashboard** via the sidebar.")

# App Flow
st.sidebar.success("System Online. Select a page above.")
st.sidebar.markdown("---")
st.sidebar.markdown("**TokenIQ Hackathon Build**")