import os
from typing import List, Dict, AsyncGenerator, Union
import google.generativeai as genai
from ..models.conversation import Conversation
from ..models.document import Document
from sqlalchemy.orm import Session
from ..core.config import settings


class ConversationMemory:
    def get_relevant_history(self, db: Session, org_id: int, topic: str, limit: int = 5) -> List[Conversation]:
        """Get semantically relevant conversation history"""
        # TODO: Implement semantic search here
        return (
            db.query(Conversation)
            .filter(Conversation.organization_id == org_id)
            .order_by(Conversation.timestamp.desc())
            .limit(limit)
            .all()
        )

class DocumentManager:
    def get_relevant_documents(self, db: Session, org_id: int, topic: str, limit: int = 3) -> List[Document]:
        """Get semantically relevant documents"""
        # TODO: Implement semantic search here
        return (
            db.query(Document)
            .filter(Document.organization_id == org_id)
            .order_by(Document.timestamp.desc())
            .limit(limit)
            .all()
        )

class AIAdvisor:
    def __init__(self, role: str):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.role = role
        self.personality = self.get_personality(role)
        self.memory = ConversationMemory()
        self.document_manager = DocumentManager()

    def get_personality(self, role: str) -> str:
        # Copy the personality definitions from the original AIAdvisor class
        personalities = {
            "legal": """
            You are a seasoned Legal Advisor with expertise in corporate law, compliance, and risk management.
            Your priorities are:
            1. Ensuring legal compliance
            2. Protecting the company from legal risks
            3. Analyzing regulatory implications
            4. Structuring deals and partnerships legally
            5. Maintaining ethical standards
            """,
            
            "financial": """
            You are an experienced Financial Advisor with expertise in corporate finance and investment strategy.
            Your priorities are:
            1. Financial performance analysis
            2. ROI optimization
            3. Risk management
            4. Market analysis
            5. Capital allocation
            """,
            
            "technology": """
            You are a Technology Strategy Advisor with expertise in digital transformation and tech trends.
            Your priorities are:
            1. Technical feasibility assessment
            2. Technology stack optimization
            3. Digital transformation strategy
            4. Cybersecurity considerations
            5. Innovation opportunities
            """
        }
        return personalities.get(role, "Generic board member personality")

    async def get_analysis(
        self, 
        input_data: Union[str, bytes], 
        db: Session, 
        org_id: int
    ) -> AsyncGenerator[str, None]:
        try:
            # Handle audio input if bytes
            if isinstance(input_data, bytes):
                topic = await self._process_audio(input_data)
            else:
                topic = input_data

            # Get relevant history and documents using managers
            past_conversations = self.memory.get_relevant_history(db, org_id, topic)
            relevant_docs = self.document_manager.get_relevant_documents(db, org_id, topic)

            # Build context
            context = f"""
            As a {self.role} advisor with the following context:
            {self.personality}

            {self._format_history(past_conversations)}
            {self._format_documents(relevant_docs)}

            Current topic:
            {topic}

            Provide your perspective based on your expertise and priorities.
            """

            response = self.model.generate_content(context, stream=True)
            for chunk in response:
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            yield f"Error from {self.role} advisor: {str(e)}"

    async def _process_audio(self, audio_data: bytes) -> str:
        """Process audio input to text using Gemini's multimodal capabilities"""
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_audio:
                temp_audio.write(audio_data)
                temp_path = temp_audio.name

            try:
                with open(temp_path, 'rb') as audio:
                    response = self.model.generate_content([audio.read()])
                return response.text
            finally:
                os.remove(temp_path)
        except Exception as e:
            raise Exception(f"Error processing audio: {str(e)}")

    def get_personality(self, role: str) -> str:
        # Existing personality definitions remain the same
        personalities = {
            "legal": """...""",  # Your existing legal personality
            "financial": """...""",  # Your existing financial personality
            "technology": """..."""  # Your existing technology personality
        }
        return personalities.get(role, "Generic board member personality")

    def _format_history(self, conversations: List[Conversation]) -> str:
        # Existing _format_history implementation remains the same
        history = []
        for conv in conversations:
            try:
                history.append(f"""
                Date: {conv.timestamp}
                Topic: {conv.topic}
                Key Points: {conv.discussion.get('synthesis', 'No synthesis available')}
                """)
            except Exception as e:
                print(f"Error formatting conversation: {str(e)}")
                continue
        return "Relevant past discussions:\n" + "\n".join(history) if history else ""

    def _format_documents(self, documents: List[Document]) -> str:
        # Existing _format_documents implementation remains the same
        docs = []
        for doc in documents:
            try:
                docs.append(f"""
                Type: {doc.type}
                Date: {doc.timestamp}
                Content: {doc.content[:500]}... # Truncated for context
                """)
            except Exception as e:
                print(f"Error formatting document: {str(e)}")
                continue
        return "Relevant company documents:\n" + "\n".join(docs) if docs else ""