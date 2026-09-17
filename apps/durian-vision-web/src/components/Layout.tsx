import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { useSession, signOut } from '../lib/auth';

const NavItem = ({ to, icon, label, fill, currentPath }: { to: string; icon: string; label: string; fill?: boolean; currentPath: string }) => {
  const isActive = currentPath === to;
  
  if (isActive) {
    return (
      <Link to={to} className="flex items-center gap-md px-md py-sm rounded-lg text-primary dark:text-primary font-bold border-r-2 border-primary bg-surface-container dark:bg-surface-container scale-95 transition-transform group">
        <span className="material-symbols-outlined text-[20px]" style={{ fontVariationSettings: fill ? "'FILL' 1" : undefined }}>{icon}</span>
        <span className="font-label-caps text-label-caps">{label}</span>
      </Link>
    );
  }

  return (
    <Link to={to} className="flex items-center gap-md px-md py-sm rounded-lg text-on-surface-variant dark:text-on-surface-variant hover:bg-surface-container hover:text-primary dark:hover:text-primary transition-colors group">
      <span className="material-symbols-outlined text-[20px] transition-transform group-hover:scale-110" style={{ fontVariationSettings: fill ? "'FILL' 1" : undefined }}>{icon}</span>
      <span className="font-label-caps text-label-caps">{label}</span>
    </Link>
  );
};

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const path = location.pathname;
  const { data: session } = useSession();

  const handleLogout = async () => {
    await signOut();
    navigate('/login');
  };
    
  return (
    <div className="bg-background text-on-surface font-body-md text-body-md h-screen w-full flex overflow-hidden">
      {/* SideNavBar */}
      <nav className="hidden md:flex bg-surface-container-low dark:bg-surface-container-low flex-col w-64 h-full py-lg px-md gap-md border-r border-surface-container-highest z-30 flex-shrink-0 shadow-[4px_0_24px_rgba(0,0,0,0.5)]">
        {/* Header */}
        <div className="flex items-center gap-sm mb-lg px-sm">
          <div className="w-10 h-10 rounded-DEFAULT bg-primary flex items-center justify-center text-on-primary font-bold shadow-[0_0_12px_rgba(75,226,119,0.3)] border border-outline-variant">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>dataset</span>
          </div>
          <div>
            <h1 className="font-headline-sm text-headline-sm font-black text-primary dark:text-primary leading-tight">DurianVision</h1>
            <p className="font-label-caps text-label-caps text-on-surface-variant">v1.0 AI Engine</p>
          </div>
        </div>
        
        {/* Navigation Links */}
        <ul className="flex flex-col gap-xs flex-1">
          <li><NavItem to="/dashboard" icon="precision_manufacturing" label="Detection" fill currentPath={path} /></li>
          <li><NavItem to="/performance" icon="insights" label="Performance" fill currentPath={path} /></li>
          <li><NavItem to="/snapshot" icon="photo_camera" label="Snapshot" currentPath={path} /></li>
          <li><NavItem to="/log" icon="list_alt" label="Log" fill currentPath={path} /></li>
          <li className="mt-auto"><NavItem to="/settings" icon="settings" label="Settings" currentPath={path} /></li>
        </ul>
        
        {/* Avatar Bottom */}
        <div className="mt-auto px-sm pt-md border-t border-surface-container-highest flex items-center justify-between">
          <div className="flex items-center gap-sm">
            <div className="w-8 h-8 rounded-full bg-surface-bright flex items-center justify-center border border-outline overflow-hidden">
              {session?.user?.image ? (
                <img src={session.user.image} alt="Avatar" className="w-full h-full object-cover" />
              ) : (
                <span className="material-symbols-outlined text-on-surface-variant text-[18px]">person</span>
              )}
            </div>
            <div className="flex flex-col">
              <span className="font-label-caps text-label-caps text-on-surface truncate w-24" title={session?.user?.name}>{session?.user?.name || 'Admin'}</span>
            </div>
          </div>
          <button 
            onClick={handleLogout}
            title="Sign out"
            className="p-1 rounded-md text-on-surface-variant hover:text-error hover:bg-error/10 transition-colors"
          >
            <span className="material-symbols-outlined text-[18px]">logout</span>
          </button>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col relative overflow-hidden bg-background">
        <Outlet />
      </main>
    </div>
  );
}
