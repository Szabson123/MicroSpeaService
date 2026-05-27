from pydantic import BaseModel
from typing import List, Dict
from uuid import UUID

class BinRequest(BaseModel):
    sns: List[str]
    machine_name: str
    task_num: UUID

class PhaseIDRequest(BaseModel):
    sns: Dict[str, str]
    machine_name: str
    phase_id: str
    task_num: UUID
    