from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..schemas.advisors import DocumentCreate, DocumentResponse
from ..models.document import Document
from ..models.user import User
from ..db.session import get_db
from ..core.security import get_current_user
import json

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload a new document"""
    try:
        content = await file.read()
        content_str = ""
        
        # Determine content type from filename if not set
        if not file.content_type:
            file.content_type = "application/pdf" if file.filename.lower().endswith('.pdf') else "text/plain"
        
        if file.content_type == 'text/plain':
            content_str = content.decode('utf-8')
        elif file.content_type == 'application/pdf':
            import io
            import pdfplumber
            
            pdf_file = io.BytesIO(content)
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    for page in pdf.pages:
                        content_str += page.extract_text() + "\n"
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error processing PDF: {str(e)}"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}"
            )

        # Create document record
        doc_metadata = {
            "filename": file.filename,
            "content_type": file.content_type
        }
        
        document = Document(
            type=type,
            content=content_str,
            doc_metadata=doc_metadata,
            organization_id=current_user.organization_id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Create a DocumentResponse object manually to ensure proper conversion
        doc_dict = {
            "id": document.id,
            "type": document.type,
            "content": document.content,
            "doc_metadata": document.doc_metadata_dict,  # Use the property method
            "timestamp": document.timestamp,
            "organization_id": document.organization_id
        }
        
        return DocumentResponse(**doc_dict)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not process document: {str(e)}"
        )

@router.get("/list", response_model=List[DocumentResponse])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for the organization"""
    documents = (
        db.query(Document)
        .filter(Document.organization_id == current_user.organization_id)
        .order_by(Document.timestamp.desc())
        .all()
    )
    
    # Create DocumentResponse objects manually to ensure proper conversion
    document_responses = []
    for doc in documents:
        # Create a dictionary representation of the document
        doc_dict = {
            "id": doc.id,
            "type": doc.type,
            "content": doc.content,
            "doc_metadata": doc.doc_metadata_dict,  # Use the property method
            "timestamp": doc.timestamp,
            "organization_id": doc.organization_id
        }
        document_responses.append(DocumentResponse(**doc_dict))
    
    return document_responses

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document"""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user.organization_id
        )
        .first()
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Create a DocumentResponse object manually to ensure proper conversion
    doc_dict = {
        "id": document.id,
        "type": document.type,
        "content": document.content,
        "doc_metadata": document.doc_metadata_dict,  # Use the property method
        "timestamp": document.timestamp,
        "organization_id": document.organization_id
    }
    
    return DocumentResponse(**doc_dict)

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a document"""
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.organization_id == current_user.organization_id
        )
        .first()
    )
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
        
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}