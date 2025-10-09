# Custom Modules
from ui.streamlit_ui import run_streamlit_app
from utils.session import init_session_state

if __name__ == "__main__":
    print('Loading Session State...') 
    init_session_state()
    
    run_streamlit_app() 
    print('Application started successfully!') 