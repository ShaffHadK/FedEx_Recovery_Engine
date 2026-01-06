import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import time


# CONFIG & STYLE

st.set_page_config(page_title="FedEx Smart Recovery", layout="wide", page_icon="logos/recovery.png")

# Custom CSS for FedEx Colors
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center;}
    h1 {color: #4D148C;} /* FedEx Purple */
    h3 {color: #FF6600;} /* FedEx Orange */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #32174D; border-radius: 4px 4px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; padding-right:10px;padding-left:10px }
    .stTabs [aria-selected="true"] { background-color: #E5E4E2; border-bottom: 2px solid #4D148C; color: #4D148C; }
</style>
""", unsafe_allow_html=True)

API_URL = "http://127.0.0.1:8080"
DATA_PATH = "data/demo_cases_bulk.csv"


# CONSTANTS & SIGNAL WEIGHTS

SIGNAL_WEIGHTS = {
    "CALL_ANSWERED": 1.5,
    "SMS_REPLIED": 1.0,
    "PROMISE_TO_PAY": 4.0,
    "PAYMENT_DATE_CONFIRMED": 4.5,
    "PARTIAL_PAYMENT": 6.0,
    "BROKEN_PROMISE": -4.0,
    "NO_RESPONSE_7_DAYS": -1.5
}


# SESSION STATE SETUP

if "signals" not in st.session_state:
    st.session_state.signals = {}
if "processed_data" not in st.session_state:
    st.session_state.processed_data = None


# DATA LOADING & API CALLS

def load_and_process_data():
    
    try:
        raw_df = pd.read_csv(DATA_PATH)
        
        
        payload = {"cases": [], "signals": []}
        
        for _, row in raw_df.iterrows():
            features = row.drop("case_id").to_dict()
            payload["cases"].append({"case_id": row["case_id"], "features": features})
            
        for cid, sigs in st.session_state.signals.items():
            for s, w in sigs:
                payload["signals"].append({"case_id": cid, "signal_type": s, "weight": w})
        
        # Call API
        response = requests.post(f"{API_URL}/allocate", json=payload)
        response.raise_for_status()
        
        # Merge Results
        result_df = pd.DataFrame(response.json())
        final_df = pd.merge(raw_df, result_df, on="case_id")
        
        st.session_state.processed_data = final_df
        return final_df
    except Exception as e:
        st.error(f"⚠️ System Offline: {e}")
        return pd.DataFrame()


if st.session_state.processed_data is None:
    df = load_and_process_data()
else:
    df = st.session_state.processed_data


# SIDEBAR: ROLE SELECTION (SECURITY REQUIREMENT)


st.sidebar.image("logos/fedex.png", width=150)
st.sidebar.title("Portal Login")
user_role = st.sidebar.radio("View As:", ["FedEx HQ (Admin)", "DCA Agent (External)"])

if user_role == "DCA Agent (External)":
    # MOCK LOGIN
    dca_login = st.sidebar.selectbox("Select Agency", ["DCA_TOP", "DCA_STANDARD", "DCA_BULK"])
    st.sidebar.info(f"Logged in as: **{dca_login}**")
    st.sidebar.caption("Restricted View: You can only see cases assigned to your agency.")
else:
    st.sidebar.success("Logged in as: **FedEx Admin**")
    st.sidebar.caption("Full View: Portfolio Analytics & Allocation Control.")



# VIEW 1: FEDEX HQ (ADMIN DASHBOARD)


if user_role == "FedEx HQ (Admin)":
    st.title("Intelligent DCA Orchestrator")
    st.caption("AI-Driven Prioritization • Real-Time Agency Allocation • Compliance Automation")

    tab1, tab2, tab3 = st.tabs(["📈 Executive Dashboard", "⚡ Live Operations Center", "🤖 Agency Performance"])

    
    with tab1:
        st.markdown("### 📊 Portfolio Health Overview")
        if not df.empty:
            
            tot_amnt = df["loan_amnt"].sum()
            avg_score = df["final_priority_score"].mean()
            high_priority_count = df[df["action_type"] == "IMMEDIATE_ESCALATION"].shape[0]
            
           
            try:
                cap_resp = requests.get(f"{API_URL}/dca-capacity").json()
                active_dcas = len(cap_resp)
                total_cap = sum(d['max_capacity'] for d in cap_resp)
                used_cap = sum(d['current_load'] for d in cap_resp)
                cap_pct = (used_cap / total_cap) * 100 if total_cap > 0 else 0
                cap_label = f"Utilization: {cap_pct:.1f}%"
            except:
                active_dcas = "N/A"
                cap_label = "Offline"

            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Exposure", f"${tot_amnt:,.0f}")
            kpi2.metric("Recovery Probability", f"{avg_score*100:.1f}%", delta="AI Prediction")
            kpi3.metric("Urgent Escalations", high_priority_count, delta="Action Req.", delta_color="inverse")
            kpi4.metric("Active Agencies", str(active_dcas), cap_label)

            st.divider()

            # Charts
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("#### 🎯 Risk Segmentation")
                fig_risk = px.pie(df, names="action_type", title="Strategy Distribution", 
                                  color="action_type", hole=0.4,
                                  color_discrete_map={"IMMEDIATE_ESCALATION":"#FF6600", "STANDARD_QUEUE":"#4D148C", "DIGITAL_ONLY":"#999999"})
                st.plotly_chart(fig_risk, use_container_width=True)
            with c2:
                st.markdown("#### 💰 Allocation Value")
                fig_bar = px.bar(df, x="assigned_dca", y="loan_amnt", color="assigned_dca", 
                                 title="Assigned Value ($)", 
                                 color_discrete_sequence=px.colors.qualitative.Bold)
                st.plotly_chart(fig_bar, use_container_width=True)

    
    with tab2:
        st.markdown("### ⚡ Centralized Case Allocation")
        
        c_side, c_main = st.columns([1, 3])
        
        with c_side:
            st.success("📡 **Signal Injection**")
            st.caption("Simulate debtor interaction.")
            
            case_select = st.selectbox("Select Case ID", df["case_id"].unique(), index=0)
            signal_select = st.selectbox("Signal Type", list(SIGNAL_WEIGHTS.keys()))
            
            if st.button("Inject Signal"):
                weight = SIGNAL_WEIGHTS[signal_select]
                st.session_state.signals.setdefault(case_select, [])
                st.session_state.signals[case_select].append((signal_select, weight))
                with st.spinner("Recalculating..."):
                    load_and_process_data()
                st.rerun()

            if st.button("Reset Signals"):
                st.session_state.signals = {}
                load_and_process_data()
                st.rerun()
            
            if st.session_state.signals:
                st.markdown("---")
                st.markdown("**Active Signals:**")
                for cid, sigs in st.session_state.signals.items():
                    st.caption(f"**{cid}**: {len(sigs)} events")

        with c_main:
            filter_status = st.multiselect("Filter DCA", df["assigned_dca"].unique(), default=df["assigned_dca"].unique())
            view_df = df[df["assigned_dca"].isin(filter_status)]
            
            st.dataframe(
                view_df[["case_id", "loan_amnt", "ml_score", "graph_score", "final_priority_score", "assigned_dca", "action_type"]]
                .sort_values("final_priority_score", ascending=False)
                .style.format({"ml_score": "{:.2f}", "graph_score": "{:.2f}", "final_priority_score": "{:.2f}", "loan_amnt": "${:,.0f}"})
                .applymap(lambda x: 'background-color: #FF0800' if x == "DCA_TOP" else '', subset=['assigned_dca'])
                , use_container_width=True, height=500
            )

 
    with tab3:
        st.markdown("### 🏭 Agency Capacity (Real-Time)")
        try:
            cap_data = requests.get(f"{API_URL}/dca-capacity").json()
            df_cap = pd.DataFrame(cap_data)
            df_cap["% Full"] = (df_cap["current_load"] / df_cap["max_capacity"]) * 100
            
            fig_cap = px.bar(df_cap, x="dca_id", y="current_load", 
                             hover_data=["max_capacity"], color="% Full",
                             color_continuous_scale="RdYlGn_r",
                             range_color=[0, 100],
                             title="Current Case Load vs Max Capacity")
            st.plotly_chart(fig_cap, use_container_width=True)
        except:
            st.warning("API Offline")

        st.info("💡 **Note:** This chart updates live as you inject signals in Tab 2. Allocations shift automatically to prevent overflow.")



# VIEW 2: DCA AGENT (EXTERNAL PORTAL)


elif user_role == "DCA Agent (External)":
    st.title(f"Portal: {dca_login}")
    st.markdown("---")
    
    
    my_cases = df[df["assigned_dca"] == dca_login].copy()
    
    col_a, col_b = st.columns([1, 2])
    
    with col_a:
        st.metric("My Assigned Cases", len(my_cases))
        st.metric("Priority Cases", len(my_cases[my_cases['action_type'] == 'IMMEDIATE_ESCALATION']))
    
    with col_b:
        st.warning("⚠️ **Compliance Alert:** Please complete SOPs for Priority Cases within 2 hours.")
    
    st.markdown("### 📋 My Case Worklist")
    
   
    if not my_cases.empty:
        for idx, row in my_cases.sort_values("final_priority_score", ascending=False).iterrows():
            with st.expander(f"{row['case_id']} | Score: {row['final_priority_score']:.2f} | {row['action_type']}"):
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Amount Due:** ${row['loan_amnt']:,.2f}")
                    st.write(f"**Income:** ${row['annual_inc']:,.0f}")
                    st.write(f"**Momentum:** {row['graph_score']:.2f}")
                with c2:
                    st.markdown("**✅ SOP Checklist:**")
                    
                    for step in row['sop_steps']:
                        st.checkbox(step, key=f"{row['case_id']}_{step}")
                    
                    st.text_area("Agent Notes", placeholder="Enter call disposition...", key=f"note_{row['case_id']}")
                    st.button("Submit Update", key=f"btn_{row['case_id']}")
    else:
        st.info("No active cases assigned.")