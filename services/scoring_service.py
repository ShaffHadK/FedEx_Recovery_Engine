
import pandas as pd
from engines.ml_engine import predict_recovery_probability
from engines.graph_engine import build_case_graph, compute_case_rank

ALPHA = 0.6
BETA = 0.4

# Domain assumption: ~2–3 strong signals = full momentum
MAX_EXPECTED_MOMENTUM = 10.0


def generate_sop(row) -> list:
    score = row["final_priority_score"]

    if score >= 0.75:
        return [
            "⚡ PRIORITY: Call within 1 hour",
            "💰 Offer Plan A (10% waiver)"
        ]
    elif score <= 0.30:
        return [
            "📧 AUTO: Send Email Nudge",
            "🚫 No outbound calls"
        ]
    else:
        return [
            "📞 Standard Call",
            "📅 Schedule follow-up"
        ]


def determine_action(row) -> str:
    ml = row["recovery_probability"]
    g  = row["graph_score"]
    p  = row["final_priority_score"]

    if p >= 0.80 or (g >= 0.70 and ml >= 0.60):
        return "IMMEDIATE_ESCALATION"
    elif p <= 0.30:
        return "DIGITAL_ONLY"
    else:
        return "STANDARD_QUEUE"


def compute_scores(df: pd.DataFrame, signals: dict) -> pd.DataFrame:
    df = df.copy()

    # ML PRIOR (STATIC)
    df = predict_recovery_probability(df)

    # GRAPH MOMENTUM (DYNAMIC)
    G = build_case_graph(df, signals)
    momentum_scores = compute_case_rank(G)

    df["graph_raw"] = df["case_id"].map(momentum_scores).fillna(0.0)

    # EMANTIC NORMALIZATION
    df["graph_score"] = (df["graph_raw"] / MAX_EXPECTED_MOMENTUM).clip(0.0, 1.0)

    # HYBRID PRIORITY SCORE
    df["final_priority_score"] = (
        ALPHA * df["recovery_probability"]
        + BETA * df["graph_score"]
    )

    # OPERATIONAL LAYER
    df["sop_steps"] = df.apply(generate_sop, axis=1)
    df["action_type"] = df.apply(determine_action, axis=1)

   
    return df.rename(columns={"recovery_probability": "ml_score"})
