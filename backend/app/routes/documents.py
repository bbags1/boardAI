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
        document = Document(
            type=type,
            content=content_str,
            doc_metadata={
                "filename": file.filename,
                "content_type": file.content_type
            },
            organization_id=current_user.organization_id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
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
    return documents

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
        
    return document

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