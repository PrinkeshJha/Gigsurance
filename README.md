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
- [Deployment](#-deployment)
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
         |  +- Auth Routes                   |
         |  +- Policy & Subscription Routes  |
         |  +- Live Weather & Trigger Routes |
         |  +- Payments (Razorpay)           |
         |  +- Admin & Location Routes       |
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
       | . sub/logs   |         |  . Trigger Engine (every 10 min) |
       +--------------+         |  . Forecast Alerts (every 6 hrs) |
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
- **Premium Subscription**: Choose to pay weekly premiums via Razorpay, or leverage micro-deductions (deducting small amounts per delivery) up to the weekly cap.
- **Real-Time Monitoring**: Interactive dashboard mapping current weather conditions, active triggers, and risk alerts for the worker's specific zone.
- **Instant Automated Payouts**: Direct deposit logs with detailed summaries showing weather metrics or news headlines that triggered the credit.
- **Notifications Hub**: Push alerts notifying workers of payouts or predictive weather warnings (next 48 hours).

### 👔 For Admins
- **KPI Metrics Dashboard**: Tracks active policies, total premiums collected vs. payouts distributed, and claims ratios.
- **Fraud Control Center**: Real-time access to geolocation verification results and ML Isolation Forest anomaly logs.
- **Active Trigger Feed**: Complete historical and active record of weather and civil triggers across all zones.

---

## 🛠️ Tech Stack

### Backend
- **Core Framework**: FastAPI (high-performance async endpoints)
- **Task Queue**: Celery 5.4.0 (offloads heavy validation and processing)
- **Message Broker & Result Store**: Redis 5.0.0
- **Background Scheduler**: APScheduler 3.10.0 (handles weather polling and weekly resets)
- **Database Driver**: Motor (async wrapper for MongoDB)
- **Machine Learning**: Scikit-learn (RandomForest for risk scoring, Isolation Forest for fraud checks) + Joblib
- **Payments**: Razorpay SDK
- **Testing**: Pytest

### Frontend
- **Framework**: React 18 + Vite (TypeScript)
- **State & Data Fetching**: TanStack React Query + Axios
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

### 4. Micro-Deductions per Delivery
Instead of paying a lump-sum premium upfront, workers can choose pay-as-you-go coverage. Every time they log a delivery, a small fraction (`weekly_cap / expected_deliveries`) is deducted from their earnings. Once they reach their weekly cap, all subsequent deliveries are fully covered. Counters reset every Monday.

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
│   │   └── train_fraud_model.py # ML training script for fraud detection
│   ├── test_core_logic.py       # Risk and Payout verification test
│   ├── test_fraud.py            # GPS & Location validation test
│   └── requirements.txt         # Backend python dependencies
│
└── Frontend/
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx              # React entry & Route guards
    │   ├── pages/               # Onboarding, Dashboard, Monitor, Policy, Admin, etc.
    │   ├── components/          # Layout layout components & ui primitives (shadcn)
    │   ├── services/            # Axios API client calls & mockData fallbacks
    │   ├── hooks/               # Custom context hooks (e.g. useAuth)
    │   └── contexts/            # Theme & Authentication contexts
    ├── tailwind.config.ts
    ├── vite.config.ts
    └── package.json             # Node frontend dependencies
```

---

## 🚀 Setting Up the Project

### Prerequisites
You will need to have these installed:
- **Node.js 18+**
- **Python 3.10+**
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
   npm install
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

### 🔐 Authentication
- `POST /auth/register`: Create user account.
- `POST /auth/login`: Authenticate and return JWT token.
- `GET /auth/me`: Get current user details.

### 📋 Policy & Onboarding
- `POST /onboarding/calculate`: Compute dynamic risk score and weekly premium rates.
- `POST /onboarding/complete`: Save onboarded profile parameters and create user policy.
- `GET /policy/me`: Retrieve active policy contracts.
- `POST /policy/toggle`: Pause or resume active coverage.

### 💸 Subscriptions & Deductions
- `POST /subscription/record-delivery`: Charge micro-deductions for a finished delivery.
- `GET /subscription/status`: Fetch current week's accumulated deductions and cap limits.
- `GET /transactions`: Retrieve chronological logs of premium debits and payout credits.

### 🌦️ Triggers & Alerts
- `GET /triggers/live`: Fetch count of currently active alerts in the user's city.
- `GET /triggers/all`: Retrieve history logs of all environmental triggers.
- `GET /weather/{zone}`: Fetch current conditions for the specific zone.

### 💰 Payments
- `POST /payments/create-order`: Initialize Razorpay payment details.
- `POST /payments/verify`: Confirm Razorpay payment signatures.

---

## 🧪 Testing

### Backend Unit Tests
We use Pytest for our backend tests. Run them from the backend folder:
```bash
cd backend
.\venv\Scripts\Activate.ps1

# Run core logic tests
python test_core_logic.py

# Run location/fraud tests
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
| **Background Checks** | **100% Done** | APScheduler processes coordinate logs, weather parameters, and News feeds every 10 min. |
| **Async Task Workers** | **100% Done** | Celery handles worker queues through Redis to execute fraud checks and calculate payouts. |
| **ML Algorithms** | **100% Done** | IsolationForest and RandomForest estimators are fully loaded and used during processing. |
| **Payments Verification**| **100% Done** | Razorpay SDK is configured for order initialization and signature confirmation checks. |
| **Micro-Deductions** | **100% Done** | Delivery logging processes per-delivery micro-debits up to weekly limits. |
| **Auto-Renewal** | **Planned** | `reset_weekly_deductions` currently contains a mock block for automatically charging remaining premium balances through Razorpay. |
| **Admin KPI Analytics** | **Partial** | Average premiums and trigger frequency metrics are partially mocked on the dashboard route. |

---

## ☁️ Deployment

### Docker Deployment (Backend)
Use the included Docker config to containerize the FastAPI core:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Deployment
Build optimized static assets:
```bash
cd Frontend
npm run build
```
Deploy the resulting `/dist` folder directly to hosting platforms like Vercel, Netlify, or Cloudflare Pages.

---

## 🤝 Contributing
1. Create a branch: `git checkout -b feature/name`.
2. Commit changes: `git commit -m 'feat: summary description'`.
3. Push branch: `git push origin feature/name`.
4. Open a Pull Request against `main`.
5. Ensure all local tests pass before requesting a review.
