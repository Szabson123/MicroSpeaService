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

class FullCheck(BaseModel):
    task_num: UUID
    sns: List[str]
    machine_name: str

class CheckedSNItem(BaseModel):
    sn_data: Dict[str, Dict[str, str]] 
    prev_phase: bool
    phase_error_code: str