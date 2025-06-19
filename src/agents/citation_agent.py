from typing import Dict, Any, List
import re
from .base_agent import BaseAgent, AgentType, Task

class CitationAgent(BaseAgent):
    def __init__(self, agent_id: str, anthropic_client):
        super().__init__(agent_id, AgentType.CITATION, anthropic_client)
    
    async def process_task(self, task: Task) -> Dict[str, Any]:
        content = task.description
        citations = await self._generate_citations(content)
        attributed_content = await self._add_attributions(content, citations)
        
        task.status = "completed"
        task.result = {
            "original_content": content,
            "attributed_content": attributed_content,
            "citations": citations
        }
        
        return task.result
    
    async def _generate_citations(self, content: str) -> List[Dict[str, Any]]:
        citation_prompt = f"""
        Analyze this research content and identify claims that need citations:
        
        {content}
        
        For each factual claim, statistical data, or research finding, suggest:
        1. What type of source would support this claim
        2. Reliability level needed (peer-reviewed, government, news, etc.)
        3. Specific search terms to find supporting sources
        
        Format as numbered list with clear claim identification.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": citation_prompt}]
        )
        
        return self._parse_citation_needs(response.content[0].text)
    
    def _parse_citation_needs(self, citation_text: str) -> List[Dict[str, Any]]:
        citations = []
        lines = citation_text.split('\n')
        current_citation = {}
        
        for line in lines:
            line = line.strip()
            if line and line[0].isdigit():
                if current_citation:
                    citations.append(current_citation)
                current_citation = {
                    "id": len(citations) + 1,
                    "claim": line.split('.', 1)[1].strip() if '.' in line else line,
                    "source_type": "unknown",
                    "reliability": "medium"
                }
            elif "source" in line.lower() or "type" in line.lower():
                if current_citation:
                    current_citation["source_type"] = line.split(':')[-1].strip()
            elif "reliability" in line.lower() or "level" in line.lower():
                if current_citation:
                    current_citation["reliability"] = line.split(':')[-1].strip()
        
        if current_citation:
            citations.append(current_citation)
        
        return citations
    
    async def _add_attributions(self, content: str, citations: List[Dict[str, Any]]) -> str:
        if not citations:
            return content
        
        attribution_prompt = f"""
        Add proper citation markers to this content based on the identified citation needs:
        
        Original Content:
        {content}
        
        Citation Requirements:
        {self._format_citations_for_prompt(citations)}
        
        Add [1], [2], etc. markers after claims that need citations.
        Provide the attributed content and a bibliography section.
        """
        
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            messages=[{"role": "user", "content": attribution_prompt}]
        )
        
        return response.content[0].text
    
    def _format_citations_for_prompt(self, citations: List[Dict[str, Any]]) -> str:
        formatted = []
        for i, citation in enumerate(citations, 1):
            formatted.append(f"{i}. {citation.get('claim', 'Unknown claim')}")
        return "\n".join(formatted)
    
    def validate_citations(self, content: str) -> Dict[str, Any]:
        citation_pattern = r'\[(\d+)\]'
        citations_found = re.findall(citation_pattern, content)
        
        return {
            "total_citations": len(citations_found),
            "citation_numbers": [int(c) for c in citations_found],
            "properly_formatted": len(citations_found) > 0,
            "sequential": self._check_sequential_citations(citations_found)
        }
    
    def _check_sequential_citations(self, citations: List[str]) -> bool:
        if not citations:
            return True
        
        citation_nums = sorted([int(c) for c in citations])
        return citation_nums == list(range(1, len(citation_nums) + 1))