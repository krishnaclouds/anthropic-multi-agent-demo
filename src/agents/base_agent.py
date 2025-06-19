from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
from enum import Enum

class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    RESEARCHER = "researcher"
    CITATION = "citation"
    WEB_SEARCHER = "web_searcher"

@dataclass
class Message:
    content: str
    sender: str
    message_type: str
    metadata: Optional[Dict[str, Any]] = None

@dataclass
class Task:
    id: str
    description: str
    status: str = "pending"
    result: Optional[Any] = None
    assigned_agent: Optional[str] = None

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: AgentType, anthropic_client):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.client = anthropic_client
        self.memory: List[Message] = []
        
    @abstractmethod
    async def process_task(self, task: Task) -> Any:
        pass
    
    def add_to_memory(self, message: Message):
        self.memory.append(message)
    
    def get_memory_context(self, limit: int = 10) -> str:
        recent_messages = self.memory[-limit:]
        return "\n".join([f"{msg.sender}: {msg.content}" for msg in recent_messages])