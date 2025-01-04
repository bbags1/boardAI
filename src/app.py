import streamlit as st
import os
from typing import Union
import sounddevice as sd
import numpy as np
import wave
import tempfile
from main import AdvisoryBoard

def initialize_board():
    if 'board' not in st.session_state:
        st.session_state.board = AdvisoryBoard()
        st.session_state.board.add_advisor("legal")
        st.session_state.board.add_advisor("financial")
        st.session_state.board.add_advisor("technology")
    
    # Initialize states
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'mic_text' not in st.session_state:
        st.session_state.mic_text = ""
    if 'show_upload_modal' not in st.session_state:
        st.session_state.show_upload_modal = False

def show_upload_modal():
    """Display upload success modal"""
    modal_container = st.empty()
    with modal_container.container():
        st.markdown("### ✅ Document Upload Successful")
        st.write("Your document has been processed and stored in the system.")
        if st.button("Close"):
            modal_container.empty()
            st.session_state.show_upload_modal = False
            st.rerun()

def display_document_management():
    """Display and manage stored documents"""
    st.sidebar.markdown("---")
    st.sidebar.header("Document Management")
    
    doc_manager = st.session_state.board.advisors["legal"].document_manager
    documents = doc_manager.get_all_documents()
    
    if not documents:
        st.sidebar.info("No documents stored in the system.")
        return
        
    for doc in documents:
        col1, col2 = st.sidebar.columns([3, 1])
        
        with col1:
            st.markdown(f"""
            **{doc['type']}**  
            *{doc['timestamp'][:10]}*  
            {len(doc['content'])} chars
            """)
            
        with col2:
            if st.button("🗑️", key=f"delete_{doc['id']}", help="Delete this document"):
                try:
                    doc_manager.delete_document(doc['id'])
                    st.sidebar.success("Document deleted!")
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error deleting document: {str(e)}")

def record_audio(duration=5, sample_rate=44100):
    """Record audio from microphone and save to temp file"""
    try:
        # Record audio
        recording = sd.rec(int(duration * sample_rate),
                         samplerate=sample_rate,
                         channels=1,
                         dtype=np.int16)
        sd.wait()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            with wave.open(tmp_file.name, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                wf.writeframes(recording.tobytes())
            return tmp_file.name
            
    except Exception as e:
        st.error(f"Error recording audio: {str(e)}")
        return None

def create_chat_input():
    """Create a custom chat input with microphone button"""
    cols = st.columns([0.92, 0.08])
    
    with cols[0]:
        user_text = st.text_input(
            "Message the board...", 
            key="chat_input", 
            label_visibility="collapsed"
        )
    
    with cols[1]:
        mic_clicked = st.button(
            "🎤" if not st.session_state.recording else "⏹️",
            help="Click to start/stop recording",
            type="primary" if st.session_state.recording else "secondary"
        )
        
        if mic_clicked:
            if not st.session_state.recording:
                st.session_state.recording = True
                st.rerun()
            else:
                st.session_state.recording = False
                with st.spinner("Recording..."):
                    audio_file = record_audio()
                    if audio_file:
                        st.session_state.audio_file = audio_file
                        st.rerun()
    
    return user_text

def get_advisor_avatar(role: str) -> str:
    """Return emoji avatar for each advisor"""
    avatars = {
        "legal": "⚖️",
        "financial": "💰",
        "technology": "💻",
        "synthesis": "🤝",
        "user": "🧑‍💼"
    }
    return avatars.get(role, "🤖")

def main():
    st.title("AI Advisory Board")
    
    # Initialize
    initialize_board()
    
    # Create necessary directories
    os.makedirs("data/memory/conversations", exist_ok=True)
    os.makedirs("data/memory/documents", exist_ok=True)
    os.makedirs("temp", exist_ok=True)

    # Sidebar for selecting advisors
    st.sidebar.header("Select Advisors for Discussion")
    advisor_options = {
        "Legal Advisor": "legal",
        "Financial Advisor": "financial",
        "Technology Advisor": "technology"
    }
    
    selected_advisors = []
    for advisor_name, advisor_role in advisor_options.items():
        if st.sidebar.checkbox(advisor_name, True):
            selected_advisors.append(advisor_role)

    # Document upload section
    st.sidebar.header("Document Upload")
    uploaded_file = st.sidebar.file_uploader("Upload Company Document", type=['pdf', 'txt'])
    doc_type = st.sidebar.selectbox("Document Type", 
        ["Financial Report", "Legal Document", "Technical Specification", "Meeting Minutes"])
    
    if uploaded_file and doc_type:
        if st.sidebar.button("Upload Document", type="primary"):
            try:
                temp_path = os.path.join("temp", uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                doc_id = st.session_state.board.advisors["legal"].document_manager.add_document(
                    temp_path, doc_type)
                st.session_state.show_upload_modal = True
                st.rerun()
            except Exception as e:
                st.sidebar.error(f"Error processing document: {str(e)}")
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)

    # Show upload modal if needed
    if st.session_state.show_upload_modal:
        show_upload_modal()

    # Display document management
    display_document_management()

    # Chat interface
    st.write("### Board Discussion")
    
    # Display chat history
    for idx, message in enumerate(st.session_state.chat_history):
        with st.chat_message(message["role"], avatar=get_advisor_avatar(message["role"])):
            st.write(message["content"])

    # Custom chat input with microphone
    user_input = create_chat_input()
    
    # If recording, show status
    if st.session_state.recording:
        st.info("🎤 Recording... Click microphone again to stop")
    
    # Process input (text or voice)
    if (user_input or hasattr(st.session_state, 'audio_file')) and not st.session_state.recording:
        if not selected_advisors:
            st.warning("Please select at least one advisor.")
            return

        # Determine input type and content
        input_data = user_input
        input_type = "text"
        
        if hasattr(st.session_state, 'audio_file'):
            input_data = st.session_state.audio_file
            input_type = "audio"
            delattr(st.session_state, 'audio_file')

        # Add user message to chat
        with st.chat_message("user", avatar=get_advisor_avatar("user")):
            st.write("🎤 Voice message" if input_type == "audio" else input_data)
        
        st.session_state.chat_history.append({
            "role": "user",
            "content": "Voice message" if input_type == "audio" else input_data
        })

        # Get advisor responses
        for role in selected_advisors:
            with st.chat_message(role, avatar=get_advisor_avatar(role)):
                message_container = st.empty()
                full_response = ""
                
                for chunk in st.session_state.board.get_individual_analysis(input_data, role):
                    full_response += chunk
                    message_container.markdown(full_response + "▌")
                message_container.markdown(full_response)
                
                st.session_state.chat_history.append({
                    "role": role,
                    "content": full_response
                })

        # Synthesis if multiple advisors
        if len(selected_advisors) > 1:
            with st.chat_message("synthesis", avatar=get_advisor_avatar("synthesis")):
                synthesis_container = st.empty()
                synthesis_text = ""
                
                for chunk in st.session_state.board.facilitate_discussion(input_data, selected_advisors):
                    synthesis_text += chunk
                    synthesis_container.markdown(synthesis_text + "▌")
                synthesis_container.markdown(synthesis_text)
                
                st.session_state.chat_history.append({
                    "role": "synthesis",
                    "content": synthesis_text
                })

if __name__ == "__main__":
    main()