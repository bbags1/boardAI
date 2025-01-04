import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict, Union
from memory import ConversationMemory
from document_manager import DocumentManager

class AIAdvisor:
    def __init__(self, role: str):
        load_dotenv()
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Using flash model for streaming
        self.role = role
        self.personality = self.get_personality(role)
        self.memory = ConversationMemory()
        self.document_manager = DocumentManager()

    def get_personality(self, role: str) -> str:
        """Define the personality and expertise for each advisor role"""
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
        
    def get_individual_analysis(self, input_data: Union[str, bytes], topic: str = None) -> genai.types.GenerateContentResponse:
        """Stream analysis with context from memory and documents"""
        try:
            # Get relevant history and documents
            try:
                past_conversations = self.memory.get_relevant_history(topic or input_data)
            except Exception as e:
                print(f"Error retrieving conversation history: {str(e)}")
                past_conversations = []

            try:
                relevant_docs = self.document_manager.get_relevant_documents(topic or input_data)
            except Exception as e:
                print(f"Error retrieving documents: {str(e)}")
                relevant_docs = []
            
            # Build context
            context = f"""
            As a {self.role} advisor with the following context:
            {self.personality}
            
            {self._format_history(past_conversations) if past_conversations else ""}
            
            {self._format_documents(relevant_docs) if relevant_docs else ""}
            """
            
            # Handle audio input
            if isinstance(input_data, str) and input_data.endswith('.wav'):
                try:
                    with open(input_data, 'rb') as audio:
                        audio_data = audio.read()
                        response = self.model.generate_content([
                            context,
                            audio_data
                        ], stream=True)
                    # Clean up temp file after use
                    os.remove(input_data)
                    return response
                except Exception as e:
                    print(f"Error processing audio file: {str(e)}")
                    # Fall back to default response if audio processing fails
                    return self.model.generate_content(
                        context + "\nError processing audio input. Please provide a text response.",
                        stream=True
                    )
            else:
                # Regular text input
                return self.model.generate_content(
                    context + f"\nCurrent topic:\n{input_data}",
                    stream=True
                )
                
        except Exception as e:
            print(f"Error in get_individual_analysis: {str(e)}")
            return self.model.generate_content(f"""
            As a {self.role} advisor:
            {self.personality}
            
            Current topic:
            {topic or input_data}
            
            Provide your perspective based on your expertise and priorities.
            """, stream=True)

    def _format_history(self, conversations: List[Dict]) -> str:
        """Format conversation history for context"""
        if not conversations:
            return ""
            
        history = []
        for conv in conversations:
            try:
                history.append(f"""
                Date: {conv['timestamp']}
                Topic: {conv['topic']}
                Key Points: {conv['discussion'].get('synthesis', 'No synthesis available')}
                """)
            except Exception as e:
                print(f"Error formatting conversation: {str(e)}")
                continue
        return "Relevant past discussions:\n" + "\n".join(history) if history else ""
        
    def _format_documents(self, documents: List[Dict]) -> str:
        """Format relevant documents for context"""
        if not documents:
            return ""
            
        docs = []
        for doc in documents:
            try:
                docs.append(f"""
                Type: {doc['type']}
                Date: {doc['timestamp']}
                Content: {doc['content'][:500]}... # Truncated for context
                """)
            except Exception as e:
                print(f"Error formatting document: {str(e)}")
                continue
        return "Relevant company documents:\n" + "\n".join(docs) if docs else ""

class AdvisoryBoard:
    def __init__(self):
        self.advisors: Dict[str, AIAdvisor] = {}
        
    def add_advisor(self, role: str):
        self.advisors[role] = AIAdvisor(role)
        
    def get_individual_analysis(self, topic: str, role: str):
        """Stream analysis from a specific advisor"""
        advisor = self.advisors.get(role)
        if not advisor:
            yield f"No advisor found for role: {role}"
            return
            
        response = advisor.get_individual_analysis(topic)
        for chunk in response:
            yield chunk.text
        
    def facilitate_discussion(self, topic: str, participating_roles: List[str]):
        """Stream a discussion between multiple advisors"""
        if not all(role in self.advisors for role in participating_roles):
            yield "Error: Some specified advisors are not on the board"
            return
            
        # Collect initial perspectives
        discussion = []
        for role in participating_roles:
            response = self.advisors[role].get_individual_analysis(topic)
            analysis = "".join(chunk.text for chunk in response)
            discussion.append(f"{role.upper()} ADVISOR:\n{analysis}\n")
            yield f"{role.upper()} ADVISOR has provided their analysis.\n"
            
        # Facilitate debate and synthesis
        debate_prompt = f"""
        The following advisors have provided their perspectives on: {topic}
        
        Previous discussion:
        {''.join(discussion)}
        
        As a neutral facilitator:
        1. Identify points of agreement and disagreement
        2. Highlight potential conflicts between different priorities
        3. Suggest a balanced approach that considers all perspectives
        4. Provide final recommendations
        """
        
        synthesis = self.advisors[participating_roles[0]].model.generate_content(debate_prompt, stream=True)
        yield "\nSYNTHESIS AND RECOMMENDATIONS:\n"
        for chunk in synthesis:
            yield chunk.text