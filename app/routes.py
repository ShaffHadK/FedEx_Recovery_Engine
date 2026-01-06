from fastapi import APIRouter
import pandas as pd

from app.schemas import AllocationRequest, AllocationResponse
from services.scoring_service import compute_scores
from services.allocation_service import allocate_cases_with_state, get_dca_status

router = APIRouter()

@router.post("/allocate", response_model=list[AllocationResponse])
def allocate_endpoint(payload: AllocationRequest):
    # 1. Convert cases to DataFrame
    records = []
    for c in payload.cases:
        record = {"case_id": c.case_id}
        
        # DYNAMIC LOADING: We trust the JSON payload to contain the correct model features
        # (loan_amnt, int_rate, dti, etc.)
        record.update(c.features)
        
        records.append(record)

    df_cases = pd.DataFrame(records)
    if df_cases.empty:
        return []

    # 2. Convert signals to dictionary
    signals = {}
    for s in payload.signals:
        signals.setdefault(s.case_id, []).append((s.signal_type, s.weight))

    # 3. Compute scores (ML + Graph)
    scored_cases = compute_scores(df_cases, signals)

    # 4. Allocate DCAs (Stateful)
    allocated = allocate_cases_with_state(scored_cases)

    return allocated.to_dict(orient="records")

@router.get("/dca-capacity")
def get_capacity_status():
    """Helper to visualize load balancing"""
    return get_dca_status()