<div align="center">
  <h1>☔ GigSurance 🛡️</h1>
  <p><strong>Parametric Micro-Insurance for Gig Workers</strong></p>
  <p>
    <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI" />
    <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" alt="React" />
    <img src="https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
    <img src="https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  </p>
  <p><em>Zero-claim, real-time insurance payouts for the modern gig economy. Because waiting for claims is so last century! 🚀</em></p>
</div>

---

## 📖 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Setup and Installation](#-setup-and-installation)
- [Running the Application](#-running-the-application)
- [API Routes](#-api-routes)
- [Database Models](#-database-models)
- [Core Workflows](#-core-workflows)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🌟 Project Overview

### 🌩️ The Problem

Gig workers in food delivery, ride-sharing, and similar sectors face unpredictable income volatility driven by external shocks:
- 🥵 **Extreme heat or cold** that suppresses demand (and energy).
- 🌧️ **Heavy rainfall** that reduces order volume (and makes driving a slip-n-slide).
- 🚧 **Civil disturbances** such as strikes, protests, or lockdowns.

### 💡 The Solution

**GigSurance** provides parametric insurance designed specifically for this workforce. Forget the paperwork!
- ⚡ **Automatic Payouts** — Payouts trigger based on objective, verifiable data (weather readings, news events). No claim submission required.
- ⚖️ **Fair Calculation** — Payout = `hourly_rate × lost_hours × risk_multiplier`, capped at a weekly maximum.
- 📡 **Real-Time Monitoring** — Live dashboard displaying active triggers, weather conditions, and payout activity.
- 🛑 **Zero Fraud by Design** — Geo-verified, parametric model eliminates the possibility of fraudulent claims.

### 💎 Value Proposition

| Benefit | Description |
|---|---|
| 🤖 **Zero-Claim Automation** | Users receive compensation automatically with no documentation or proof of loss. |
| 🎯 **Precise Risk Scoring** | Premiums are personalized based on city, delivery platform, and working hours. |
| ⏱️ **Real-Time Triggers** | Payouts are processed immediately upon confirmed weather or civil events. |
| 🔍 **Transparent Pricing** | All calculations are visible to the user prior to policy purchase. |
| 📊 **Admin Analytics** | Full visibility into revenue, risk pool health, and claims activity. |

---

## ✨ Key Features

### 🛵 For Gig Workers (Users)

| Feature | Description |
|---|---|
| 📝 **Smart Onboarding** | Three-step setup: platform selection, city and zone, working hours, risk preview. |
| 🌦️ **Real-Time Monitoring** | Live trigger dashboard showing weather conditions, active incidents, and payout count. |
| 💸 **Automatic Payouts** | Compensation credited instantly when triggers occur. |
| 🔄 **Premium Management** | Weekly premium recalculation based on current risk factors. |
| 💳 **Payment Integration** | Razorpay integration for seamless premium collection. |
| 📜 **Payout History** | Detailed log of all payouts with amounts and trigger reasons. |
| ⚙️ **Profile Management** | Edit platform, city, and working hours; view earnings and risk score. |

### 👔 For Platform Admins

| Feature | Description |
|---|---|
| 📈 **KPI Dashboard** | Revenue, active users, claims ratio, and growth metrics. |
| 🧮 **Risk Pool Analytics** | Inflow (premiums) vs. outflow (payouts) visualization. |
| 🕵️ **Fraud Detection** | Manual review queue and geo-verification logs. |
| 🌍 **Trigger Monitoring** | Real-time view of all active triggers by city and zone. |

---

## 🏗️ Architecture

### 📐 System Design

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
         |  +- Policy Routes                 |
         |  +- Trigger Monitoring Routes     |
         |  +- Payout Routes                 |
         |  +- Payment Routes (Razorpay)     |
         |  +- Admin Routes                  |
         +----------+----------+-----------+
                    |          |
       +-----------+--+   +---+------------+
       |  MongoDB     |   |  External APIs |
       | (Motor Async)|   |  +- OpenWeather|
       |              |   |  +- NewsAPI    |
       | Collections: |   |  +- Razorpay   |
       | . users      |   +----------------+
       | . policies   |
       | . triggers   |
       | . payouts    |
       | . subscriptions
       +--------------+

       +----------------------------------+
       |  Background Jobs (APScheduler)   |
       |  . Trigger Engine (every 10 min) |
       |  . Premium Recalculator (weekly) |
       +----------------------------------+
```

### 🧠 Key Services

- **Risk Engine** 🎲 — Calculates a user risk score in the range 0.5–2.5, factoring in city, platform, and working hours.
- **Trigger Engine** 🌩️ — Monitors real-time conditions every 10 minutes. Detects heat (>45°C), rain (>12mm/hr), and civil disturbances. Processes payouts for all affected users.
- **Payout Service** 💰 — Calculates payouts using the formula: `hourly_rate × lost_hours × (1.0 + risk_score/200)`, capped at the user's weekly limit.
- **Premium Service** 🔄 — Manages weekly premium updates: `weekly_premium = risk_score × 10`.

---

## 🛠️ Tech Stack

### 🔙 Backend

| Component | Technology |
|---|---|
| **Framework** | FastAPI 0.113.0 |
| **Server** | Uvicorn 0.30.0 |
| **Database** | MongoDB with Motor 3.7.1 (async) |
| **Authentication** | Python-Jose + Passlib + Bcrypt (JWT) |
| **Job Scheduling** | APScheduler 3.10.0 |
| **Risk Scoring** | Scikit-learn 1.3.0 + Joblib 1.3.2 |
| **Payments** | Razorpay 1.4.1 |
| **HTTP Client** | HTTPX 0.25.0 |
| **Configuration** | Pydantic 2.8.0 |

### 🔜 Frontend

| Component | Technology |
|---|---|
| **Framework** | React 18.3.1 + TypeScript 5.8.3 |
| **Build Tool** | Vite 5.4.19 |
| **Styling** | Tailwind CSS 3.4.17 + PostCSS |
| **UI Components** | shadcn/ui + Radix UI |
| **Routing** | React Router v6.30.1 |
| **Data Fetching** | TanStack React Query 5.83.0 + Axios |
| **Charts & UI** | Recharts 2.15.4, Framer Motion 12.38.0, Lucide React |
| **Forms** | React Hook Form + Zod |
| **Testing** | Vitest 3.2.4 + Playwright 1.57.0 + React Testing Library |

### 🔌 External Integrations

- **OpenWeather API** 🌤️ — Real-time weather data
- **NewsAPI** 📰 — Civil disturbance detection
- **Razorpay** 💳 — Payment processing

---

## 📂 Repository Structure

```text
GigSurance/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── scheduler.py
│   │   ├── db/          # Database connection
│   │   ├── models/      # MongoDB models & metadata
│   │   ├── routes/      # FastAPI endpoints
│   │   ├── services/    # Business logic (Risk, Trigger, Payouts)
│   │   ├── schemas/     # Pydantic schemas for requests/responses
│   │   ├── deps/        # Dependencies (e.g., Auth)
│   │   └── utils/       # Security & helpers
│   ├── requirements.txt
│   └── tests/           # Core logic & Fraud tests
│
└── Frontend/
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── pages/       # React pages (Dashboard, Admin, etc.)
    │   ├── components/  # Reusable UI components
    │   ├── services/    # API calls (Axios)
    │   ├── hooks/       # Custom React hooks
    │   ├── contexts/    # React Context (Auth, Theme)
    │   └── lib/         # Utility functions
    ├── vite.config.ts
    ├── tailwind.config.ts
    └── package.json
```

---

## 🚀 Setup and Installation

### 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local instance or cloud)
- Git

### 🔧 Backend Setup

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\Activate.ps1   
   # macOS / Linux
   source venv/bin/activate       
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   MONGODB_URL=mongodb://localhost:27017/gigsurance
   JWT_SECRET=your-secret-key-here
   OPENWEATHER_API_KEY=your-openweather-key
   NEWSAPI_KEY=your-newsapi-key
   RAZORPAY_KEY_ID=your-razorpay-key
   RAZORPAY_KEY_SECRET=your-razorpay-secret
   ```

5. **Start the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   *API available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.*

### 🎨 Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd Frontend
   npm install
   ```

2. **Start the development server:**
   ```bash
   npm run dev
   ```
   *Application available at `http://localhost:5173`.*

---

## 🏃 Running the Application

**Terminal 1 — Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd Frontend
npm run dev
```

### 🚢 Production Build

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
npm run build && npm run preview
```

---

## 🛣️ API Routes

### 🔐 Authentication
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/register` | Register with name, email, mobile, PAN, and password |
| `POST` | `/auth/login` | Login with PAN and password; returns JWT token |

### 📋 Policy and Onboarding
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/onboarding/calculate` | Calculate risk score and premium |
| `POST` | `/onboarding/complete` | Create policy after onboarding |
| `GET` | `/policy/me` | Retrieve the authenticated user's policy |
| `POST` | `/policy/toggle` | Activate or deactivate a policy |

### 📡 Real-Time Monitoring
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/triggers/live` | Active trigger count by severity |
| `GET` | `/triggers/all` | All recent triggers |
| `GET` | `/triggers/{zone}` | Triggers for a specific zone |

### 💸 Payouts & Payments
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/payouts/history` | Authenticated user's payout history |
| `GET` | `/payouts/{user_id}` | Admin: look up payouts for a specific user |
| `POST` | `/payments/create-order` | Create a Razorpay order |
| `POST` | `/payments/verify` | Verify payment signature |

### 👤 User Data & Admin
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/transactions/` | Combined payouts and premium debits |
| `GET` | `/analytics/` | User analytics (earnings saved, trigger frequency) |
| `GET` | `/admin/kpis` | Dashboard metrics (revenue, growth, claims ratio) |
| `GET` | `/fraud/logs` | Fraud detection logs |

---

## 🗄️ Database Models

### 👤 Users Collection
```json
{
  "_id": "ObjectId",
  "name": "Raj Kumar",
  "email": "raj@example.com",
  "mobile": "+919876543210",
  "pan": "AAAPA5055K",
  "platform": "Blinkit",
  "city": "Delhi",
  "zone": "Central Delhi",
  "working_hours": { "start": 7, "end": 22 },
  "hourly_rate": 25,
  "risk_score": 1.5,
  "weekly_premium": 15.0,
  "weekly_cap": 120.0,
  "role": "user",
  "is_onboarded": true,
  "created_at": "2026-05-01T10:30:00Z"
}
```

*See `backend/app/models` for full policy, trigger, and payout collection schemas.*

---

## ⚙️ Core Workflows

### 1️⃣ User Onboarding
```text
User Registers 
  → Select delivery platform 
  → Select city and zone 
  → Set working hours
  → 🎲 Risk Engine calculates risk score
  → 💰 Premium generated (risk_score × 10)
  → 🛡️ Policy created and ready for payment
```

### 2️⃣ Real-Time Trigger and Payout (Every 10 min)
```text
APScheduler fires 
  → Fetch weather (OpenWeather) & news (NewsAPI)
  → Evaluate conditions:
      🔥 Heat: > 45°C
      🌧️ Rain: > 12mm/hr
      🚧 Civil: keywords (strike, protest, riot)
  → If triggered:
      Log to DB & Identify affected users
      🕵️ Fraud check (location verification, duplicate checks)
      💸 Calculate payout: hourly_rate × lost_hours × risk multiplier
      🔔 Record payout & dispatch notification
```

### 3️⃣ Weekly Premium Recalculation (Every Sunday)
```text
For each onboarded user:
  → Recalculate risk score
  → Update new premium and weekly cap
  → Sync with MongoDB collections
```

---

## 🧪 Testing

### Backend
```bash
cd backend
pytest                         # Run all tests
pytest test_core_logic.py -v   # Core logic tests
pytest test_fraud.py -v        # Fraud detection tests
```

### Frontend
```bash
cd Frontend
npm test                       # Run all tests
npm run test:watch             # Watch mode
npx playwright test            # End-to-end tests
```

---

## ☁️ Deployment

### Backend (Docker)
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
*Supported platforms: AWS EC2, GCP Cloud Run, Railway, Render, Heroku.*

### Frontend
```bash
cd Frontend && npm run build
```
*Supported platforms: Vercel (recommended), Netlify, Cloudflare Pages, AWS S3 + CloudFront.*

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:
1. Branch off main: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m 'feat: added awesome new feature'`
3. Push and open a pull request against `main`
4. Ensure all tests pass before requesting a review.

**Code Standards:**
- **Backend:** Follow PEP 8; use type hints throughout.
- **Frontend:** Use TypeScript; ESLint configuration is included.

---

## 📚 Additional Resources

- **API Documentation:** Swagger UI at `http://localhost:8000/docs`
- **Project Analysis:** See `project_analysis.txt` for extended architecture notes
- **CI/CD:** Pipeline defined in `.github/workflows/ci.yml`

---

<div align="center">
  <p>Made with ❤️ for gig workers.</p>
  <p><strong>GigSurance</strong> — All rights reserved.</p>
</div>
