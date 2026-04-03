import { useAuth } from '@/contexts/AuthContext';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import AppSidebar from './AppSidebar';
import Footer from './Footer';
import MobileNav from './MobileNav';

const publicPaths = ['/', '/need', '/pricing', '/about', '/contact', '/legal', '/login', '/register'];

const AppLayout = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();
  const location = useLocation();
  const isPublicPage = publicPaths.includes(location.pathname);
  const isAuthPage = ['/login', '/register', '/onboarding'].includes(location.pathname);
  const showSidebar = user?.onboarded && !isPublicPage && !isAuthPage;

  if (isAuthPage) return <>{children}</>;

  return (
    <div className="min-h-screen flex flex-col">
      {(isPublicPage || !user) && <Navbar />}
      <div className="flex flex-1">
        {showSidebar && <AppSidebar />}
        <main className="flex-1 flex flex-col">
          {showSidebar && <MobileNav />}
          <div className="flex-1">{children}</div>
        </main>
      </div>
      {isPublicPage && <Footer />}
    </div>
  );
};

export default AppLayout;
