import asyncio
from typing import List, Dict, Any
from .base_agent import BaseAgent, AgentType, Task, Message
from .research_agent import ResearchAgent
from .web_search_agent import WebSearchAgent
from .citation_agent import CitationAgent

class OrchestratorAgent(BaseAgent):
    def __init__(self, anthropic_client):
        super().__init__("orchestrator", AgentType.ORCHESTRATOR, anthropic_client)
        self.subagents: Dict[str, BaseAgent] = {}
        self.active_tasks: List[Task] = []
        
    async def research_query(self, query: str) -> Dict[str, Any]:
        await self._decompose_query(query)
        results = await self._execute_parallel_research()
        final_report = await self._synthesize_results(results)
        return final_report
    
    async def _decompose_query(self, query: str):
        prompt = f"""
        You are a research orchestrator. Break down this query into 3-5 specific research subtasks:
        Query: {query}
        
        Provide subtasks as a numbered list focusing on different aspects of the topic.
        Each subtask should be specific and actionable.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        subtasks = self._parse_subtasks(response.content[0].text)
        
        for i, subtask in enumerate(subtasks):
            task = Task(
                id=f"task_{i}",
                description=subtask,
                status="pending"
            )
            self.active_tasks.append(task)
    
    def _parse_subtasks(self, response: str) -> List[str]:
        lines = response.strip().split('\n')
        subtasks = []
        for line in lines:
            if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                subtask = line.split('.', 1)[-1].strip() if '.' in line else line.strip()
                subtasks.append(subtask)
        return subtasks
    
    async def _execute_parallel_research(self) -> List[Dict[str, Any]]:
        research_agents = []
        tasks_to_execute = []
        
        for i, task in enumerate(self.active_tasks):
            agent_id = f"researcher_{i}"
            agent = ResearchAgent(agent_id, self.client)
            self.subagents[agent_id] = agent
            research_agents.append(agent)
            tasks_to_execute.append(task)
        
        results = await asyncio.gather(*[
            agent.process_task(task) 
            for agent, task in zip(research_agents, tasks_to_execute)
        ])
        
        return results
    
    async def _synthesize_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        combined_findings = "\n\n".join([
            f"Research Area: {result.get('topic', 'Unknown')}\n{result.get('findings', '')}"
            for result in results if result
        ])
        
        synthesis_prompt = f"""
        Synthesize these research findings into a comprehensive report:
        
        {combined_findings}
        
        Provide:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Conclusions
        
        Format as a structured report.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        
        return {
            "final_report": response.content[0].text,
            "subtask_results": results,
            "total_tasks": len(self.active_tasks)
        }
    
    async def process_task(self, task: Task) -> Any:
        return await self.research_query(task.description)