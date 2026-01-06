import pandas as pd
import os

# GLOBAL STATE
DCA_STATE = pd.DataFrame()

def load_dca_profiles():
    global DCA_STATE
    base_dir = os.path.dirname(__file__)
    path = os.path.join(base_dir, "..", "data", "dca_profiles.csv")


    # 1. Load Data
    if os.path.exists(path):
        try:
            DCA_STATE = pd.read_csv(path, sep=",", encoding="utf-8")
            DCA_STATE.columns = DCA_STATE.columns.str.strip()
            print("✅ DCA Profiles loaded from CSV.")
        except Exception as e:
            print(f"⚠️ CSV Load Error: {e}. Reverting to defaults.")
            DCA_STATE = pd.DataFrame()

    
    # 2. Validation & Defaults
    required_cols = ["dca_id", "max_capacity", "current_load", "success", "sla"]

    # If CSV failed or is missing required columns, load defaults
    if DCA_STATE.empty or not all(col in DCA_STATE.columns for col in required_cols):
        print("⚠️ Using Default DCA Profiles (CSV missing or invalid).")
        DCA_STATE = pd.DataFrame([
            {"dca_id": "DCA_TOP", "max_capacity": 50, "current_load": 0, "success": 0.85, "sla": 0.95},
            {"dca_id": "DCA_STANDARD", "max_capacity": 200, "current_load": 0, "success": 0.70, "sla": 0.90},
            {"dca_id": "DCA_BULK", "max_capacity": 1000, "current_load": 0, "success": 0.55, "sla": 0.85},
        ])

def allocate_cases_with_state(df_cases: pd.DataFrame) -> pd.DataFrame:
    global DCA_STATE
    
    # Ensure state is loaded
    if DCA_STATE.empty:
        load_dca_profiles()
    
    # Sort cases by priority
    if "final_priority_score" in df_cases.columns:
        df_cases = df_cases.sort_values("final_priority_score", ascending=False)
    
    assignments = []

    for _, case in df_cases.iterrows():
        # Check Global Capacity
        eligible = DCA_STATE[DCA_STATE["current_load"] < DCA_STATE["max_capacity"]].copy()

        if eligible.empty:
            assignments.append("INTERNAL_HOLD_QUEUE")
            continue

        # Score DCAs
        eligible["score"] = 0.6 * eligible["success"] + 0.4 * eligible["sla"]
        
        # Optimization Strategy
        priority = case.get("final_priority_score", 0.5)
        if priority > 0.7:
             chosen = eligible.sort_values("score", ascending=False).iloc[0]
        else:
             chosen = eligible.sort_values("score", ascending=True).iloc[0]

        dca_id = chosen["dca_id"]
        assignments.append(dca_id)

        # UPDATE GLOBAL STATE
        DCA_STATE.loc[DCA_STATE["dca_id"] == dca_id, "current_load"] += 1

    df_cases["assigned_dca"] = assignments
    return df_cases

def get_dca_status():
    global DCA_STATE
    if DCA_STATE.empty: load_dca_profiles()
    return DCA_STATE.to_dict(orient="records")