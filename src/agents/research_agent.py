from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentType, Task

class ResearchAgent(BaseAgent):
    def __init__(self, agent_id: str, anthropic_client):
        super().__init__(agent_id, AgentType.RESEARCHER, anthropic_client)
        self.research_depth = "comprehensive"
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        research_result = await self._conduct_research(task.description)
        
        task.status = "completed"
        task.result = research_result
        
        return research_result
    
    async def _conduct_research(self, topic: str) -> Dict[str, Any]:
        research_prompt = f"""
        You are a specialized research agent. Thoroughly research this topic: {topic}
        
        Use interleaved thinking to evaluate your research process:
        1. What are the key aspects to explore?
        2. What questions need answering?
        3. What evidence supports conclusions?
        
        Provide:
        - Key findings
        - Supporting evidence
        - Analysis and insights
        - Limitations or gaps
        
        Be comprehensive but focused.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": research_prompt}]
        )
        
        findings = response.content[0].text
        
        return {
            "agent_id": self.agent_id,
            "topic": topic,
            "findings": findings,
            "confidence": self._assess_confidence(findings),
            "key_points": self._extract_key_points(findings)
        }
    
    def _assess_confidence(self, findings: str) -> float:
        confidence_indicators = [
            "evidence shows", "research indicates", "studies demonstrate",
            "data confirms", "analysis reveals", "established that"
        ]
        uncertainty_indicators = [
            "unclear", "uncertain", "limited evidence", "requires further",
            "insufficient data", "conflicting"
        ]
        
        confidence_score = sum(1 for indicator in confidence_indicators 
                              if indicator in findings.lower())
        uncertainty_score = sum(1 for indicator in uncertainty_indicators 
                              if indicator in findings.lower())
        
        total_indicators = confidence_score + uncertainty_score
        if total_indicators == 0:
            return 0.5
        
        return confidence_score / total_indicators
    
    def _extract_key_points(self, findings: str) -> List[str]:
        lines = findings.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                key_points.append(line[1:].strip())
            elif line and line[0].isdigit() and '.' in line:
                key_points.append(line.split('.', 1)[1].strip())
        
        return key_points[:5]