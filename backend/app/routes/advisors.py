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
import traceback

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
        # Validate request
        if not request.advisor_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one advisor role must be specified"
            )
        
        if not request.topic:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Topic cannot be empty"
            )

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
                detail=f"Invalid advisor roles: {', '.join(invalid_roles)}"
            )

        # Create conversation record
        conversation = Conversation(
            topic=request.topic,
            organization_id=current_user.organization_id,
            discussion={"responses": {}, "complete": False}
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
                    try:
                        advisor = advisors[role]
                        response_header = f"### {role.upper()} ADVISOR:\n\n"
                        yield response_header.encode('utf-8')
                        
                        full_response = ""
                        async for chunk in advisor.get_analysis(
                            request.topic, 
                            async_db,
                            async_user.organization_id
                        ):
                            if chunk:
                                chunk_bytes = chunk.encode('utf-8')
                                yield chunk_bytes
                                full_response += chunk
                        
                        yield b"\n\n"
                        full_responses[role] = full_response

                        # Update conversation in database after each advisor
                        async_conversation.discussion["responses"] = full_responses
                        async_db.commit()

                    except Exception as advisor_error:
                        error_msg = f"\nError from {role} advisor: {str(advisor_error)}\n"
                        print(f"Advisor error: {error_msg}\n{traceback.format_exc()}")
                        yield error_msg.encode('utf-8')
                        full_responses[role] = f"Error: {str(advisor_error)}"
                        continue

            except Exception as e:
                error_msg = f"Error generating response: {str(e)}\n{traceback.format_exc()}"
                print(error_msg)
                yield error_msg.encode('utf-8')
            finally:
                try:
                    # Mark conversation as complete and close session
                    if 'async_conversation' in locals():
                        async_conversation.discussion["complete"] = True
                        async_db.commit()
                except Exception as cleanup_error:
                    print(f"Error during cleanup: {str(cleanup_error)}")
                finally:
                    async_db.close()

        return StreamingResponse(
            generate_response(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions
        raise http_ex
    except Exception as e:
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        print(error_detail)  # Log the full error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
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