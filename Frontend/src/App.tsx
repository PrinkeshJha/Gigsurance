import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { createBrowserRouter, RouterProvider, Outlet, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import { useAuth } from "@/hooks/useAuth";
import AppLayout from "@/components/layout/AppLayout";

import LandingPage from "./pages/LandingPage";
import NeedPage from "./pages/NeedPage";
import PricingPage from "./pages/PricingPage";
import AboutPage from "./pages/AboutPage";
import ContactPage from "./pages/ContactPage";
import LegalPage from "./pages/LegalPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import OnboardingPage from "./pages/OnboardingPage";
import DashboardPage from "./pages/DashboardPage";
import MonitorPage from "./pages/MonitorPage";
import PolicyPage from "./pages/PolicyPage";
import HistoryPage from "./pages/HistoryPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ProfilePage from "./pages/ProfilePage";
import NotificationsPage from "./pages/NotificationsPage";
import PaymentsPage from "./pages/PaymentsPage";
import TriggersPage from "./pages/TriggersPage";
import AdminPage from "./pages/AdminPage";
import WalletPage from "./pages/WalletPage";
import TrackingPage from "./pages/TrackingPage";
import GeospatialPage from "./pages/GeospatialPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

/* ================= ROOT LAYOUT ================= */
const RootLayout = () => (
  <AppLayout>
    <Outlet />
  </AppLayout>
);

/* ================= PROTECTED ROUTE ================= */
const ProtectedRoute = ({
  children,
  requiredRole,
}: {
  children: JSX.Element;
  requiredRole?: string;
}) => {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  // ❌ Not logged in
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // ❌ Not onboarded → force onboarding
  if (!user.is_onboarded) {
    return <Navigate to="/onboarding" replace />;
  }

  // ❌ Role mismatch
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

/* ================= AUTH ROUTE ================= */
const AuthRoute = ({ children }: { children: JSX.Element }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  if (user) {
    if (!user.is_onboarded) {
      return <Navigate to="/onboarding" replace />;
    }
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

/* ================= ONBOARDING GUARD ================= */
const OnboardingRoute = ({ children }: { children: JSX.Element }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // ✅ Already onboarded → go dashboard
  if (user.is_onboarded) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

/* ================= ROUTER ================= */
const router = createBrowserRouter(
  [
    {
      element: (
        <AuthProvider>
          <RootLayout />
        </AuthProvider>
      ),
      children: [
        /* 🌐 PUBLIC */
        { path: "/", element: <LandingPage /> },
        { path: "/need", element: <NeedPage /> },
        { path: "/pricing", element: <PricingPage /> },
        { path: "/about", element: <AboutPage /> },
        { path: "/contact", element: <ContactPage /> },
        { path: "/legal", element: <LegalPage /> },

        /* 🔐 AUTH */
        {
          path: "/login",
          element: (
            <AuthRoute>
              <LoginPage />
            </AuthRoute>
          ),
        },
        {
          path: "/register",
          element: (
            <AuthRoute>
              <RegisterPage />
            </AuthRoute>
          ),
        },

        /* ✅ FIXED ONBOARDING */
        {
          path: "/onboarding",
          element: (
            <OnboardingRoute>
              <OnboardingPage />
            </OnboardingRoute>
          ),
        },

        /* 👤 PROTECTED */
        {
          path: "/dashboard",
          element: (
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/monitor",
          element: (
            <ProtectedRoute>
              <MonitorPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/policy",
          element: (
            <ProtectedRoute>
              <PolicyPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/history",
          element: (
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/analytics",
          element: (
            <ProtectedRoute>
              <AnalyticsPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/profile",
          element: (
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/notifications",
          element: (
            <ProtectedRoute>
              <NotificationsPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/payments",
          element: (
            <ProtectedRoute>
              <PaymentsPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/triggers",
          element: (
            <ProtectedRoute>
              <TriggersPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/wallet",
          element: (
            <ProtectedRoute>
              <WalletPage />
            </ProtectedRoute>
          ),
        },

        /* 🛡️ ADMIN */
        {
          path: "/admin",
          element: (
            <ProtectedRoute requiredRole="admin">
              <AdminPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/admin/tracking",
          element: (
            <ProtectedRoute requiredRole="admin">
              <TrackingPage />
            </ProtectedRoute>
          ),
        },
        {
          path: "/admin/geospatial",
          element: (
            <ProtectedRoute requiredRole="admin">
              <GeospatialPage />
            </ProtectedRoute>
          ),
        },

        /* ❌ 404 */
        {
          path: "*",
          element: <NotFound />,
        },
      ],
    },
  ],
  {
    future: {
      v7_relativeSplatPath: true,
    },
  }
);

/* ================= APP ================= */
const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <RouterProvider router={router} />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;