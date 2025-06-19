"""
Simple Research System

A streamlined multi-agent research system that conducts comprehensive research
by decomposing queries into subtasks, researching each independently, and
synthesizing results into coherent reports.
"""

import logging
import os
from typing import Dict, Any, Optional, List

import anthropic
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchError(Exception):
    """Custom exception for research-related errors."""
    pass


class SimpleResearchSystem:
    """
    A simplified multi-agent research system.
    
    This system conducts research by:
    1. Decomposing complex queries into focused subtasks
    2. Researching each subtask independently 
    3. Synthesizing all findings into a comprehensive report
    """
    
    DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
    MAX_SUBTASKS = 4
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None) -> None:
        """
        Initialize the research system.
        
        Args:
            api_key: Anthropic API key. If None, loads from environment.
            model: Claude model to use. Defaults to claude-3-5-sonnet-20241022.
            
        Raises:
            ResearchError: If API key is not provided or found in environment.
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key or self.api_key.strip() == "":
            raise ResearchError(
                "Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable."
            )
        
        self.model = model or os.getenv("MODEL_NAME", self.DEFAULT_MODEL)
        
        try:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            logger.info(f"Initialized research system with model: {self.model}")
        except Exception as e:
            raise ResearchError(f"Failed to initialize Anthropic client: {e}")
        
    def conduct_research(self, query: str) -> Dict[str, Any]:
        """
        Conduct comprehensive research on a query.
        
        Args:
            query: The research question to investigate.
            
        Returns:
            Dict containing query, subtasks, research results, and final report.
            
        Raises:
            ResearchError: If research process fails.
        """
        if not query or not query.strip():
            raise ResearchError("Query cannot be empty")
            
        logger.info(f"Starting research for query: {query[:100]}...")
        
        try:
            # Step 1: Break down the query
            logger.info("Step 1: Decomposing query into subtasks")
            subtasks = self._decompose_query(query)
            logger.info(f"Generated {len(subtasks)} subtasks")
            
            # Step 2: Research each subtask
            logger.info("Step 2: Researching subtasks")
            research_results = []
            for i, subtask in enumerate(subtasks):
                logger.info(f"Researching subtask {i+1}/{len(subtasks)}")
                result = self._research_subtask(subtask, i)
                research_results.append(result)
            
            # Step 3: Synthesize results
            logger.info("Step 3: Synthesizing research findings")
            final_report = self._synthesize_results(query, research_results)
            
            logger.info("Research completed successfully")
            
            return {
                "query": query,
                "subtasks": subtasks,
                "research_results": research_results,
                "final_report": final_report,
                "total_subtasks": len(subtasks),
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Research failed: {e}")
            raise ResearchError(f"Research process failed: {e}")
    
    def _decompose_query(self, query: str) -> List[str]:
        """
        Break down the query into research subtasks.
        
        Args:
            query: The research question to decompose.
            
        Returns:
            List of subtask strings.
            
        Raises:
            ResearchError: If decomposition fails.
        """
        prompt = self._build_decomposition_prompt(query)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            subtasks = self._parse_subtasks(response.content[0].text)
            
            if not subtasks:
                raise ResearchError("Failed to generate subtasks from query")
                
            return subtasks
            
        except Exception as e:
            raise ResearchError(f"Query decomposition failed: {e}")
    
    def _build_decomposition_prompt(self, query: str) -> str:
        """Build the prompt for query decomposition."""
        return f"""Break down this research query into 3-4 specific subtasks:

Query: {query}

Requirements:
- Provide subtasks as a numbered list
- Each subtask should focus on a different aspect
- Make each subtask specific and actionable for research
- Ensure comprehensive coverage of the topic

Format your response as:
1. [First subtask]
2. [Second subtask]
3. [Third subtask]
4. [Fourth subtask (if needed)]"""
    
    def _parse_subtasks(self, response: str) -> List[str]:
        """
        Parse subtasks from the LLM response.
        
        Args:
            response: Raw response text from the LLM.
            
        Returns:
            List of parsed subtask strings.
        """
        lines = response.strip().split('\n')
        subtasks = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for numbered list items or bullet points
            if (line[0].isdigit() and '.' in line) or line.startswith('-'):
                # Extract the subtask text after the number/bullet
                if '.' in line:
                    subtask = line.split('.', 1)[1].strip()
                else:
                    subtask = line[1:].strip()
                    
                if subtask:
                    subtasks.append(subtask)
        
        # Limit to maximum subtasks
        return subtasks[:self.MAX_SUBTASKS]
    
    def _research_subtask(self, subtask: str, index: int) -> Dict[str, Any]:
        """
        Research a specific subtask.
        
        Args:
            subtask: The subtask to research.
            index: Index of the subtask.
            
        Returns:
            Dict containing research findings.
            
        Raises:
            ResearchError: If subtask research fails.
        """
        prompt = self._build_research_prompt(subtask)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "subtask": subtask,
                "index": index,
                "findings": response.content[0].text,
                "status": "completed",
                "model_used": self.model
            }
            
        except Exception as e:
            logger.error(f"Subtask research failed for '{subtask}': {e}")
            return {
                "subtask": subtask,
                "index": index,
                "findings": f"Research failed: {e}",
                "status": "failed",
                "model_used": self.model
            }
    
    def _build_research_prompt(self, subtask: str) -> str:
        """Build the prompt for researching a subtask."""
        return f"""Research this specific topic comprehensively: {subtask}

Please provide:

1. **Key Findings**: The most important discoveries or information
2. **Supporting Evidence**: Data, statistics, or credible sources that support the findings  
3. **Important Considerations**: Limitations, caveats, or important context
4. **Analysis**: Your interpretation and insights about the findings

Requirements:
- Be comprehensive but concise
- Focus on factual, well-supported information
- Provide specific details when possible
- Maintain objectivity and balance"""
    
    def _synthesize_results(self, query: str, research_results: List[Dict[str, Any]]) -> str:
        """
        Synthesize all research results into a final report.
        
        Args:
            query: Original research query.
            research_results: List of research result dictionaries.
            
        Returns:
            Synthesized final report.
            
        Raises:
            ResearchError: If synthesis fails.
        """
        # Filter successful results
        successful_results = [r for r in research_results if r["status"] == "completed"]
        
        if not successful_results:
            raise ResearchError("No successful research results to synthesize")
        
        combined_findings = self._format_findings(successful_results)
        prompt = self._build_synthesis_prompt(query, combined_findings)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            raise ResearchError(f"Result synthesis failed: {e}")
    
    def _format_findings(self, research_results: List[Dict[str, Any]]) -> str:
        """Format research findings for synthesis."""
        formatted_sections = []
        
        for result in research_results:
            section = f"""Research Area {result['index'] + 1}: {result['subtask']}
{'=' * 50}
{result['findings']}
"""
            formatted_sections.append(section)
        
        return "\n\n".join(formatted_sections)
    
    def _build_synthesis_prompt(self, query: str, combined_findings: str) -> str:
        """Build the prompt for synthesizing research results."""
        return f"""Synthesize these research findings into a comprehensive report for the query: 
"{query}"

Research Findings:
{combined_findings}

Create a well-structured report with the following sections:

1. **Executive Summary** (2-3 paragraphs)
   - Brief overview of the research scope
   - Key conclusions and main insights

2. **Key Findings** (bullet points or numbered list)
   - Most important discoveries from the research
   - Supported by evidence from the research areas

3. **Detailed Analysis** (several paragraphs)
   - In-depth discussion of the findings
   - Connections between different research areas
   - Implications and significance

4. **Conclusions** (1-2 paragraphs)
   - Final thoughts and synthesis
   - Future considerations or recommendations

Requirements:
- Maintain objectivity and balance
- Ensure logical flow between sections
- Reference findings from different research areas
- Make the report comprehensive yet accessible"""

    def get_system_info(self) -> Dict[str, Any]:
        """Get information about the research system configuration."""
        return {
            "model": self.model,
            "max_subtasks": self.MAX_SUBTASKS,
            "api_configured": bool(self.api_key),
            "version": "1.0.0"
        }