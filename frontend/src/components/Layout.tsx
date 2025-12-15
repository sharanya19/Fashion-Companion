import React from 'react';
import { Link, useLocation, Navigate } from 'react-router-dom';
import { Home, Shirt, MessageSquare, LogOut } from 'lucide-react';

export default function Layout({ children }: { children: React.ReactNode }) {
    const location = useLocation();
    const isAuthenticated = !!localStorage.getItem('token');

    if (!isAuthenticated && location.pathname !== '/login' && location.pathname !== '/register') {
        return <Navigate to="/login" replace />;
    }

    if (!isAuthenticated) return <>{children}</>;

    const handleLogout = () => {
        localStorage.removeItem('token');
        window.location.href = '/login';
    };

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            <aside style={{
                width: '260px',
                borderRight: '1px solid var(--border-color)',
                padding: '24px',
                display: 'flex',
                flexDirection: 'column',
                position: 'sticky',
                top: 0,
                height: '100vh',
                boxSizing: 'border-box'
            }}>
                <div style={{ marginBottom: '40px' }}>
                    <h2 style={{ fontSize: '1.5rem', background: 'linear-gradient(to right, #fff, #999)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                        Palette
                    </h2>
                </div>

                <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1 }}>
                    <NavLink to="/" icon={<Home size={20} />} label="Dashboard" active={location.pathname === '/'} />
                    <NavLink to="/wardrobe" icon={<Shirt size={20} />} label="Wardrobe" active={location.pathname === '/wardrobe'} />
                    <NavLink to="/chat" icon={<MessageSquare size={20} />} label="Stylist Chat" active={location.pathname === '/chat'} />
                </nav>

                <button onClick={handleLogout} className="nav-link" style={{ display: 'flex', alignItems: 'center', gap: '12px', background: 'none', border: 'none', cursor: 'pointer' }}>
                    <LogOut size={20} />
                    Sign Out
                </button>
            </aside>

            <main style={{ flex: 1, padding: '40px', overflowY: 'auto' }}>
                <div className="container">
                    {children}
                </div>
            </main>
        </div>
    );
}

function NavLink({ to, icon, label, active }: { to: string, icon: React.ReactNode, label: string, active: boolean }) {
    return (
        <Link to={to} className={`nav-link ${active ? 'active' : ''}`} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            borderRadius: '8px',
            backgroundColor: active ? 'rgba(255,255,255,0.05)' : 'transparent'
        }}>
            {icon}
            {label}
        </Link>
    );
}
