from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class CaseInput(BaseModel):
    case_id: str
    features: Dict[str, Any] 

class SignalInput(BaseModel):
    case_id: str
    signal_type: str 
    weight: float

class AllocationRequest(BaseModel):
    cases: List[CaseInput]
    signals: List[SignalInput] = []

class AllocationResponse(BaseModel):
    case_id: str
    ml_score: float
    graph_score: float
    final_priority_score: float
    assigned_dca: str
    sop_steps: List[str]
    action_type: str