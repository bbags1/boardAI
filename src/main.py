import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict

class AIAdvisor:
    def __init__(self, role: str):
        load_dotenv()
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.model = genai.GenerativeModel('gemini-1.5-flash')  # Using flash model for streaming
        self.role = role
        self.personality = self.get_personality(role)

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
        
    def get_individual_analysis(self, topic: str) -> genai.types.GenerateContentResponse:
        """Stream analysis from this advisor"""
        prompt = f"""
        As a {self.role} advisor with the following context:
        {self.personality}
        
        Analyze this topic:
        {topic}
        
        Provide your perspective considering your specific expertise and priorities.
        """
        
        return self.model.generate_content(prompt, stream=True)

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