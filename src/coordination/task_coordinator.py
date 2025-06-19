import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from ..agents.base_agent import BaseAgent, Task, AgentType

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class TaskResult:
    task_id: str
    status: TaskStatus
    result: Any
    agent_id: str
    execution_time: float
    error: Optional[str] = None

class TaskCoordinator:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_results: Dict[str, TaskResult] = {}
        self.agent_assignments: Dict[str, List[str]] = {}
        
    def create_task(self, description: str, priority: str = "medium", 
                   metadata: Optional[Dict[str, Any]] = None) -> str:
        task_id = f"task_{len(self.tasks) + 1}"
        task = Task(
            id=task_id,
            description=description,
            status="pending"
        )
        self.tasks[task_id] = task
        return task_id
    
    def assign_task(self, task_id: str, agent: BaseAgent) -> bool:
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.assigned_agent = agent.agent_id
        task.status = "assigned"
        
        if agent.agent_id not in self.agent_assignments:
            self.agent_assignments[agent.agent_id] = []
        self.agent_assignments[agent.agent_id].append(task_id)
        
        return True
    
    async def execute_task(self, task_id: str, agent: BaseAgent) -> TaskResult:
        if task_id not in self.tasks:
            return TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                result=None,
                agent_id=agent.agent_id,
                execution_time=0.0,
                error="Task not found"
            )
        
        task = self.tasks[task_id]
        task.status = "in_progress"
        
        start_time = asyncio.get_event_loop().time()
        
        try:
            result = await agent.process_task(task)
            end_time = asyncio.get_event_loop().time()
            
            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                agent_id=agent.agent_id,
                execution_time=end_time - start_time
            )
            
            task.status = "completed"
            task.result = result
            
        except Exception as e:
            end_time = asyncio.get_event_loop().time()
            task_result = TaskResult(
                task_id=task_id,
                status=TaskStatus.FAILED,
                result=None,
                agent_id=agent.agent_id,
                execution_time=end_time - start_time,
                error=str(e)
            )
            
            task.status = "failed"
        
        self.task_results[task_id] = task_result
        return task_result
    
    async def execute_parallel_tasks(self, task_agent_pairs: List[tuple]) -> List[TaskResult]:
        tasks_to_execute = []
        
        for task_id, agent in task_agent_pairs:
            if self.assign_task(task_id, agent):
                tasks_to_execute.append(self.execute_task(task_id, agent))
        
        results = await asyncio.gather(*tasks_to_execute, return_exceptions=True)
        
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(TaskResult(
                    task_id="unknown",
                    status=TaskStatus.FAILED,
                    result=None,
                    agent_id="unknown",
                    execution_time=0.0,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    def get_task_status(self, task_id: str) -> Optional[str]:
        if task_id in self.tasks:
            return self.tasks[task_id].status
        return None
    
    def get_agent_tasks(self, agent_id: str) -> List[Task]:
        task_ids = self.agent_assignments.get(agent_id, [])
        return [self.tasks[tid] for tid in task_ids if tid in self.tasks]
    
    def get_coordination_summary(self) -> Dict[str, Any]:
        total_tasks = len(self.tasks)
        completed_tasks = sum(1 for task in self.tasks.values() if task.status == "completed")
        failed_tasks = sum(1 for task in self.tasks.values() if task.status == "failed")
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks > 0 else 0,
            "active_agents": len(self.agent_assignments),
            "avg_execution_time": self._calculate_avg_execution_time()
        }
    
    def _calculate_avg_execution_time(self) -> float:
        completed_results = [r for r in self.task_results.values() 
                           if r.status == TaskStatus.COMPLETED]
        if not completed_results:
            return 0.0
        
        total_time = sum(r.execution_time for r in completed_results)
        return total_time / len(completed_results)