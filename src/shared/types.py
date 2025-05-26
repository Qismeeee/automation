from typing import Dict, List, Optional, Literal, Any
from dataclasses import dataclass, field
from datetime import datetime

ActionType = Literal['click', 'type', 'wait', 'extract', 'screenshot', 'navigate']
WaitUntil = Literal['load', 'domcontentloaded', 'networkidle']

@dataclass
class StepOptions:
    multiple: Optional[bool] = None
    timeout: Optional[int] = None
    wait_until: Optional[WaitUntil] = None

@dataclass
class WorkflowStep:
    action: ActionType
    target: Optional[str] = None
    value: Optional[str] = None
    wait_time: Optional[int] = None
    options: Optional[StepOptions] = None


@dataclass
class WorkflowConfig:
    max_retries: int = 3
    timeout: int = 300
    captcha_solving: bool = False
    ai_assisted: bool = True


@dataclass
class WorkflowDefinition:
    workflow_id: str
    name: str
    steps: List[WorkflowStep]
    description: Optional[str] = None
    config: Optional[WorkflowConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

