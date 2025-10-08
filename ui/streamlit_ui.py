from pypdf import PdfReader
import streamlit as st
from services.adk_service import initialize_adk, run_adk_sync
from config.settings import MESSAGE_HISTORY_KEY, get_api_key


def run_streamlit_app():
    '''
    Sets up and runs the Streamlit web application for the ADK chat assistant.
    '''
    

    st.set_page_config(page_title='Aura', layout='wide') # Configures the browser tab title and page layout.
    st.title(':blue[Aura]') # Main title of the app.
    st.caption('Powered by ADK & Gemini') # Descriptive text.
    st.header('', divider = 'blue')
    api_key = get_api_key() # Retrieve the API key from settings.
    if not api_key:
        st.error('Action Required: Google API Key Not Found or Invalid! Please set GOOGLE_API_KEY in your .env file. ⚠️')
        st.stop() # Stop the application if the API key is missing, prompting the user for action.
    # Initialize ADK runner and session ID (cached to run only once).
    adk_runner, current_session_id = initialize_adk()
    
    # Display session ID for debugging purposes
    '''st.sidebar.title('Info')
    st.sidebar.divider()
    st.sidebar.info(
        current_session_id
    )
    '''
    print(f"DEBUG UI: Using ADK session ID: {current_session_id}")

    ## < -- PLACEHOLDER CODE -- >
    
    uploaded_file = st.file_uploader("Upload a file (e.g., an image or PDF)", type=None)

    if uploaded_file is not None:
        reader = PdfReader(uploaded_file)

        texts = []
        for page in reader.pages:

            text = page.extract_text()

            texts.append(text.replace('\n', ''))

        st.session_state.file = ' '.join(texts)


     # Initialize chat message history in Streamlit's session state if it doesn't exist.
    if MESSAGE_HISTORY_KEY not in st.session_state:
        st.session_state[MESSAGE_HISTORY_KEY] = []
    # Display existing chat messages from the session state.
    for message in st.session_state[MESSAGE_HISTORY_KEY]:
        with st.chat_message(message['role']): # Use Streamlit's chat message container for styling.
            st.markdown(message['content'])
    # Handle new user input.
    if prompt := st.chat_input('Enter message'):
        # Append user's message to history and display it.
        st.session_state[MESSAGE_HISTORY_KEY].append({'role': 'user', 'content': prompt})
        with st.chat_message('user'):
            st.markdown(prompt)
        # Process the user's message with the ADK agent and display the response.
        with st.chat_message('assistant'):
            message_placeholder = st.empty() # Create an empty placeholder to update with the assistant's response.
            with st.spinner('Assistant is thinking...'): # Show a spinner while the agent processes the request.
                print(f"DEBUG UI: Sending message to ADK with session ID: {current_session_id}")

                agent_response = run_adk_sync(adk_runner, current_session_id, prompt + f'\nInput: {st.session_state.file}') # Call the synchronous ADK runner.
                print(f"DEBUG UI: Received response from ADK: {agent_response[:50]}...")
                message_placeholder.markdown(agent_response) # Update the placeholder with the final response.
        
        # Append assistant's response to history.
        st.session_state[MESSAGE_HISTORY_KEY].append({'role': 'assistant', 'content': agent_response})