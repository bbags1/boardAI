from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from ..schemas.advisors import DocumentCreate, DocumentResponse
from ..models.document import Document
from ..models.user import User
from ..db.session import get_db
from ..core.security import get_current_user
import json
import io
import pdfplumber
import os
import tempfile
from datetime import datetime
from ..api.deps import get_current_organization

router = APIRouter()

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    files: List[UploadFile] = File(...),
    type: str = Form(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    current_org = Depends(get_current_organization)
):
    """Upload multiple documents and store them in the database"""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    uploaded_documents = []
    
    for file in files:
        # Determine content type
        content_type = file.content_type
        
        # Read content from file
        content = ""
        if content_type == "application/pdf":
            # Extract text from PDF
            with tempfile.NamedTemporaryFile(delete=False) as temp:
                temp.write(await file.read())
                temp_path = temp.name
            
            try:
                with pdfplumber.open(temp_path) as pdf:
                    content = "\n".join([page.extract_text() or "" for page in pdf.pages])
                os.unlink(temp_path)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")
        else:
            # Read text file
            content = (await file.read()).decode("utf-8")
        
        # Create document metadata
        doc_metadata = {
            "filename": file.filename,
            "content_type": content_type,
            "size": file.size,
            "upload_date": datetime.now().isoformat()
        }
        
        # Create document in database
        db_document = Document(
            type=type,
            content=content,
            doc_metadata=doc_metadata,
            organization_id=current_org.id
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        # Convert to Pydantic model
        doc_response = DocumentResponse(
            id=db_document.id,
            type=db_document.type,
            content=db_document.content,
            doc_metadata=db_document.doc_metadata_dict,
            timestamp=db_document.timestamp,
            organization_id=db_document.organization_id
        )
        uploaded_documents.append(doc_response)
    
    return uploaded_documents

@router.get("/list", response_model=List[DocumentResponse])
def list_documents(
    db: Session = Depends(get_db),
    current_org = Depends(get_current_organization)
):
    """List all documents for the current organization"""
    documents = db.query(Document).filter(
        Document.organization_id == current_org.id
    ).all()
    
    # Convert to Pydantic models
    document_responses = []
    for doc in documents:
        document_responses.append(
            DocumentResponse(
                id=doc.id,
                type=doc.type,
                content=doc.content,
                doc_metadata=doc.doc_metadata_dict,
                timestamp=doc.timestamp,
                organization_id=doc.organization_id
            )
        )
    
    return document_responses

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_org = Depends(get_current_organization)
):
    """Get a specific document by ID"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == current_org.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Convert to Pydantic model
    return DocumentResponse(
        id=document.id,
        type=document.type,
        content=document.content,
        doc_metadata=document.doc_metadata_dict,
        timestamp=document.timestamp,
        organization_id=document.organization_id
    )

@router.get("/download/{document_id}")
def download_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_org = Depends(get_current_organization)
):
    """Download a document by ID"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == current_org.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Get metadata
    metadata = document.doc_metadata_dict
    filename = metadata.get("filename", f"document_{document_id}.txt")
    content_type = metadata.get("content_type", "text/plain")
    
    # Create file-like object
    file_obj = io.BytesIO(document.content.encode("utf-8"))
    
    # Return file for download
    return StreamingResponse(
        file_obj,
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_org = Depends(get_current_organization)
):
    """Delete a document by ID"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.organization_id == current_org.id
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}