

# GigSurance

**Parametric Micro-Insurance for Gig Workers**

GigSurance is a real-time, zero-claim insurance platform that protects gig workers from income loss caused by external factors such as extreme weather and civil disturbances. Using parametric insurance mechanics, eligible users receive automatic payouts when a predefined trigger occurs — no claim filing required.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Repository Structure](#repository-structure)
- [Setup and Installation](#setup-and-installation)
- [Running the Application](#running-the-application)
- [API Routes](#api-routes)
- [Database Models](#database-models)
- [Core Workflows](#core-workflows)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)

---

## Project Overview

### Problem

Gig workers in food delivery, ride-sharing, and similar sectors face unpredictable income volatility driven by external shocks:

- Extreme heat or cold that suppresses demand
- Heavy rainfall that reduces order volume
- Civil disturbances such as strikes, protests, or lockdowns

### Solution

GigSurance provides parametric insurance designed specifically for this workforce:

- **Automatic Payouts** — Payouts trigger based on objective, verifiable data (weather readings, news events). No claim submission required.
- **Fair Calculation** — Payout = `hourly_rate x lost_hours x risk_multiplier`, capped at a weekly maximum.
- **Real-Time Monitoring** — Live dashboard displaying active triggers, weather conditions, and payout activity.
- **Zero Fraud by Design** — Geo-verified, parametric model eliminates the possibility of fraudulent claims.

### Value Proposition

| Benefit | Description |
|---|---|
| Zero-Claim Automation | Users receive compensation automatically with no documentation or proof of loss |
| Precise Risk Scoring | Premiums are personalised based on city, delivery platform, and working hours |
| Real-Time Triggers | Payouts are processed immediately upon confirmed weather or civil events |
| Transparent Pricing | All calculations are visible to the user prior to policy purchase |
| Admin Analytics | Full visibility into revenue, risk pool health, and claims activity |

---

## Key Features

### User Features

| Feature | Description |
|---|---|
| Smart Onboarding | Three-step setup: platform selection, city and zone, working hours, risk preview |
| Real-Time Monitoring | Live trigger dashboard showing weather conditions, active incidents, and payout count |
| Automatic Payouts | Compensation credited instantly when triggers occur |
| Premium Management | Weekly premium recalculation based on current risk factors |
| Payment Integration | Razorpay integration for seamless premium collection |
| Payout History | Detailed log of all payouts with amounts and trigger reasons |
| Profile Management | Edit platform, city, and working hours; view earnings and risk score |

### Admin Features

| Feature | Description |
|---|---|
| KPI Dashboard | Revenue, active users, claims ratio, and growth metrics |
| Risk Pool Analytics | Inflow (premiums) vs. outflow (payouts) visualisation |
| Fraud Detection | Manual review queue and geo-verification logs |
| Trigger Monitoring | Real-time view of all active triggers by city and zone |

---

## Architecture

### System Design

```
+-----------------------------------------------------+
|           Frontend (React + TypeScript)             |
|  DashboardPage, MonitorPage, AnalyticsPage, etc.   |
+------------------------+----------------------------+
                         |
                  Axios + React Query
                         |
         +--------------+-+------------------+
         |  Backend API (FastAPI)            |
         |  +- Auth Routes                  |
         |  +- Policy Routes                |
         |  +- Trigger Monitoring Routes    |
         |  +- Payout Routes               |
         |  +- Payment Routes (Razorpay)   |
         |  +- Admin Routes                |
         +----------+----------+-----------+
                    |          |
       +-----------+--+   +---+------------+
       |  MongoDB      |   |  External APIs |
       |  (Motor Async)|   |  +- OpenWeather|
       |               |   |  +- NewsAPI    |
       |  Collections: |   |  +- Razorpay   |
       |  . users      |   +----------------+
       |  . policies   |
       |  . triggers   |
       |  . payouts    |
       |  . subscriptions
       +---------------+

       +----------------------------------+
       |  Background Jobs (APScheduler)  |
       |  . Trigger Engine (every 10 min)|
       |  . Premium Recalculator (weekly)|
       +----------------------------------+
```

### Key Services

**Risk Engine** — Calculates a user risk score in the range 0.5–2.5, factoring in city, platform, and working hours.

**Trigger Engine** — Monitors real-time conditions every 10 minutes. Detects heat (>45°C), rain (>12mm/hr), and civil disturbances. Processes payouts for all affected users.

**Payout Service** — Calculates payouts using the formula: `hourly_rate x lost_hours x (1.0 + risk_score/200)`, capped at the user's weekly limit.

**Premium Service** — Manages weekly premium updates: `weekly_premium = risk_score x 10`.

---

## Tech Stack

### Backend

| Component | Technology |
|---|---|
| Framework | FastAPI 0.113.0 |
| Server | Uvicorn 0.30.0 |
| Database | MongoDB with Motor 3.7.1 (async) |
| Authentication | Python-Jose + Passlib + Bcrypt (JWT) |
| Job Scheduling | APScheduler 3.10.0 |
| Risk Scoring | Scikit-learn 1.3.0 + Joblib 1.3.2 |
| Payments | Razorpay 1.4.1 |
| HTTP Client | HTTPX 0.25.0 |
| Configuration | Pydantic 2.8.0 |

### Frontend

| Component | Technology |
|---|---|
| Framework | React 18.3.1 + TypeScript 5.8.3 |
| Build Tool | Vite 5.4.19 |
| Styling | Tailwind CSS 3.4.17 + PostCSS |
| UI Components | shadcn/ui + Radix UI |
| Routing | React Router v6.30.1 |
| HTTP Client | Axios 1.14.0 |
| Data Fetching | TanStack React Query 5.83.0 |
| Charts | Recharts 2.15.4 |
| Animations | Framer Motion 12.38.0 |
| Icons | Lucide React 0.462.0 |
| Forms | React Hook Form + Zod |
| Testing | Vitest 3.2.4 + Playwright 1.57.0 + React Testing Library |

### External Integrations

- **OpenWeather API** — Real-time weather data
- **NewsAPI** — Civil disturbance detection
- **Razorpay** — Payment processing

---

## Repository Structure

```
GigSurance/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── scheduler.py
│   │   ├── db/
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   └── meta.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── onboarding.py
│   │   │   ├── policy.py
│   │   │   ├── triggers.py
│   │   │   ├── payouts.py
│   │   │   ├── payments.py
│   │   │   ├── premium.py
│   │   │   ├── analytics.py
│   │   │   ├── admin.py
│   │   │   ├── fraud.py
│   │   │   └── notifications.py
│   │   ├── services/
│   │   │   ├── auth.py
│   │   │   ├── risk_engine.py
│   │   │   ├── trigger_engine.py
│   │   │   ├── payout_service.py
│   │   │   ├── premium_service.py
│   │   │   └── risk_model.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── responses.py
│   │   ├── deps/
│   │   │   └── auth.py
│   │   └── utils/
│   │       └── security.py
│   ├── requirements.txt
│   ├── test_core_logic.py
│   └── test_fraud.py
│
└── Frontend/
    ├── src/
    │   ├── main.tsx
    │   ├── App.tsx
    │   ├── pages/
    │   ├── components/
    │   ├── services/
    │   ├── hooks/
    │   ├── contexts/
    │   └── lib/
    ├── vite.config.ts
    ├── tailwind.config.ts
    ├── package.json
    └── vitest.config.ts
```

---

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- MongoDB (local instance or cloud)
- Git

### Backend Setup

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1   # Windows
   source venv/bin/activate       # macOS / Linux
   ```

3. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the `backend/` directory:

   ```env
   MONGODB_URL=mongodb://localhost:27017/gigsurance
   JWT_SECRET=your-secret-key-here
   OPENWEATHER_API_KEY=your-openweather-key
   NEWSAPI_KEY=your-newsapi-key
   RAZORPAY_KEY_ID=your-razorpay-key
   RAZORPAY_KEY_SECRET=your-razorpay-secret
   ```

5. Start the backend server:

   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   API available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory and install dependencies:

   ```bash
   cd Frontend
   npm install
   ```

2. Start the development server:

   ```bash
   npm run dev
   ```

   Application available at `http://localhost:5173`.

---

## Running the Application

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

### Production Build

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend
npm run build && npm run preview
```

---

## API Routes

### Authentication
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register with name, email, mobile, PAN, and password |
| POST | `/auth/login` | Login with PAN and password; returns JWT token |

### Policy and Onboarding
| Method | Endpoint | Description |
|---|---|---|
| POST | `/onboarding/calculate` | Calculate risk score and premium |
| POST | `/onboarding/complete` | Create policy after onboarding |
| GET | `/policy/me` | Retrieve the authenticated user's policy |
| POST | `/policy/toggle` | Activate or deactivate a policy |

### Real-Time Monitoring
| Method | Endpoint | Description |
|---|---|---|
| GET | `/triggers/live` | Active trigger count by severity |
| GET | `/triggers/all` | All recent triggers |
| GET | `/triggers/{zone}` | Triggers for a specific zone |

### Payouts
| Method | Endpoint | Description |
|---|---|---|
| GET | `/payouts/history` | Authenticated user's payout history |
| GET | `/payouts/{user_id}` | Admin: look up payouts for a specific user |

### Payments
| Method | Endpoint | Description |
|---|---|---|
| POST | `/payments/create-order` | Create a Razorpay order |
| POST | `/payments/verify` | Verify payment signature |

### User Data
| Method | Endpoint | Description |
|---|---|---|
| GET | `/transactions/` | Combined payouts and premium debits |
| GET | `/analytics/` | User analytics (earnings saved, trigger frequency) |
| GET | `/notifications/` | User notifications |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| GET | `/admin/kpis` | Dashboard metrics (revenue, growth, claims ratio) |
| GET | `/fraud/logs` | Fraud detection logs |

---

## Database Models

### Users Collection
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

### Policies Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "status": "active",
  "weekly_premium": 15.0,
  "weekly_cap": 120.0,
  "risk_score": 1.5,
  "created_at": "2026-05-01T10:30:00Z"
}
```

### Triggers Collection
```json
{
  "_id": "ObjectId",
  "type": "heat",
  "city": "Delhi",
  "zone": "Central Delhi",
  "value": 46.5,
  "timestamp": "2026-05-02T14:30:00Z",
  "status": "active"
}
```

### Payouts Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "policy_id": "ObjectId",
  "trigger_id": "ObjectId",
  "amount": 75.50,
  "lost_hours": 3,
  "reason": "Heat trigger (>45°C)",
  "status": "credited",
  "fraud_status": "passed",
  "created_at": "2026-05-02T15:00:00Z"
}
```

---

## Core Workflows

### Workflow 1: User Onboarding

```
User Registers
  -> Select delivery platform
  -> Select city and zone
  -> Set working hours
  -> Risk Engine calculates risk score
  -> Premium generated: risk_score x 10
  -> Weekly cap set: premium x 8
  -> Policy created and ready for payment
```

### Workflow 2: Real-Time Trigger and Payout (every 10 minutes)

```
APScheduler fires
  -> Fetch weather from OpenWeather API
  -> Fetch news from NewsAPI
  -> Evaluate conditions:
       Heat:  temperature > 45°C
       Rain:  rainfall > 12mm/hr
       Civil: keywords matched (bandh, strike, protest, riot)
  -> If triggered:
       Log to triggers collection
       Identify affected users (matching city + active policy)
  -> Fraud check:
       Verify location matches registered city
       Check for duplicate payouts in same window
  -> Calculate payout:
       lost_hours = hours from trigger to end of shift
       amount = hourly_rate x lost_hours x (1.0 + risk_score/200)
       cap at weekly_cap
  -> Record payout and dispatch notification
```

### Workflow 3: Payment Processing

```
User initiates premium payment
  -> Create Razorpay order
  -> User completes payment
  -> Verify payment signature
  -> Mark subscription active and update policy status
```

### Workflow 4: Weekly Premium Recalculation (every Sunday)

```
For each onboarded user:
  -> Recalculate risk score
  -> new_premium = risk_score x 10
  -> new_cap = premium x 8
  -> Update users, policies, and premium history collections
```

---

## Testing

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

## Deployment

### Backend

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Supported platforms: AWS EC2 / Elastic Beanstalk, GCP Cloud Run, Railway, Render, Heroku.

### Frontend

```bash
cd Frontend && npm run build
```

Supported platforms: Vercel (recommended), Netlify, Cloudflare Pages, AWS S3 + CloudFront.

### Environment Variables

**Backend (`backend/.env`):**
```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/gigsurance
JWT_SECRET=your-production-secret-key
OPENWEATHER_API_KEY=your-key
NEWSAPI_KEY=your-key
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
```

**Frontend (`Frontend/.env.production`):**
```env
VITE_API_BASE_URL=https://api.gigsurance.com
```

---

## Contributing

### Code Standards

- **Backend:** Follow PEP 8; use type hints throughout.
- **Frontend:** Use TypeScript; ESLint configuration is included.
- **Commits:** Use conventional commit messages (`feat:`, `fix:`, `docs:`, `chore:`, etc.).

### Pull Request Process

1. Branch off main: `git checkout -b feature/your-feature`
2. Commit your changes: `git commit -m 'feat: description'`
3. Push and open a pull request against `main`
4. Ensure all tests pass before requesting a review

### Running CI Locally

```bash
# Backend
cd backend && pytest && python -m flake8 app/

# Frontend
cd Frontend && npm run lint && npm test
```

---

## Additional Resources

- **API Documentation:** Swagger UI at `http://localhost:8000/docs`
- **Project Analysis:** See `project_analysis.txt` for extended architecture notes
- **CI/CD:** Pipeline defined in `.github/workflows/ci.yml`

---

GigSurance — All rights reserved.
