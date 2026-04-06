# 🚀 AutoSeller AI

AutoSeller AI is an intelligent agent system designed to simplify and automate the process of selling second-hand items.

Instead of manually handling pricing, listing, negotiation, payment, and delivery, the system guides and automates the entire workflow — from uploading an item to completing a sale.

---

## 🧠 Problem Statement

Selling second-hand items today is fragmented and time-consuming.

Users must:
- Decide the correct price
- Create listings manually
- Respond to multiple buyers
- Negotiate deals
- Manage payments and delivery

This leads to:
- Underpricing
- Time loss
- Abandoned transactions

---

## 💡 Solution

AutoSeller AI introduces an **agent-based system** that:

- Analyzes the uploaded item
- Suggests optimal pricing
- Generates a ready-to-use listing
- Handles buyer interactions
- Negotiates offers automatically
- Guides payment and delivery flow

The goal is to reduce the effort of selling to **almost zero**.

---

## ⚙️ Key Features

### 🔍 1. AI-Based Item Analysis
- Extracts item details (title, category, condition)
- Estimates resale value
- Uses vision models (Gemini integration-ready)

---

### 💰 2. Smart Pricing Engine
- Uses rule-based + data-driven logic
- Considers condition, category, and market trends
- Generates optimal asking price

---

### 📝 3. Automated Listing Generator
- Creates title, description, and tags
- Suggests best platform for selling
- Provides ready-to-use listing format

---

### 💬 4. AI Negotiation System (In Progress)
- Handles buyer queries
- Evaluates offers using thresholds:
  - Accept (>95%)
  - Reject (<60%)
  - Counter (between range)
- Adaptive negotiation strategy

---

### 💳 5. Payment Flow (Integration Ready)
- Razorpay integration designed
- Supports secure transaction handling
- Escrow-style flow planned for trust

---

### 🚚 6. Delivery & Tracking (Integration Ready)
- Shiprocket / Delhivery integration designed
- Pickup scheduling
- Real-time tracking updates

---

### 🧠 7. Memory & Learning System
- Stores interaction data
- Tracks:
  - Final price
  - Time to sell
  - Platform success
- Improves future decisions

---

### ⚠️ 8. Risk Detection
- Detects suspicious buyer behavior
- Flags potential fraud patterns
- Enhances trust and safety

---

## 🔄 Agent Workflow

The system follows an autonomous loop:

### 1. THINK
- Understand item
- Estimate price
- Identify platform
- Analyze buyer intent

### 2. PLAN
- Generate listing
- Define pricing thresholds
- Decide negotiation strategy

### 3. EXECUTE
- Call services:
  - AI analysis
  - Pricing
  - Listing
  - Negotiation
  - Payment
  - Delivery

### 4. REVIEW
- Evaluate offers and outcomes
- Store data in memory

### 5. UPDATE
- Improve pricing and negotiation logic
- Update system performance

---

## 🧱 Project Structure
```
autoseller_ai/
│
├── app.py
├── config.py
├── constants.py
├── requirements.txt
├── .env
├── claude.md
│
├── agent/
│   ├── orchestrator.py
│   ├── agent_loop.py
│   ├── state_machine.py
│   ├── state_manager.py
│   ├── memory.py
│   ├── long_term_memory.py
│   ├── feedback_engine.py
│   ├── decision_engine.py
│   └── risk_checker.py
│
├── services/
│   ├── ai_service.py
│   ├── listing_service.py
│   ├── pricing_service.py
│   ├── platform_service.py
│   ├── buyer_service.py
│   ├── negotiation_service.py
│   ├── payment_service.py
│   ├── logistics_service.py
│   ├── notification_service.py
│   └── contact_service.py
│
├── routes/
│   ├── upload.py
│   ├── agent.py
│   ├── chat.py
│   ├── delivery.py
│   └── payment.py
│
├── integrations/
│   ├── gemini.py
│   ├── razorpay.py
│   └── shiprocket.py
│
├── database/
│   ├── db.py
│   └── models.py
│
├── schemas/
│   ├── item_schema.py
│   ├── chat_schema.py
│   ├── negotiation_schema.py
│   ├── delivery_schema.py
│   └── payment_schema.py
│
├── simulations/
│   ├── fake_chat.py
│   ├── fake_tracking.py
│   ├── fake_market.py
│   └── sim_router.py
│
├── templates/
│   ├── index.html
│   ├── dashboard.html
│   ├── marketplace.html
│   ├── chat.html
│   └── tracking.html
│
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── dashboard.css
│   │   ├── chat.css
│   │   ├── marketplace.css
│   │   └── tracking.css
│   │
│   ├── js/
│   │   ├── upload.js
│   │   ├── agent.js
│   │   ├── chat.js
│   │   ├── marketplace.js
│   │   └── tracking.js
│   │
│   └── images/
│       └── logo.png
│
├── uploads/
│
├── utils/
│   ├── helpers.py
│   ├── scheduler.py
│   ├── logger.py
│   └── explain.py
│
└── tests/
    └── test_agent_flow.py
```

---

## 🛠️ Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite

### Frontend
- HTML
- CSS
- JavaScript

### AI & Agent System
- Custom Agent Architecture
- State Machine + Orchestrator
- Decision Engine
- Memory System

### Integrations (Designed / Partial)
- Gemini Vision (AI)
- Razorpay (Payments)
- Shiprocket / Delhivery (Logistics)

---

## 📊 Current Status

- Core agent pipeline implemented
- Dashboard and item analysis working
- Negotiation, chat, and marketplace in progress
- Simulation layer used for full workflow demonstration
- Designed for real-world API integration

---

## 🚧 Future Scope

- Real AI model integration for image analysis
- WhatsApp API / chat system integration
- Escrow-based payment system
- Real logistics API integration
- Campus-focused marketplace MVP

---

## 🌍 SDG Alignment

Aligned with **SDG 12: Responsible Consumption and Production**

Encourages reuse of products and reduces waste through easier resale.

---

## 👩‍💻 Author

**Sandhya**  
Founder & Full Stack Developer  

Built as a solo project — including backend, frontend, and AI agent architecture.

---

## ⭐ Final Note

AutoSeller AI is not just a tool — it is a step toward **autonomous commerce**, where intelligent agents handle complex real-world workflows.
