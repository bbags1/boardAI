from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, AsyncGenerator
from ..core.advisors import AIAdvisor
from ..schemas.advisors import ConversationCreate, ConversationResponse
from ..models.conversation import Conversation
from ..models.user import User
from ..db.session import get_db, SessionLocal
from ..core.security import get_current_user
from ..models.personality import Personality
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

# Initialize advisors
ADVISORS = {
    "legal": AIAdvisor("legal"),
    "financial": AIAdvisor("financial"),
    "technology": AIAdvisor("technology")
}

@router.post("/analyze")
async def get_analysis(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analysis from specified advisors"""
    try:
        # Get custom personalities for the organization
        custom_personalities = db.query(Personality).filter(
            Personality.organization_id == current_user.organization_id
        ).all()
        
        # Create dynamic advisors dictionary combining default and custom
        advisors = {
            "legal": AIAdvisor("legal", db, current_user.organization_id),
            "financial": AIAdvisor("financial", db, current_user.organization_id),
            "technology": AIAdvisor("technology", db, current_user.organization_id)
        }
        
        # Add custom personalities to advisors
        for personality in custom_personalities:
            advisors[personality.name] = AIAdvisor(personality.name, db, current_user.organization_id)
        
        # Validate advisor roles
        invalid_roles = [role for role in request.advisor_roles if role not in advisors]
        if invalid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid advisor roles: {invalid_roles}"
            )

        # Create conversation record
        conversation = Conversation(
            topic=request.topic,
            organization_id=current_user.organization_id,
            discussion={"responses": {}}
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        async def generate_response():
            # Create a new session for the streaming context
            async_db = SessionLocal()
            try:
                # Get fresh instances from the new session
                async_conversation = async_db.merge(conversation)
                async_user = async_db.merge(current_user)
                
                full_responses = {}
                for role in request.advisor_roles:
                    advisor = advisors[role]
                    response_header = f"### {role.upper()} ADVISOR:\n\n"
                    yield response_header.encode('utf-8')
                    
                    full_response = ""
                    async for chunk in advisor.get_analysis(
                        request.topic, 
                        async_db,  # Pass the new session
                        async_user.organization_id
                    ):
                        if chunk:
                            yield chunk.encode('utf-8')
                            full_response += chunk
                    
                    yield b"\n\n"
                    full_responses[role] = full_response

                    # Update conversation in database
                    async_conversation.discussion["responses"] = full_responses
                    async_db.commit()

            except Exception as e:
                print(f"Error generating response: {str(e)}")
                yield f"Error: {str(e)}".encode('utf-8')
            finally:
                # Mark conversation as complete and close session
                if 'async_conversation' in locals():
                    async_conversation.discussion["complete"] = True
                    async_db.commit()
                async_db.close()

        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error: {str(e)}"
        )

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get conversation history for the organization"""
    conversations = (
        db.query(Conversation)
        .filter(Conversation.organization_id == current_user.organization_id)
        .order_by(Conversation.timestamp.desc())
        .all()
    )
    return conversations

@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific conversation"""
    conversation = (
        db.query(Conversation)
        .filter(
            Conversation.id == conversation_id,
            Conversation.organization_id == current_user.organization_id
        )
        .first()
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )
        
    return conversation