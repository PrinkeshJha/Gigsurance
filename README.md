<div align="center">
  <h1>☔ GigSurance 🛡️</h1>
  <p><strong>Parametric Micro-Insurance for Gig Workers</strong></p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
    <img src="https://img.shields.io/badge/Celery-37814A?style=for-the-badge&logo=celery&logoColor=white" alt="Celery" />
    <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis" />
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  </p>
  <p><em>Zero-claim, real-time insurance payouts for the modern gig economy. Because waiting for claims is so last century! 🚀</em></p>
</div>

---

## 📖 Table of Contents

- [Why GigSurance?](#-why-gigsurance)
- [How it Works Under the Hood](#-how-it-works-under-the-hood)
- [Key Features](#-key-features)
- [Tech Stack](#-tech-stack)
- [Database Schema](#-database-schema)
- [Core Workflows](#-core-workflows)
- [Project Directory Layout](#-project-directory-layout)
- [Setting Up the Project](#-setting-up-the-project)
- [Running the Stack](#-running-the-stack)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Current Implementation Status](#-current-implementation-status)
- [Deployment Guide](#-deployment-guide)
- [Contributing](#-contributing)

---

## 💡 Why GigSurance?

### 🌩️ The Volatility Problem
Gig workers in food delivery, ride-sharing, and logistics face constant income volatility. When extreme weather strikes (severe heatwaves or monsoon rain storms) or when civil disturbances block city streets, order volume drops and driving becomes hazardous. Workers are forced to go offline, losing crucial daily income.

Traditional insurance is completely broken for this demographic. Filing claims for a lost ₹500 shift involves hours of paperwork, manual verification, and weeks of waiting.

### ⚡ The Zero-Claim Solution
**GigSurance** is a parametric insurance platform designed from scratch for the gig economy. 

- **Automatic Verification**: Payouts trigger automatically based on objective, third-party data feeds (weather parameters and local news reports). No claim forms or evidence submissions required.
- **Proportional Payouts**: Payouts match lost shift earnings using the formula: `hourly_rate × remaining_shift_hours × risk_multiplier`.
- **Fraud Prevention**: Integrates live GPS checks and machine learning models to detect location mismatches or claim anomalies.

---

## 🏗️ How it Works Under the Hood

```text
+-----------------------------------------------------+
|           Frontend (React + TypeScript)             |
|  DashboardPage, MonitorPage, AnalyticsPage, etc.    |
+------------------------+----------------------------+
                         |
                  Axios + React Query
                         |
         +--------------+-+------------------+
         |  Backend API (FastAPI)            |
         |  +- Auth & KYC Routes             |
         |  +- Policy & Subscription Routes  |
         |  +- Live Weather & Trigger Routes |
         |  +- Payments (Razorpay)           |
         |  +- Wallet & Ledger Routes        |
         |  +- WebSockets Live GPS Tracking  |
         +----------+----------+-----------+
                    |          |
        +-----------+--+   +---+------------+
        |  MongoDB     |   |  External APIs |
        | (Motor Async)|   |  +- OpenWeather|
        |              |   |  +- NewsAPI    |
        | Collections: |   |  +- Razorpay   |
        | . users      |   +----------------+
        | . policies   |
        | . triggers   |         +----------------------------------+
        | . payouts    |         |  Background Jobs (APScheduler)   |
        | . wallets    |         |  . Trigger Engine (every 10 min) |
        | . locations  |         |  . Forecast Alerts (every 6 hrs) |
        +--------------+         |  . Maturity Release (10 min job) |
                                 +----------------+-----------------+
                                                  |
                                       Async Task Dispatch (Redis)
                                                  |
                                                  v
                                 +----------------------------------+
                                 |    Celery Distributed Workers    |
                                 |  . ML-based Fraud Checks         |
                                 |  . GPS/Location Validation       |
                                 |  . Proportional Payout Engine    |
                                 +----------------------------------+
```

---

## ✨ Key Features

### 🛵 For Gig Workers
- **Onboarding Setup**: Set up your delivery platform, working city/zone, and scheduled shift hours to calculate a personalized risk score.
- **KYC Verification**: Submit PAN card image and number for automated masking, format validation, and instant verification reviews.
- **Micro-Deductions**: Pay weekly premiums dynamically via pay-as-you-go delivery deductions up to your cap limit.
- **Real-Time Monitoring**: Interactive dashboard mapping current weather conditions, active triggers, and risk alerts for the worker's specific zone.
- **Unified Wallet System**: Tracks Available vs. Pending balances. Workers can submit cashout requests (UPI vs. Bank Account) that auto-approve up to ₹10,000.
- **Notifications Hub**: Push alerts notifying workers of payouts or predictive weather warnings (next 48 hours).

### 👔 For Admins & Operations
- **Live Worker GPS Map**: Interactive dark-themed map layer showing online workers with real-time pulsing markers. Includes **Trip Session Replay** with speed play/pause multipliers to track historical delivery routes.
- **Geospatial Heatmaps**: Overlay layers visualizing **Worker Density**, **Fraud Hotspots**, **Weather Triggers**, and **Payout Distribution**.
- **K-Means Clustering**: Mapped indigo-colored spatial worker centroids showing coordinates and group sizes.
- **Interactive Zone Analytics**: Click/hover parametric zone outlines to inspect active triggers, total payouts, and active worker count.
- **Ops Dashboard**: Review and approve high-value cashout requests (> ₹10,000) and toggle wallet freeze states to protect insurance pools.

---

## 🛠️ Tech Stack

### Backend
- **Core Framework**: FastAPI (high-performance async endpoints)
- **Task Queue**: Celery 5.4.0 (offloads heavy validation and processing)
- **Message Broker & Result Store**: Redis 5.0.0
- **Background Scheduler**: APScheduler 3.10.0 (handles weather polling, resets, and wallet maturity)
- **Database Driver**: Motor (async wrapper for MongoDB)
- **Machine Learning**: Scikit-learn (RandomForest for risk scoring, Isolation Forest for fraud checks) + Joblib
- **Payments**: Razorpay SDK
- **Testing**: Pytest

### Frontend
- **Framework**: React 18 + Vite (TypeScript)
- **State & Data Fetching**: TanStack React Query + Axios
- **Mapping Library**: Leaflet + React-Leaflet (Vite optimized layout)
- **Styling**: Tailwind CSS + shadcn/ui (Radix UI primitives)
- **Animations**: Framer Motion
- **Charts**: Recharts
- **Testing**: Vitest + Playwright (E2E)

---

## 🗄️ Database Schema

Here is a summary of how we store our data in MongoDB:
- `users`: Core profile details, PAN, active platform, working location (city/zone), shift hours, and computed risk score/premium.
- `policies`: Active policy records, weekly caps, and per-delivery deduction rates.
- `subscriptions`: Weekly logs tracking how much premium the user has paid so far this week.
- `triggers` & `trigger_logs`: Logs of environmental and civil triggers captured per zone.
- `payouts`: Records of credited or pending payouts (along with status and fraud check logs).
- `fraud_logs` & `payout_jobs`: Celery background job logs and ML anomaly detection details.
- `zones` & `meta_locations`: Geospatial zone definitions and city coordinates.
- `alerts` & `delivery_logs`: 48-hour forecast alerts and micro-deduction transaction logs.
- `wallets`: Available balances, pending balances, status, and double-entry transaction ledgers.
- `wallet_transactions`: Chronological ledger entries tracking credits, holds, releases, and refunds.
- `withdrawal_requests`: Cashout details, reviewer logs, status, and bank/UPI destination fields.
- `worker_locations` & `location_history`: Live coordinates, online status, and historical logs with TTL indices.

---

## ⚙️ Core Workflows

### 1. Smart Onboarding & Risk Calculation
When a worker registers, they choose their city, zone, and shift hours. We run a `RandomForestRegressor` model (`risk_model.joblib`) to compute a personalized risk score between `0.5` and `2.5`. This score determines their weekly premium rate and maximum weekly coverage cap.

### 2. Parametric Trigger Polling (Every 10 min)
A scheduler queries active zone center coordinates:
- **OpenWeather**: Triggers active if temperature > 45°C or hourly rainfall > 12mm.
- **NewsAPI**: Scans news headlines for keywords like *strike*, *protest*, *riot*, or *curfew*.
If a threshold is crossed, a trigger is logged to `triggers_collection`.

### 3. Async Payout Pipeline & Fraud Verification
Once a trigger is logged, a Celery job is dispatched for every worker in the zone:
1. **GPS Verification**: Compares the worker's last updated location with the trigger coordinates. Rejects if they are too far away, or if coordinates are older than 30 minutes.
2. **ML Fraud Check**: An `IsolationForest` model evaluates worker metrics (claims frequency, average payout rate, activity score). Suspicious claims are flagged for manual admin review.
3. **IST Shift Adjustment**: Calculates remaining shift hours using Indian Standard Time (IST), and credits a proportional payout (`hourly_rate × remaining_shift_hours × risk_multiplier`) up to their weekly cap limit.
4. **Wallet Escrow**: Deposited directly into the worker's wallet `pending_balance` under a 24-hour review window before transferring to `available_balance` via maturity task runner.

---

## 📂 Project Directory Layout

```text
GigSurance/
├── backend/
│   ├── app/
│   │   ├── main.py              # Application entrypoint & middlewares
│   │   ├── config.py            # Pydantic environment configurations
│   │   ├── celery_app.py        # Celery task manager setup
│   │   ├── scheduler.py         # Background job registers (APScheduler)
│   │   ├── db/
│   │   │   └── database.py      # MongoDB connections and collections setups
│   │   ├── models/              # Joblib binary models & user metadata
│   │   ├── routes/              # FastAPI endpoints split by resource
│   │   ├── services/            # Core business workflows & ML models loaders
│   │   ├── schemas/             # Pydantic input/output schemas
│   │   ├── deps/                # Auth dependency checks
│   │   └── utils/               # JWT token utilities
│   ├── scripts/
│   │   ├── train_fraud_model.py # ML training script for fraud detection
│   │   └── migrate_v2_schema.py # Schema upgrade database migration script
│   ├── test_core_logic.py       # Risk and Payout verification test
│   ├── test_fraud.py            # GPS & Location validation test
│   ├── test_kyc_flow.py         # KYC & RBAC workflow test
│   ├── test_wallet.py           # Wallet and transaction ledger test
│   ├── test_tracking_analytics.py # Tracking and Geospatial analytics test
│   └── requirements.txt         # Backend python dependencies
│
└── Frontend/
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx              # React entry & Route guards
    │   ├── pages/               # Onboarding, Dashboard, Wallet, Tracking, Geospatial, etc.
    │   ├── components/          # Layout layout components & ui primitives (shadcn)
    │   ├── services/            # Axios API client calls & WebSocket connectors
    │   ├── hooks/               # Custom context hooks (e.g. useAuth)
    │   └── contexts/            # Theme & Authentication contexts
    │   └── test/                # Vitest files
    ├── tailwind.config.ts
    ├── vite.config.ts
    └── package.json             # Node frontend dependencies
```

---

## 🚀 Setting Up the Project

### Prerequisites
You will need to have these installed:
- **Node.js 18+**
- **Python 3.12+**
- **MongoDB**
- **Redis**

---

### 🔧 1. Backend Setup
1. Go to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Train the ML models:
   ```bash
   python scripts/train_fraud_model.py
   ```
5. Create a `.env` file in the `backend/` folder and fill in your keys (see `.env.example` or copy the sample below):
   ```env
   MONGO_URI=mongodb://localhost:27017/gigsurance
   JWT_SECRET=supersecretjwtkeyVpsvy05
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   OPENWEATHER_API_KEY=your_key_here
   NEWSAPI_KEY=your_key_here
   RAZORPAY_KEY_ID=your_key_here
   RAZORPAY_KEY_SECRET=your_key_here
   ```

---

### 🎨 2. Frontend Setup
1. Go to the Frontend folder:
   ```bash
   cd Frontend
   ```
2. Install dependencies:
   ```bash
   npm install --legacy-peer-deps
   ```

---

## 🏃 Running the Stack
To run the full application locally, you will need to open four terminal windows/tabs:

1. **Redis**: Ensure Redis is running:
   ```bash
   # Windows (WSL)
   wsl redis-server
   # macOS / Linux
   redis-server
   ```
2. **FastAPI Server**:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   python -m uvicorn app.main:app --reload
   ```
3. **Celery Worker**:
   ```bash
   cd backend
   .\venv\Scripts\Activate.ps1
   # Windows requires the solo pool:
   celery -A app.celery_app.celery_app worker --loglevel=info -P solo
   # macOS / Linux:
   celery -A app.celery_app.celery_app worker --loglevel=info
   ```
4. **React Dev Server**:
   ```bash
   cd Frontend
   npm run dev
   ```

---

## 🛣️ API Reference
Refer to the detailed [api_directory.txt](file:///e:/GigSurance/api_directory.txt) file in the root directory for a comprehensive list of all backend endpoints, roles, and schema structures.

---

## 🧪 Testing

### Backend Unit Tests
We use Pytest for our backend tests. Run them from the backend folder:
```bash
cd backend
.\venv\Scripts\Activate.ps1

# Run wallet ledger tests
python test_wallet.py

# Run GPS tracking & geo analytics tests
python test_tracking_analytics.py

# Run KYC & RBAC workflow tests
python test_kyc_flow.py

# Run core calculations tests
python test_core_logic.py

# Run fraud anomaly tests
python test_fraud.py
```

### Frontend Tests
Execute front-end tests:
```bash
cd Frontend
npm test                       # Run Vitest suite
npx playwright test            # Execute End-to-end integration tests
```

---

## 📊 Current Implementation Status

| Component | Status | Details |
|---|---|---|
| **Auth & Guards** | **100% Done** | JWT token extraction and role-based client side routing validations. |
| **Onboarding Pipeline** | **100% Done** | Interactive workflow linked to dynamic ML-based risk scores estimation. |
| **KYC Submission & Verification** | **100% Done** | Automated masking, format check and admin status reviews. |
| **Background Checks** | **100% Done** | APScheduler processes coordinate logs, weather parameters, and News feeds every 10 min. |
| **Async Task Workers** | **100% Done** | Celery handles worker queues through Redis to execute fraud checks and calculate payouts. |
| **ML Algorithms** | **100% Done** | IsolationForest and RandomForest estimators are fully loaded and used during processing. |
| **Payments Verification**| **100% Done** | Razorpay SDK is configured for order initialization and signature confirmation checks. |
| **Micro-Deductions** | **100% Done** | Delivery logging processes per-delivery micro-debits up to weekly limits. |
| **Wallet System** | **100% Done** | Available/locked balances, ledger double entry logs, UPI/bank cashouts, admin reviewer reviews, freeze controls. |
| **Live GPS Tracking** | **100% Done** | Websockets stream worker coordinates, Admin live map tracks online workers and reviews playback sessions. |
| **Geospatial Analytics** | **100% Done** | Density, fraud, triggers and payouts heatmaps, spatial K-Means clustering centroid markers, zone inspectors. |

---

## deployment-guide">☁️ Deployment Guide

### 🗄️ 1. Database & Cache Provisioning
1. **MongoDB**:
   * Create an account on [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
   * Deploy a free shared cluster (M0) and create a database named `gigsurance`.
   * Set up IP access lists (allowing your server IPs) and create database credentials.
   * Secure your connection string: `mongodb+srv://<user>:<password>@cluster.mongodb.net/gigsurance`.
2. **Redis & Message Broker**:
   * Deploy a managed Redis server using [Upstash](https://upstash.com/) or [Redis Enterprise Cloud].
   * Retrieve the TLS Redis URL: `rediss://:<password>@<host>:<port>`.

### 🖥️ 2. Backend API Deployment (FastAPI on Render/AWS)
To deploy the FastAPI backend to Render or AWS ECS:
1. **Dockerfile**: The backend directory includes a production Docker setup:
   ```dockerfile
   FROM python:3.12-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY . .
   RUN python scripts/train_fraud_model.py
   EXPOSE 8000
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```
2. **Web Service Setup (FastAPI)**:
   * Create a new Web Service on Render, link your GitHub repository, and choose `Docker` environment.
   * Add env variables: `MONGO_URI`, `JWT_SECRET`, `REDIS_URL`, `OPENWEATHER_API_KEY`, etc.
3. **Background Worker Setup (Celery)**:
   * Create a new **Background Worker** service on Render.
   * Choose `Docker` environment and override the run command:
     `celery -A app.celery_app.celery_app worker --loglevel=info`
   * Share the same Environment variables.

### 🎨 3. Frontend Web App Deployment (Vercel/Netlify)
1. **Build Settings**:
   * Framework: `Vite` (Vite SPA)
   * Build Command: `npm run build`
   * Output Directory: `dist`
2. **Environment Variables**:
   * Add `VITE_API_BASE` pointing to your deployed backend URL: `https://gigsurance-api.onrender.com`.
3. **Routing Configuration**:
   * If deploying to Netlify, add a `_redirects` file in the `public` directory:
     `/* /index.html 200`
   * If deploying to Vercel, add a `vercel.json` file in the root directory:
     ```json
     {
       "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
     }
     ```

### 🔒 4. Production Security Checklists
* **SSL/TLS**: Ensure both API (`https://`) and WebSocket connections (`wss://`) run exclusively over secure sockets.
* **CORS Settings**: Update `allow_origins` list inside `backend/app/main.py` from localhost endpoints to your production frontend domain.
* **Secrets**: Never commit `.env` files. Store secrets securely in the hosting environment control panels.
* **Collections Indexing**: Run `migrate_v2_schema.py` or startup commands on the production MongoDB server to initialize all geospatial `2dsphere` and user `unique` indices before taking traffic.
