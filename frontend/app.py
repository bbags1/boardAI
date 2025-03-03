import streamlit as st
import time
import requests
import os
from typing import Union, List, Dict, Optional
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
    if 'viewing_document' not in st.session_state:
        st.session_state.viewing_document = None
    if 'document_content' not in st.session_state:
        st.session_state.document_content = None
    if 'document_type' not in st.session_state:
        st.session_state.document_type = None
    if 'selected_advisors' not in st.session_state:
        st.session_state.selected_advisors = []

def show_upload_modal():
    """Show the upload modal"""
    st.session_state.show_upload_modal = True
    st.rerun()

def view_document(document_id: int):
    """Set a document to be viewed"""
    st.session_state.viewing_document = document_id
    st.rerun()

def close_document_viewer():
    """Close the document viewer"""
    st.session_state.viewing_document = None
    st.rerun()

def display_document_viewer():
    """Display the document viewer"""
    if not st.session_state.viewing_document:
        return
    
    try:
        # Get document details
        response = requests.get(
            f"{API_URL}/documents/{st.session_state.viewing_document}",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            document = response.json()
            metadata = document.get("doc_metadata", {})
            
            # Display document info
            st.header(f"Document: {metadata.get('filename', 'Unnamed Document')}")
            
            # Display document content
            st.subheader("Content")
            st.text_area("", value=document.get("content", ""), height=400, key="document_content_area")
            
            # Download button
            col1, col2 = st.columns([1, 5])
            with col1:
                st.download_button(
                    "Download",
                    data=document.get("content", "").encode("utf-8"),
                    file_name=metadata.get("filename", "document.txt"),
                    mime=metadata.get("content_type", "text/plain"),
                    key="download_document_btn"
                )
            with col2:
                if st.button("Close Viewer", key="close_viewer_btn"):
                    close_document_viewer()
            
            # Document metadata
            st.subheader("Document Metadata")
            st.json(metadata)
            
            # Delete document button
            if st.button("Delete Document", type="primary", use_container_width=True, key="delete_document_btn"):
                if st.button("Confirm Delete", type="primary", key="confirm_delete_btn"):
                    delete_response = requests.delete(
                        f"{API_URL}/documents/{st.session_state.viewing_document}",
                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                    )
                    
                    if delete_response.status_code == 200:
                        st.success("Document deleted!")
                        close_document_viewer()
                    else:
                        st.error("Error deleting document")
        else:
            st.error(f"Error loading document: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def display_document_management():
    """Display the document management section"""
    # Document viewer
    if st.session_state.viewing_document:
        display_document_viewer()
        return
    
    # Document list
    st.subheader("Documents")
    
    try:
        response = requests.get(
            f"{API_URL}/documents/list",
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        
        if response.status_code == 200:
            documents = response.json()
            
            if not documents:
                st.info("No documents found. Upload some documents to get started.")
            else:
                # Display documents in a table
                doc_data = []
                for doc in documents:
                    metadata = doc.get("doc_metadata", {})
                    doc_data.append({
                        "ID": doc["id"],
                        "Name": metadata.get("filename", f"Document {doc['id']}"),
                        "Type": doc["type"],
                        "Size": metadata.get("size", "Unknown"),
                        "Date": doc["timestamp"]
                    })
                
                # Create a dataframe for the table
                import pandas as pd
                df = pd.DataFrame(doc_data)
                
                # Display the table with action buttons
                for i, row in df.iterrows():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.write(f"**{row['Name']}**")
                        st.write(f"Type: {row['Type']} | Date: {row['Date'][:10]}")
                    with col2:
                        if st.button("View", key=f"view_doc_{row['ID']}"):
                            view_document(row["ID"])
                    with col3:
                        if st.button("Delete", key=f"delete_doc_{row['ID']}"):
                            delete_response = requests.delete(
                                f"{API_URL}/documents/{row['ID']}",
                                headers={"Authorization": f"Bearer {st.session_state.token}"}
                            )
                            
                            if delete_response.status_code == 200:
                                st.success("Document deleted!")
                                st.rerun()
                            else:
                                st.error("Error deleting document")
                    st.divider()
        else:
            st.error(f"Error loading documents: {response.json().get('detail', 'Unknown error')}")
    except Exception as e:
        st.error(f"Error: {str(e)}")

def display_chat():
    st.header("Board Discussion")
    
    # Advisor selection
    st.subheader("Select Advisors")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        legal_selected = st.checkbox("Legal", value="legal" in st.session_state.selected_advisors, key="legal_advisor_cb")
    with col2:
        financial_selected = st.checkbox("Financial", value="financial" in st.session_state.selected_advisors, key="financial_advisor_cb")
    with col3:
        tech_selected = st.checkbox("Technology", value="technology" in st.session_state.selected_advisors, key="tech_advisor_cb")
    
    # Update selected advisors
    selected_advisors = []
    if legal_selected:
        selected_advisors.append("legal")
    if financial_selected:
        selected_advisors.append("financial")
    if tech_selected:
        selected_advisors.append("technology")
    
    st.session_state.selected_advisors = selected_advisors
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    prompt = st.chat_input("Message the board...")
    if prompt and selected_advisors:  # Only proceed if we have a prompt and selected advisors
        # Add user message to chat history
        st.session_state.chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        try:
            response = requests.post(
                f"{API_URL}/advisors/analyze",
                json={
                    "topic": prompt,
                    "advisor_roles": selected_advisors
                },
                headers={"Authorization": f"Bearer {st.session_state.token}"},
                stream=True  # Enable streaming
            )
            
            if response.status_code == 200:
                # Create a placeholder for the streaming response
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    try:
                        # Process the streaming response
                        for chunk in response.iter_content(chunk_size=1024, decode_unicode=True):
                            if chunk:
                                # Decode the chunk if it's bytes
                                if isinstance(chunk, bytes):
                                    chunk = chunk.decode('utf-8')
                                full_response += chunk
                                # Update the message placeholder with the accumulated response
                                message_placeholder.markdown(full_response)
                    except Exception as stream_error:
                        st.error(f"Error processing stream: {str(stream_error)}")
                        st.error(f"Response headers: {response.headers}")
                
                # Add AI response to chat history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": full_response
                })
            else:
                error_detail = "Unknown error"
                try:
                    error_detail = response.json().get('detail', 'No detail provided')
                except Exception as json_error:
                    error_detail = f"Could not parse error response: {str(json_error)}"
                st.error(f"Error getting response (Status {response.status_code}): {error_detail}")
                st.error("Please make sure you have selected at least one advisor and entered a message.")
        except Exception as e:
            st.error(f"Request error: {str(e)}")
            import traceback
            st.error(f"Traceback: {traceback.format_exc()}")
        
        st.rerun()

def main():
    initialize_session()  # Initialize session state first
    st.title("BoardAI")
    
    # Authentication section in sidebar
    st.sidebar.header("Authentication")
    
    if not st.session_state.token:
        # Login form
        with st.sidebar.form("login_form"):
            st.subheader("Login")
            st.text_input("Email", key="email")
            st.text_input("Password", type="password", key="password")
            
            col1, col2 = st.columns(2)
            with col1:
                login_submitted = st.form_submit_button("Login")
            
            with col2:
                show_register = st.form_submit_button("Register")
        
        if login_submitted:
            try:
                response = requests.post(
                    f"{API_URL}/auth/token",
                    data={
                        "username": st.session_state.email,
                        "password": st.session_state.password
                    }
                )
                
                if response.status_code == 200:
                    st.session_state.token = response.json()["access_token"]
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Login failed")
            except Exception as e:
                st.error(f"Login failed: {str(e)}")
        
        if show_register:
            # Show registration form
            with st.sidebar.form("register_form"):
                st.subheader("Register")
                st.text_input("Full Name", key="full_name")
                st.text_input("Email", key="reg_email")
                st.text_input("Password", type="password", key="reg_password")
                st.text_input("Organization Name", key="org_name")
                
                register_submitted = st.form_submit_button("Register")
            
            if register_submitted:
                try:
                    response = requests.post(
                        f"{API_URL}/auth/register",
                        json={
                            "email": st.session_state.reg_email,
                            "password": st.session_state.reg_password,
                            "full_name": st.session_state.full_name,
                            "organization_name": st.session_state.org_name
                        }
                    )
                    
                    if response.status_code == 200:
                        st.success("Registration successful! Please login.")
                        st.rerun()
                    else:
                        st.error(f"Registration failed: {response.json()['detail']}")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")
    else:
        # Show logout button
        if st.sidebar.button("Logout"):
            st.session_state.token = None
            st.session_state.email = ""
            st.session_state.password = ""
            st.session_state.chat_history = []
            st.rerun()
        
        # Main content when logged in
        tab1, tab2 = st.tabs(["Documents", "Chat"])
        
        with tab1:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.header("Document Upload")
            with col2:
                st.button("Upload Document", on_click=show_upload_modal, key="show_upload_modal_btn")
            
            # Document upload modal
            if st.session_state.show_upload_modal:
                with st.container():
                    st.subheader("Upload Company Document")
                    
                    uploaded_files = st.file_uploader(
                        "Drag and drop files here", 
                        accept_multiple_files=True,
                        type=["txt", "pdf"]
                    )
                    
                    doc_type = st.selectbox(
                        "Document Type",
                        ["Financial Report", "Legal Document", "Technical Document", "Meeting Minutes", "Other"]
                    )
                    
                    col3, col4 = st.columns([1, 1])
                    with col3:
                        if st.button("Upload Document", key="upload_document_btn"):
                            if uploaded_files:
                                try:
                                    files = [("files", (file.name, file.getvalue(), file.type)) for file in uploaded_files]
                                    
                                    response = requests.post(
                                        f"{API_URL}/documents/upload",
                                        files=files,
                                        data={
                                            "type": doc_type
                                        },
                                        headers={"Authorization": f"Bearer {st.session_state.token}"}
                                    )
                                    
                                    if response.status_code == 200:
                                        st.success(f"{len(uploaded_files)} document(s) uploaded successfully!")
                                        st.session_state.show_upload_modal = False
                                        st.rerun()
                                    else:
                                        st.error(f"Error uploading document: {response.json()['detail']}")
                                except Exception as e:
                                    st.error(f"Error: {str(e)}")
                            else:
                                st.error("Please select at least one file to upload")
                    
                    with col4:
                        if st.button("Cancel", key="cancel_upload_btn"):
                            st.session_state.show_upload_modal = False
                            st.rerun()
            
            st.markdown("---")
            
            # Document management section
            display_document_management()
        
        with tab2:
            display_chat()

if __name__ == "__main__":
    main()