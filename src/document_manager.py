import json
import os
from typing import List, Dict
import PyPDF2
from datetime import datetime

class DocumentManager:
    def __init__(self, storage_path: str = "data/memory/documents"):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)

    def get_all_documents(self) -> List[Dict]:
        """Retrieve all stored documents with metadata"""
        documents = []
        
        if not os.path.exists(self.storage_path):
            return documents
            
        for filename in os.listdir(self.storage_path):
            if not filename.endswith('.json'):
                continue
                
            file_path = os.path.join(self.storage_path, filename)
            try:
                with open(file_path, 'r') as f:
                    doc = json.load(f)
                    # Add file identifier
                    doc['id'] = filename[:-5]  # Remove .json extension
                    documents.append(doc)
            except Exception as e:
                print(f"Error loading document {filename}: {str(e)}")
                
        # Sort by timestamp, newest first
        return sorted(documents, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document from storage"""
        file_path = os.path.join(self.storage_path, f"{doc_id}.json")
        
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return True
            except Exception as e:
                print(f"Error deleting document: {str(e)}")
                return False
        return False
    
    def get_document_content(self, doc_id: str) -> str:
        """Retrieve full content of a specific document"""
        file_path = os.path.join(self.storage_path, f"{doc_id}.json")
        
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    doc = json.load(f)
                    return doc.get('content', '')
            except Exception as e:
                print(f"Error reading document: {str(e)}")
                return ''
        return ''
        
    def add_document(self, file_path: str, doc_type: str, metadata: Dict = None):
        """Process and store a new document"""
        timestamp = datetime.now().isoformat()
        
        if file_path.endswith('.pdf'):
            content = self._process_pdf(file_path)
        else:
            with open(file_path, 'r') as f:
                content = f.read()
                
        document = {
            "timestamp": timestamp,
            "type": doc_type,
            "content": content,
            "metadata": metadata or {}
        }
        
        # Store document content and metadata
        doc_id = f"{doc_type}_{timestamp}"
        with open(f"{self.storage_path}/{doc_id}.json", 'w') as f:
            json.dump(document, f, indent=2)
            
        return doc_id
        
    def _process_pdf(self, file_path: str) -> str:
        """Extract text content from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = []
                for page in pdf_reader.pages:
                    try:
                        text.append(page.extract_text())
                    except Exception as e:
                        print(f"Error extracting text from page: {str(e)}")
                return "\n".join(text)
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}")
        
    def get_relevant_documents(self, query: str, doc_type: str = None) -> List[Dict]:
        """Retrieve relevant documents based on query and type"""
        documents = []
        for filename in os.listdir(self.storage_path):
            if filename.endswith('.json'):
                with open(f"{self.storage_path}/{filename}", 'r') as f:
                    doc = json.load(f)
                    if doc_type is None or doc["type"] == doc_type:
                        documents.append(doc)
        return documents