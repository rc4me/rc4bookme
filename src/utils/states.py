from typing import Dict, Optional
import streamlit as st

def setState(
    stateName: str, state: Dict, force: Optional[bool] = False
) -> Dict | None:
    if stateName in st.session_state and not force:
        return
    st.session_state[stateName] = state
    if force:
        return st.session_state[stateName]
