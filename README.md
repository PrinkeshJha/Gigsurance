# 🛡️ GigSurance

**Parametric Micro-Insurance for Gig Workers**

GigSurance is a real-time, zero-claim insurance platform protecting gig workers from income loss due to external factors like extreme weather and civil disturbances. Using parametric insurance mechanics, eligible users receive **automatic payouts** when a trigger occurs—no claim filing required.

---

## 📋 Table of Contents

- [Project Overview](#-project-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Repository Structure](#-repository-structure)
- [Setup & Installation](#-setup--installation)
- [Running the Application](#-running-the-application)
- [API Routes](#-api-routes)
- [Database Models](#-database-models)
- [Core Workflows](#-core-workflows)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Contributing](#-contributing)

---

## 🎯 Project Overview

### Problem
Gig workers (food delivery, ride-sharing, etc.) face income volatility due to external shocks:
- Extreme heat/cold affecting demand
- Heavy rainfall reducing orders
- Civil disturbances (strikes, lockdowns)

### Solution
**GigSurance** provides parametric insurance that:
- **Automatic Payouts**: No claim filing needed—payouts trigger based on objective data (weather, news)
- **Fair Calculation**: Payout = hourly_rate × lost_hours × risk_multiplier (capped weekly)
- **Real-Time Monitoring**: Live dashboard showing active triggers and weather
- **Zero Fraud Claims**: Geo-verified, parametric model eliminates fraudulent claims

### Value Proposition
- 💰 **Zero-Claim Automation**: Users don't need to file claims or provide proof of losses
- 📍 **Precise Risk Scoring**: Different premiums based on city, platform, and working hours
- 🌦️ **Real-Time Triggers**: Automatic payouts when weather/civil events occur
- 🔐 **Transparent & Fair**: All calculations visible to users before purchase
- 📊 **Admin Analytics**: Complete insights into revenue, risk pool, and claims

---

## ⚡ Key Features

### User Features
| Feature | Description |
|---------|-------------|
| **Smart Onboarding** | 3-step setup: Platform selection → City/Zone → Working hours → Risk preview |
| **Real-Time Monitoring** | Live trigger dashboard showing weather, active incidents, payout count |
| **Automatic Payouts** | Receive compensation instantly when triggers occur (no manual claim) |
| **Premium Management** | Weekly premium recalculation based on risk factors |
| **Payment Integration** | Razorpay integration for seamless premium payments |
| **Payout History** | Detailed history of all payouts with amounts and trigger reasons |
| **Profile Management** | Edit platform, city, working hours; view earnings and risk score |

### Admin Features
| Feature | Description |
|---------|-------------|
| **KPI Dashboard** | Revenue, active users, claims ratio, growth metrics |
| **Risk Pool Analytics** | Inflow (premiums) vs. outflow (payouts) visualization |
| **Fraud Detection** | Manual review queue, geo-verification logs |
| **Trigger Monitoring** | Real-time view of all active triggers by city/zone |

---

## 🏗️ Architecture

### System Design

```
┌─────────────────────────────────────────────────────┐
│              Frontend (React + TypeScript)          │
│  DashboardPage, MonitorPage, AnalyticsPage, etc.   │
└────────────────────────┬────────────────────────────┘
                         │
                    Axios + React Query
                         │
        ┌────────────────▼────────────────┐
        │  Backend API (FastAPI)          │
        │  ├─ Auth Routes                 │
        │  ├─ Policy Routes               │
        │  ├─ Trigger Monitoring Routes   │
        │  ├─ Payout Routes               │
        │  ├─ Payment Routes (Razorpay)   │
        │  └─ Admin Routes                │
        └────────────┬──────────────┬─────┘
                     │              │
        ┌────────────▼──┐  ┌────────▼──────┐
        │  MongoDB      │  │  External APIs │
        │  (Motor Async)│  │  ├─ OpenWeather│
        │               │  │  ├─ NewsAPI    │
        │  Collections: │  │  └─ Razorpay   │
        │  • users      │  └────────────────┘
        │  • policies   │
        │  • triggers   │
        │  • payouts    │
        │  • subscriptions
        └───────────────┘

        ┌────────────────────────────────┐
        │  Background Jobs (APScheduler) │
        │  • Trigger Engine (every 10 min)
        │  • Premium Recalculator (weekly)
        └────────────────────────────────┘
```

### Key Services

1. **Risk Engine** - Calculates user risk score (0.5-2.5 range)
   - City factor, platform factor, working hours factor
   
2. **Trigger Engine** - Monitors real-time triggers (every 10 mins)
   - Heat (>45°C), Rain (>12mm/hr), Civil disturbances
   - Processes payouts for affected users
   
3. **Payout Service** - Calculates fair payouts
   - Formula: `hourly_rate × lost_hours × (1.0 + risk_score/200)`, capped at weekly_cap
   
4. **Premium Service** - Manages weekly premium updates
   - Formula: `weekly_premium = risk_score × 10`

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.113.0 (async Python web framework)
- **Server**: Uvicorn 0.30.0 (ASGI server)
- **Database**: MongoDB with Motor 3.7.1 (async driver)
- **Authentication**: Python-Jose + Passlib + Bcrypt (JWT + secure hashing)
- **Job Scheduling**: APScheduler 3.10.0 (background tasks)
- **ML/Risk Scoring**: Scikit-learn 1.3.0 + Joblib 1.3.2 (joblib model)
- **Payments**: Razorpay 1.4.1 (payment gateway)
- **HTTP Client**: HTTPX 0.25.0 (async HTTP requests)
- **Config**: Pydantic 2.8.0 (validation & settings)

### Frontend
- **Framework**: React 18.3.1 + TypeScript 5.8.3
- **Build Tool**: Vite 5.4.19 (fast bundler)
- **Styling**: Tailwind CSS 3.4.17 + PostCSS
- **UI Components**: shadcn/ui + Radix UI (accessible, customizable)
- **Routing**: React Router v6.30.1
- **HTTP Client**: Axios 1.14.0
- **Data Fetching**: TanStack React Query 5.83.0 (server state)
- **Charts**: Recharts 2.15.4 (data visualization)
- **Animations**: Framer Motion 12.38.0
- **Icons**: Lucide React 0.462.0
- **Forms**: React Hook Form + Zod validation
- **Testing**: Vitest 3.2.4 + Playwright 1.57.0 + React Testing Library

### External Integrations
- **OpenWeather API** - Real-time weather data
- **NewsAPI** - Civil disturbance detection
- **Razorpay** - Payment processing

---

## 📁 Repository Structure

```
GigSurance/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── main.py                  # App initialization & route registration
│   │   ├── config.py                # Configuration & settings
│   │   ├── scheduler.py             # APScheduler setup
│   │   ├── db/
│   │   │   └── database.py          # MongoDB connection
│   │   ├── models/
│   │   │   ├── user.py              # User model
│   │   │   └── meta.py              # Meta config
│   │   ├── routes/                  # API endpoints
│   │   │   ├── auth.py              # Register, login
│   │   │   ├── onboarding.py        # Risk calculation
│   │   │   ├── policy.py            # Policy management
│   │   │   ├── triggers.py          # Trigger monitoring
│   │   │   ├── payouts.py           # Payout history
│   │   │   ├── payments.py          # Razorpay integration
│   │   │   ├── premium.py           # Premium info
│   │   │   ├── analytics.py         # User analytics
│   │   │   ├── admin.py             # Admin KPIs
│   │   │   ├── fraud.py             # Fraud logs
│   │   │   ├── notifications.py     # User notifications
│   │   │   └── [other routes]
│   │   ├── services/
│   │   │   ├── auth.py              # Auth business logic
│   │   │   ├── risk_engine.py       # Risk scoring algorithm
│   │   │   ├── trigger_engine.py    # Trigger detection & processing
│   │   │   ├── payout_service.py    # Payout calculation
│   │   │   ├── premium_service.py   # Premium management
│   │   │   ├── risk_model.py        # ML-based risk scoring
│   │   │   └── [other services]
│   │   ├── schemas/
│   │   │   ├── auth.py              # Request/response models
│   │   │   └── responses.py
│   │   ├── deps/
│   │   │   └── auth.py              # JWT dependency
│   │   └── utils/
│   │       └── security.py          # Security utilities
│   ├── requirements.txt             # Python dependencies
│   ├── test_core_logic.py           # Backend unit tests
│   └── test_fraud.py                # Fraud detection tests
│
├── Frontend/                         # React + Vite frontend
│   ├── src/
│   │   ├── main.tsx                 # App entry point
│   │   ├── App.tsx                  # Main app component
│   │   ├── pages/                   # Page components
│   │   │   ├── DashboardPage.tsx    # Main dashboard
│   │   │   ├── MonitorPage.tsx      # Live trigger monitoring
│   │   │   ├── OnboardingPage.tsx   # User setup
│   │   │   ├── ProfilePage.tsx      # User profile
│   │   │   ├── PaymentsPage.tsx     # Premium payments
│   │   │   ├── AnalyticsPage.tsx    # User analytics
│   │   │   ├── AdminPage.tsx        # Admin dashboard
│   │   │   ├── HistoryPage.tsx      # Payout history
│   │   │   └── [other pages]
│   │   ├── components/              # Reusable components
│   │   │   ├── layout/              # Layout components
│   │   │   ├── shared/              # Shared UI components
│   │   │   └── ui/                  # shadcn/ui components
│   │   ├── services/                # API services
│   │   │   ├── api.ts               # Axios API client
│   │   │   └── mockData.ts
│   │   ├── hooks/                   # Custom hooks
│   │   │   ├── useAuth.ts           # Auth hook
│   │   │   └── use-toast.ts         # Toast hook
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx      # Auth state
│   │   └── lib/
│   │       └── utils.ts             # Utility functions
│   ├── vite.config.ts               # Vite configuration
│   ├── tailwind.config.ts           # Tailwind configuration
│   ├── package.json                 # Dependencies
│   └── vitest.config.ts             # Test configuration
│
├── .gitignore                        # Git ignore rules
├── .gitattributes                    # Git attributes (line endings)
├── README.md                         # This file
└── project_analysis.txt              # Project documentation
```

---

## 🚀 Setup & Installation

### Prerequisites
- **Python 3.10+** (for backend)
- **Node.js 18+** (for frontend)
- **MongoDB** (local or cloud instance)
- **Git**

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create a Python virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Create a `.env` file in the `backend/` directory:
   ```env
   MONGODB_URL=mongodb://localhost:27017/gigsurance
   JWT_SECRET=your-secret-key-here
   OPENWEATHER_API_KEY=your-openweather-key
   NEWSAPI_KEY=your-newsapi-key
   RAZORPAY_KEY_ID=your-razorpay-key
   RAZORPAY_KEY_SECRET=your-razorpay-secret
   ```

5. **Run the backend server:**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
   Backend will be available at: `http://localhost:8000`
   API docs (Swagger): `http://localhost:8000/docs`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd Frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment (optional):**
   Create a `.env.local` file for API configuration if needed.

4. **Run the development server:**
   ```bash
   npm run dev
   ```
   Frontend will be available at: `http://localhost:5173`

---

## 🎮 Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd Frontend
npm run dev
```

### Production Build

**Backend:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend:**
```bash
npm run build
npm run preview
```

---

## 🔌 API Routes

### Authentication
- `POST /auth/register` - User registration (name, email, mobile, PAN, password)
- `POST /auth/login` - Login with PAN + password, returns JWT token

### Policy & Onboarding
- `POST /onboarding/calculate` - Calculate risk score & premium
- `POST /onboarding/complete` - Create policy after onboarding
- `GET /policy/me` - Get user's policy details
- `POST /policy/toggle` - Activate/deactivate policy

### Real-Time Monitoring
- `GET /triggers/live` - Active triggers count by severity
- `GET /triggers/all` - All recent triggers
- `GET /triggers/{zone}` - Triggers for specific zone

### Payouts
- `GET /payouts/history` - User's payout history
- `GET /payouts/{user_id}` - Admin: lookup user payouts

### Payments
- `POST /payments/create-order` - Create Razorpay order
- `POST /payments/verify` - Verify payment signature

### User Data
- `GET /transactions/` - Combined payouts + premium debits
- `GET /analytics/` - User analytics (earnings saved, trigger frequency)
- `GET /notifications/` - User notifications

### Admin
- `GET /admin/kpis` - Dashboard metrics (revenue, growth, claims ratio)
- `GET /fraud/logs` - Fraud detection logs

---

## 💾 Database Models

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
  "working_hours": {"start": 7, "end": 22},
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

### Payouts Collection ⭐
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

## 🔄 Core Workflows

### Workflow 1: User Onboarding
```
1. User Registers
   ↓
2. Select Delivery Platform (Blinkit, Zepto, Swiggy, etc.)
   ↓
3. Select City & Zone
   ↓
4. Set Working Hours
   ↓
5. Risk Engine Calculates Risk Score
   ↓
6. Generate Premium (risk_score × 10)
   ↓
7. Set Weekly Cap (premium × 8)
   ↓
8. Create Policy
   ↓
9. Ready for Payments
```

### Workflow 2: Real-Time Trigger & Payout (Every 10 minutes)
```
1. APScheduler Triggers
   ↓
2. Fetch Real-Time Weather (OpenWeather API)
   ↓
3. Fetch News Data (NewsAPI)
   ↓
4. Check Conditions:
   - Heat: Temp > 45°C?
   - Rain: Rainfall > 12mm/hr?
   - Civil: Keywords (bandh, strike, protest, riot)?
   ↓
5. If Triggered:
   - Log to triggers_collection
   - Find affected users (in that city + active policy)
   ↓
6. Fraud Check:
   - Verify user location matches city
   - Check for duplicate payouts in same window
   ↓
7. Calculate Payout:
   - lost_hours = hours from trigger to end of shift
   - amount = hourly_rate × lost_hours × (1.0 + risk_score/200)
   - cap at weekly_cap
   ↓
8. Record Payout:
   - Save to payouts_collection
   - Update subscription weekly total
   ↓
9. Send Notification & Notification Page Update
```

### Workflow 3: Payment Processing (Razorpay)
```
1. User Initiates Premium Payment
   ↓
2. Create Razorpay Order (amount, user_id)
   ↓
3. User Completes Payment on Razorpay
   ↓
4. Verify Payment Signature
   ↓
5. Mark Subscription Active
   ↓
6. Update Policy Status
```

### Workflow 4: Weekly Premium Recalculation
```
Every Sunday (via APScheduler):
   ↓
1. For each onboarded user:
   - Recalculate risk_score (based on current factors)
   - new_premium = risk_score × 10
   - new_cap = premium × 8
   ↓
2. Update:
   - users_collection (risk_score, weekly_premium)
   - policies_collection (weekly_premium, weekly_cap)
   - premium_history_collection (log for analytics)
```

---

## 🧪 Testing

### Backend Tests

Run all backend tests:
```bash
cd backend
pytest
```

Run specific test file:
```bash
pytest test_core_logic.py -v
pytest test_fraud.py -v
```

### Frontend Tests

Run all frontend tests:
```bash
cd Frontend
npm test
```

Run tests in watch mode:
```bash
npm run test:watch
```

Run specific test file:
```bash
npm test -- example.test.ts
```

Run Playwright E2E tests:
```bash
npx playwright test
```

---

## 🌐 Deployment

### Backend Deployment

**Using Docker:**
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt
COPY backend/app ./app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deployment Platforms:**
- Heroku: `git push heroku main`
- AWS EC2 / EB
- GCP Cloud Run
- Railway, Render, etc.

### Frontend Deployment

**Build for production:**
```bash
cd Frontend
npm run build
```

**Deployment Platforms:**
- Vercel (recommended for Vite + React)
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Cloudflare Pages

### Environment Variables

**Backend (.env):**
```env
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/gigsurance
JWT_SECRET=your-production-secret-key
OPENWEATHER_API_KEY=your-key
NEWSAPI_KEY=your-key
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
```

**Frontend (.env.production):**
```env
VITE_API_BASE_URL=https://api.gigsurance.com
```

---

## 🤝 Contributing

### Code Standards
- **Backend**: Follow PEP 8, use type hints
- **Frontend**: Use TypeScript, ESLint configuration included
- **Commits**: Use conventional commits (feat:, fix:, docs:, etc.)

### Pull Request Process
1. Create a feature branch: `git checkout -b feature/your-feature`
2. Commit changes: `git commit -m 'feat: add new feature'`
3. Push to origin: `git push origin feature/your-feature`
4. Open a pull request against `main`
5. Ensure all tests pass
6. Request review from maintainers

### Running CI Locally
```bash
# Backend lint & tests
cd backend
pytest
python -m flake8 app/

# Frontend lint & tests
cd Frontend
npm run lint
npm test
```

---

## 📝 License

GigSurance is proprietary software. All rights reserved.

---

## 📞 Contact & Support

For questions or issues:
- Open an issue on GitHub
- Contact the development team
- Check `project_analysis.txt` for additional technical documentation

---

## 📚 Additional Resources

- **Backend API Docs**: Available at `http://localhost:8000/docs` (Swagger UI)
- **Project Analysis**: See `project_analysis.txt` for detailed architecture notes
- **GitHub Actions**: CI/CD pipeline defined in `.github/workflows/ci.yml`

---

**Made with ❤️ by the GigSurance Team**
