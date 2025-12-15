import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';

export default function Login() {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        try {
            if (isLogin) {
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);
                const res = await api.post('/auth/token', formData);
                localStorage.setItem('token', res.data.access_token);
                navigate('/');
            } else {
                await api.post('/auth/register', { email, password, full_name: fullName });
                // Auto login after register
                const formData = new FormData();
                formData.append('username', email);
                formData.append('password', password);
                const res = await api.post('/auth/token', formData);
                localStorage.setItem('token', res.data.access_token);
                navigate('/');
            }
        } catch (err: any) {
            console.error(err);
            if (err.response && err.response.data && err.response.data.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Authentication failed. Please check your credentials.');
            }
        }
    };

    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
            <div className="glass-panel animate-fade-in" style={{ width: '400px' }}>
                <h1 style={{ textAlign: 'center', marginBottom: '8px' }}>Palette</h1>
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', marginBottom: '32px' }}>
                    {isLogin ? 'Welcome back, Stylist.' : 'Begin your style journey.'}
                </p>

                {error && <div style={{ color: 'var(--error)', marginBottom: '16px', fontSize: '0.9rem' }}>{error}</div>}

                <form onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div style={{ marginBottom: '16px' }}>
                            <input
                                className="input-field"
                                placeholder="Full Name"
                                value={fullName}
                                onChange={e => setFullName(e.target.value)}
                                required
                            />
                        </div>
                    )}
                    <div style={{ marginBottom: '16px' }}>
                        <input
                            className="input-field"
                            type="email"
                            placeholder="Email address"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div style={{ marginBottom: '24px' }}>
                        <input
                            className="input-field"
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                        />
                    </div>

                    <button type="submit" className="btn-primary" style={{ width: '100%' }}>
                        {isLogin ? 'Sign In' : 'Create Account'}
                    </button>
                </form>

                <div style={{ marginTop: '24px', textAlign: 'center' }}>
                    <button
                        className="btn-secondary"
                        style={{ border: 'none', padding: '0', background: 'transparent', color: 'var(--primary-color)' }}
                        onClick={() => setIsLogin(!isLogin)}
                    >
                        {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
                    </button>
                </div>
            </div>
        </div>
    );
}
