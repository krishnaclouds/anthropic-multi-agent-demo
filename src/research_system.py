import asyncio
import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import anthropic

from .agents.orchestrator import OrchestratorAgent
from .agents.research_agent import ResearchAgent
from .agents.web_search_agent import WebSearchAgent
from .agents.citation_agent import CitationAgent
from .coordination.memory_manager import MemoryManager
from .coordination.task_coordinator import TaskCoordinator

class MultiAgentResearchSystem:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-5-sonnet-20241022"):
        load_dotenv()
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model_name = model_name
        
        self.memory_manager = MemoryManager()
        self.task_coordinator = TaskCoordinator()
        
        self.orchestrator = OrchestratorAgent(self.client)
        self.citation_agent = CitationAgent("citation_agent", self.client)
        
        self.research_session_id = None
        
    async def conduct_research(self, query: str, enable_citations: bool = True, 
                             research_depth: str = "comprehensive") -> Dict[str, Any]:
        
        self.research_session_id = f"session_{len(self.memory_manager.memory_store) + 1}"
        
        self.memory_manager.store_memory(
            content=f"Research query: {query}",
            agent_id="system",
            entry_type="query_start",
            metadata={"research_depth": research_depth}
        )
        
        try:
            research_results = await self.orchestrator.research_query(query)
            
            if enable_citations and research_results.get("final_report"):
                citation_task = self.task_coordinator.create_task(
                    description=research_results["final_report"],
                    priority="high"
                )
                
                citation_result = await self.task_coordinator.execute_task(
                    citation_task, self.citation_agent
                )
                
                if citation_result.status.value == "completed":
                    research_results["cited_report"] = citation_result.result.get("attributed_content")
                    research_results["citations"] = citation_result.result.get("citations", [])
            
            self.memory_manager.store_memory(
                content=f"Research completed for: {query}",
                agent_id="system",
                entry_type="query_complete",
                metadata={"results_summary": research_results.get("final_report", "")[:200]}
            )
            
            return {
                "query": query,
                "session_id": self.research_session_id,
                "results": research_results,
                "coordination_summary": self.task_coordinator.get_coordination_summary(),
                "memory_summary": self.memory_manager.get_memory_summary("system")
            }
            
        except Exception as e:
            self.memory_manager.store_memory(
                content=f"Research failed for: {query}. Error: {str(e)}",
                agent_id="system",
                entry_type="query_error"
            )
            raise
    
    async def follow_up_question(self, question: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        if session_id:
            self.research_session_id = session_id
        
        context_memories = self.memory_manager.search_memories(
            query=question,
            agent_id="system"
        )
        
        context = "\n".join([mem.content for mem in context_memories[:3]])
        
        enhanced_query = f"""
        Follow-up question: {question}
        
        Previous research context:
        {context}
        
        Please provide a focused response building on the previous research.
        """
        
        return await self.conduct_research(enhanced_query, enable_citations=True)
    
    def get_research_history(self) -> Dict[str, Any]:
        return {
            "total_sessions": len(set(mem.metadata.get("session_id", "") 
                                   for mem in self.memory_manager.memory_store.values() 
                                   if mem.metadata)),
            "recent_queries": [
                mem.content for mem in self.memory_manager.search_memories("Research query:")[:5]
            ],
            "system_summary": self.memory_manager.get_memory_summary("system")
        }
    
    def export_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        session_id = session_id or self.research_session_id
        
        return {
            "session_id": session_id,
            "coordination_data": self.task_coordinator.get_coordination_summary(),
            "memory_export": self.memory_manager.export_memories("system"),
            "export_timestamp": self.memory_manager.export_memories()["export_timestamp"]
        }