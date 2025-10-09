# Non-Standard Libraries
import streamlit as st

def init_session_state():
    defaults = {
        'file_name': None,
        'file_text': None,
        'summary': None,
        'translation': None,
        'lang': 'English',
        'status': 'Awaiting Upload',
        'viewing': None
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value