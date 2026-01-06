import joblib
import pandas as pd
import os
import warnings

# Path to your pickle file
MODEL_PATH = "models/recovery_model.pkl"

def predict_recovery_probability(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    model_loaded = False
    
    # 1. Try Loading the Pickle Model
    if os.path.exists(MODEL_PATH):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = joblib.load(MODEL_PATH)
                pass
        except Exception as e:
            print(f"⚠️ Model load failed ({e}). Using Financial Heuristic.")
    
    # 2. Heuristic Logic 
    if not model_loaded:
        def financial_risk_heuristic(row):
          
            score = 0.75 
            
            #  A. INCOME & DEBT  
            annual_inc = float(row.get("annual_inc", 50000))
            dti = float(row.get("dti", 20)) # Debt-to-Income Ratio
            
            # Higher income = Better score
            if annual_inc > 80000: score += 0.10
            if annual_inc < 30000: score -= 0.10
            
            # Lower DTI = Better score
            if dti > 25: score -= 0.15 # High debt burden
            if dti < 12: score += 0.05
            
            #  B. CREDIT UTILIZATION (Financial Stress) 
            revol_util = float(row.get("revol_util", 50))
            if revol_util > 70: score -= 0.10 # Maxed out cards
            if revol_util < 30: score += 0.05
            
            #  C. STABILITY (Home & Employment) 
            # Home Ownership
            if row.get("home_ownership_OWN", 0) == 1: score += 0.05
            if row.get("home_ownership_RENT", 0) == 1: score -= 0.05
            
            # Employment Length (Stability)
            if row.get("emp_length_10+ years", 0) == 1: score += 0.05
            
            #  D. LOAN CHARACTERISTICS 
            loan_amnt = float(row.get("loan_amnt", 10000))
            int_rate = float(row.get("int_rate", 10))
            
            # High interest rate often implies sub-prime risk
            if int_rate > 15: score -= 0.10
            
            # Sanity Cap (0.01 to 0.99)
            return max(0.01, min(score, 0.99))

        # Apply the new logic
        df["recovery_probability"] = df.apply(financial_risk_heuristic, axis=1)
    
    return df