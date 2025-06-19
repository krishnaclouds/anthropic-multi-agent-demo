from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json
import hashlib
from datetime import datetime

@dataclass
class MemoryEntry:
    id: str
    content: str
    timestamp: datetime
    agent_id: str
    entry_type: str
    metadata: Optional[Dict[str, Any]] = None

class MemoryManager:
    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.memory_store: Dict[str, MemoryEntry] = {}
        self.agent_memories: Dict[str, List[str]] = {}
        
    def store_memory(self, content: str, agent_id: str, entry_type: str = "general", 
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        memory_id = self._generate_memory_id(content, agent_id)
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            agent_id=agent_id,
            entry_type=entry_type,
            metadata=metadata or {}
        )
        
        self.memory_store[memory_id] = entry
        
        if agent_id not in self.agent_memories:
            self.agent_memories[agent_id] = []
        self.agent_memories[agent_id].append(memory_id)
        
        self._enforce_memory_limits()
        return memory_id
    
    def retrieve_agent_memories(self, agent_id: str, limit: int = 10) -> List[MemoryEntry]:
        if agent_id not in self.agent_memories:
            return []
        
        memory_ids = self.agent_memories[agent_id][-limit:]
        return [self.memory_store[mid] for mid in memory_ids if mid in self.memory_store]
    
    def search_memories(self, query: str, agent_id: Optional[str] = None) -> List[MemoryEntry]:
        results = []
        search_pool = self.memory_store.values()
        
        if agent_id:
            memory_ids = self.agent_memories.get(agent_id, [])
            search_pool = [self.memory_store[mid] for mid in memory_ids if mid in self.memory_store]
        
        query_lower = query.lower()
        for entry in search_pool:
            if query_lower in entry.content.lower():
                results.append(entry)
        
        return sorted(results, key=lambda x: x.timestamp, reverse=True)
    
    def get_memory_summary(self, agent_id: str) -> Dict[str, Any]:
        memories = self.retrieve_agent_memories(agent_id, limit=50)
        
        if not memories:
            return {"total_memories": 0, "summary": "No memories stored"}
        
        return {
            "total_memories": len(self.agent_memories.get(agent_id, [])),
            "recent_memories": len(memories),
            "memory_types": list(set(m.entry_type for m in memories)),
            "date_range": {
                "earliest": min(m.timestamp for m in memories).isoformat(),
                "latest": max(m.timestamp for m in memories).isoformat()
            }
        }
    
    def _generate_memory_id(self, content: str, agent_id: str) -> str:
        timestamp = datetime.now().isoformat()
        hash_input = f"{content}_{agent_id}_{timestamp}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:12]
    
    def _enforce_memory_limits(self):
        if len(self.memory_store) > self.max_entries:
            oldest_entries = sorted(self.memory_store.values(), key=lambda x: x.timestamp)
            entries_to_remove = oldest_entries[:len(self.memory_store) - self.max_entries]
            
            for entry in entries_to_remove:
                del self.memory_store[entry.id]
                if entry.agent_id in self.agent_memories:
                    if entry.id in self.agent_memories[entry.agent_id]:
                        self.agent_memories[entry.agent_id].remove(entry.id)
    
    def export_memories(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        if agent_id:
            memories = self.retrieve_agent_memories(agent_id, limit=1000)
        else:
            memories = list(self.memory_store.values())
        
        return {
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(memories),
            "agent_id": agent_id,
            "memories": [asdict(memory) for memory in memories]
        }