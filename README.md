# FedEx Smart Recovery  
**AI-Driven Dynamic Case Prioritization & DCA Orchestration**

FedEx Smart Recovery is an intelligent decision engine designed to **dynamically prioritize delayed cases** and **allocate Debt Collection Agencies (DCAs)** based on a combination of **financial capacity** and **real-time customer engagement signals**.

Instead of treating all delayed customers the same, the system continuously adapts priorities to ensure the **right customer is contacted at the right time with the right action**.

---

# 📖 The Problem

FedEx manages thousands of overdue accounts using fragmented spreadsheets and static credit scores.

Once a case is classified as “high” or “low” risk, it rarely changes — even when the customer suddenly engages.

This leads to:
- Missed recovery opportunities  
- Overuse of premium DCAs  
- Delayed response to high-intent customers  

---

# 💡 Our Solution: Behavioral Momentum
**Priority ≠ Probability of Payment**
We distinguish between:
- **Capacity to pay** → long-term financial ability  
- **Intent to pay** → short-term engagement and behavior  

The system focuses on **urgency and timing**, not just risk.

---

## 🧠 Solution Overview

FedEx Smart Recovery combines:

### 1️⃣ Machine Learning (Static Layer)
- Estimates baseline recoverability
- Uses financial features like:
  - Income
  - Debt-to-Income (DTI)
  - Loan profile
- Changes slowly over time

### 2️⃣ Behavioral Momentum (Dynamic Layer)
- Captures real-time signals such as:
  - Call answered
  - Promise to pay
  - Payment date confirmed
  - Partial payment
- Uses a graph-based momentum model
- Includes saturation to prevent signal spamming

### 3️⃣ Hybrid Priority Score
```text
Priority = α × ML Score + β × Momentum
```

---

This score determines:
- **Case ranking**
- **DCA assignment**
- **Action type and SOP enforcement**

---

## ⚙️ Key Features

- 📊 **Dynamic case re-prioritization**
- ⚡ **Real-time reaction to customer behavior**
- 🏭 **Capacity-aware DCA allocation**
- 📋 **Automatic SOP enforcement**
- 🔍 **Explainable and policy-driven decisions**
- 🖥️ **Interactive Streamlit dashboard**

---

## 📡 Real-World Signals Used

| Category | Examples |
|--------|----------|
| Engagement | CALL_ANSWERED, SMS_REPLIED |
| Intent | PROMISE_TO_PAY, PAYMENT_DATE_CONFIRMED |
| Conversion | PARTIAL_PAYMENT |
| Negative | BROKEN_PROMISE, NO_RESPONSE_7_DAYS |

Signals **increase urgency**, but **cannot fully override financial risk**.

---

## 🏗️ System Architecture

```text
Loan & Customer Data
        ↓
 ML Risk Engine (Capacity)
        ↓
 Behavioral Signals
        ↓
 Graph-Based Momentum Engine
        ↓
 Priority Calculation
        ↓
 DCA Allocation & SOP Engine
        ↓
 Streamlit Command Center
```

- **FastAPI** acts as the single source of truth
- **Streamlit** is a presentation layer only
- No business logic is duplicated in the UI

---

# 🖥️ Dashboard Views

### 📊 Portfolio Intelligence
- Priority index overview
- Exposure distribution
- Escalation volume

### ⚡ Live Case Re-Prioritization
- Batch case ranking
- Signal injection
- Real-time priority movement

### 🏭 Agency Load & Governance
- DCA capacity utilization
- Allocation transparency
- Policy clarity

---

# 🚀 How to Run Locally

## 1️⃣ Clone the Repository
```bash
git clone https://github.com/ShaffHadK/FedEx_Recovery_Engine.git
cd FedEx_Recovery_Engine
```

## 2️⃣ Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

## 3️⃣ Install Dependencies
```bash
pip install -r requirement.txt
```

## 4️⃣ Start FastAPI Backend
```bash
uvicorn app.main:app --reload --port 8080
```

## 5️⃣ Run Streamlit Dashboard
```bash
streamlit run dashboard.py
```

---

# 🔮 Future Enhancements
- Time-decay on signals
- Dynamic risk refresh
- Region-specific policy tuning
- Reinforcement learning for thresholds
- CRM and call-log integrations

---

# 🏁 Final Note
FedEx Smart Recovery demonstrates how AI can drive operational decisions, not just generate scores.

---

<h3 align="center">Made By Team NeuroThrive for FedEx SMART Hackathon</h3> 

---

