import json
from typing import List, Dict
import os
from datetime import datetime

class ConversationMemory:
    def __init__(self, storage_path: str = "data/memory"):
        self.storage_path = storage_path
        self.ensure_storage_exists()
        
    def ensure_storage_exists(self):
        """Create storage directories if they don't exist"""
        os.makedirs(f"{self.storage_path}/conversations", exist_ok=True)
        os.makedirs(f"{self.storage_path}/documents", exist_ok=True)
        
    def save_conversation(self, topic: str, advisors: List[str], discussion: Dict):
        """Save a conversation to persistent storage"""
        timestamp = datetime.now().isoformat()
        conversation = {
            "timestamp": timestamp,
            "topic": topic,
            "advisors": advisors,
            "discussion": discussion
        }
        
        filename = f"{self.storage_path}/conversations/{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(conversation, f, indent=2)
            
    def get_relevant_history(self, topic: str, limit: int = 5) -> List[Dict]:
        """Retrieve relevant past conversations based on topic"""
        conversations = []
        conv_dir = f"{self.storage_path}/conversations"
        
        if not os.path.exists(conv_dir):
            return conversations
            
        for filename in sorted(os.listdir(conv_dir), reverse=True):
            if filename.endswith('.json'):
                with open(f"{conv_dir}/{filename}", 'r') as f:
                    conv = json.load(f)
                    conversations.append(conv)
                    
                if len(conversations) >= limit:
                    break
                    
        return conversations