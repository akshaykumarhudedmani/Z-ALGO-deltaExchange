import streamlit as st

st.set_page_config(page_title="Settings | TokenIQ", page_icon="⚙️", layout="wide")

if 'authenticated' not in st.session_state or not st.session_state.authenticated:
    st.warning("Please enter via the main App Gate.")
    st.stop()
    
# Layout
st.title("⚙️ System Control Panel")
st.markdown("Manage execution state and session memory.")

st.divider()

col1, col2 = st.columns(2)

# --- 1. THE KILL SWITCH ---
col1.subheader("🛑 Engine Kill Switch")
col1.markdown("Immediately halts all simulated execution and API routing in the background.")

if st.session_state.get('kill_switch', False):
    col1.error("**STATUS: SYSTEM HALTED MOCK**")
    if col1.button("🟢 Reboot Algo Engine"):
        st.session_state.kill_switch = False
        st.rerun()
else:
    col1.success("**STATUS: ENGINE ACTIVE**")
    if col1.button("🔴 ENGAGE KILL SWITCH"):
        st.session_state.kill_switch = True
        st.rerun()

# --- 2. SESSION RESET ---
col2.subheader("🔄 Master Reset")
col2.markdown("Clears all session states and mock data for fresh hackathon demonstration pitching.")

if col2.button("⚠️ Clear App Memory (Logout)"):
    # Clear all state
    # st.session_state.clear() 
    # Because clearing drops 'authenticated', it'll kick user to app.py 
    for key in list(st.session_state.keys()):
        del st.session_state[key]
        
    st.success("Session cleared. Please return to the main entry page.")
    st.rerun()

st.divider()
st.caption("Settings affect the active browser instance only. Delta API connection relies on env.")
