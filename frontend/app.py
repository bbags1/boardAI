import streamlit as st
import requests
import os
from typing import Union
import json

# Configure API endpoint
API_URL = "http://localhost:8000/api/v1"

def initialize_session():
    """Initialize session state variables"""
    if 'token' not in st.session_state:
        st.session_state.token = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'show_upload_modal' not in st.session_state:
        st.session_state.show_upload_modal = False
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'password' not in st.session_state:
        st.session_state.password = ""
    if 'full_name' not in st.session_state:
        st.session_state.full_name = ""
    if 'org_name' not in st.session_state:
        st.session_state.org_name = ""

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
    if not st.session_state.token:
        st.sidebar.warning("Please login to manage documents")
        return

    st.sidebar.markdown("---")
    st.sidebar.header("Document Management")
    
    try:
        response = requests.get(
            f"{API_URL}/documents/list",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if response.status_code == 200:
            documents = response.json()
            
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
                        delete_response = requests.delete(
                            f"{API_URL}/documents/{doc['id']}",
                            headers={"Authorization": f"Bearer {st.session_state.token}"}
                        )
                        if delete_response.status_code == 200:
                            st.sidebar.success("Document deleted!")
                            st.rerun()
                        else:
                            st.sidebar.error("Error deleting document")
        else:
            st.sidebar.error("Error fetching documents")
    except Exception as e:
        st.sidebar.error(f"Error: {str(e)}")

def display_chat():
    st.write("### Board Discussion")
    
    if not st.session_state.token:
        st.info("Please login to use the chat feature")
        return
    
    # Add advisor selection
    advisor_roles = st.multiselect(
        "Select Advisors",
        ["legal", "financial", "technology"],
        default=["legal", "financial", "technology"]
    )
        
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Message the board..."):
        # Add user message to chat
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        try:
            # Make API call to get board response
            response = requests.post(
                f"{API_URL}/advisors/analyze",
                json={
                    "topic": prompt,
                    "advisor_roles": advisor_roles
                },
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                stream=True
            )
            
            if response.status_code == 200:
                # Initialize the response container
                response_container = st.empty()
                full_response = ""
                
                # Process the streaming response
                for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                    if chunk:
                        full_response += chunk
                        response_container.markdown(full_response + "▌")
                
                # Final update without cursor
                response_container.markdown(full_response)
                
                # Add to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })
            else:
                st.error(f"Error getting response: {response.json()['detail']}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
        
        st.rerun()

def main():
    initialize_session()  # Initialize session state first
    st.title("BoardAI")
    
    # Authentication section in sidebar
    st.sidebar.header("Authentication")
    if not st.session_state.token:
        tab1, tab2 = st.sidebar.tabs(["Login", "Register"])
        
        with tab1:
            with st.form("login_form"):
                email = st.text_input("Email", value=st.session_state.email, key="login_email")
                password = st.text_input("Password", type="password", value=st.session_state.password, key="login_password")
                if st.form_submit_button("Login"):
                    try:
                        response = requests.post(
                            f"{API_URL}/auth/token",
                            data={"username": email, "password": password}
                        )
                        if response.status_code == 200:
                            st.session_state.token = response.json()["access_token"]
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Login failed")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
        
        with tab2:
            with st.form("register_form"):
                email = st.text_input("Email", value=st.session_state.email, key="register_email")
                password = st.text_input("Password", type="password", value=st.session_state.password, key="register_password")
                full_name = st.text_input("Full Name", value=st.session_state.full_name, key="register_full_name")
                org_name = st.text_input("Organization Name", value=st.session_state.org_name, key="register_org_name")
                if st.form_submit_button("Register"):
                    try:
                        response = requests.post(
                            f"{API_URL}/auth/register",
                            json={
                                "email": email,
                                "password": password,
                                "full_name": full_name,
                                "organization_name": org_name
                            }
                        )
                        if response.status_code == 200:
                            st.success("Registration successful! Please login.")
                        else:
                            st.error(f"Registration failed: {response.json()['detail']}")
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    else:
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.rerun()

        # Document upload section
    uploaded_file = None
    doc_type = None
    
    if st.session_state.token:
        st.sidebar.header("Document Upload")
        uploaded_file = st.sidebar.file_uploader("Upload Company Document", type=['pdf', 'txt'])
        doc_type = st.sidebar.selectbox("Document Type", 
            ["Financial Report", "Legal Document", "Technical Specification", "Meeting Minutes"])

    if uploaded_file and doc_type:
        if st.sidebar.button("Upload Document", type="primary"):
            try:
                # Set the appropriate content type based on file extension
                content_type = "application/pdf" if uploaded_file.name.lower().endswith('.pdf') else "text/plain"
            
                files = {
                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        content_type
                    )
                }
                params = {"type": doc_type}
                response = requests.post(
                    f"{API_URL}/documents/upload",
                    files=files,
                    params=params,
                    headers={"Authorization": f"Bearer {st.session_state.token}"}
                )
                if response.status_code == 200:
                    st.session_state.show_upload_modal = True
                    st.rerun()
                else:
                    st.sidebar.error(f"Error uploading document: {response.json()['detail']}")
            except Exception as e:
                st.sidebar.error(f"Error: {str(e)}")

    # Show upload modal if needed
    if st.session_state.show_upload_modal:
        show_upload_modal()

    if st.session_state.token:
        display_chat()
    # Display document management
    display_document_management()

if __name__ == "__main__":
    main()