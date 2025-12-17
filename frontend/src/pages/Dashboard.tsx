import React, { useEffect, useState, useRef } from 'react';
import api, { analyzePhoto } from '../api/client';
import { Palette, Sparkles, AlertCircle, Upload, Camera, CheckCircle, Info, Eye } from 'lucide-react';

interface ColorItem {
    hex: string;
    name: string;
    category: string;
}

interface RichFeature {
    name: string;
    hex: string;
    depth?: string;
}

interface Analysis {
    season: string;
    season_subtype: string;
    undertone: string;
    skin_tone: RichFeature | string; // Handle both for safety
    confidence_score: number;
    best_colors: ColorItem[];
    neutral_colors: ColorItem[];
    worst_colors: ColorItem[];
    complementary_colors: ColorItem[];
    accent_colors?: ColorItem[]; // New
    luxury_colors?: ColorItem[]; // New
    eye_color: RichFeature | string;
    hair_color: RichFeature | string;
    jewelry_metals: any[]; // List of objects or strings
    jewelry_stones: any[];
    explanation?: string[];
}

export default function Dashboard() {
    const [analysis, setAnalysis] = useState<Analysis | null>(null);
    const [profile, setProfile] = useState<any>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [dragActive, setDragActive] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        api.get('/profile').then(res => setProfile(res.data));
        api.get('/profile/analysis')
            .then(res => setAnalysis(res.data))
            .catch(() => setAnalysis(null));
    }, []);

    const handleUpload = async (file: File) => {
        setIsUploading(true);
        try {
            const res = await analyzePhoto(file);
            setAnalysis(res.data);
        } catch (err) {
            console.error(err);
        } finally {
            setIsUploading(false);
        }
    };

    const handleDrag = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleUpload(e.dataTransfer.files[0]);
        }
    };

    if (isUploading) {
        return (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '60vh' }}>
                <div style={{ position: 'relative', width: '80px', height: '80px' }}>
                    <div className="animate-pulse-glow" style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '2px solid var(--primary-color)' }}></div>
                    <Sparkles size={40} className="animate-pulse" style={{ position: 'absolute', top: '20px', left: '20px', color: 'var(--primary-color)' }} />
                </div>
                <h2 style={{ marginTop: '24px' }}>Analyzing Your Style...</h2>
                <p style={{ color: 'var(--text-muted)' }}>Detecting skin tone, features, and seasonal harmony.</p>
            </div>
        );
    }

    if (!analysis) {
        return (
            <div className="animate-fade-in">
                <h1 style={{ marginBottom: '8px' }}>Welcome, let's find your season.</h1>
                <p style={{ color: 'var(--text-muted)', marginBottom: '32px' }}>Upload a photo to get your personalized color palette and style usage.</p>

                <div
                    className={`upload-zone ${dragActive ? 'drag-active' : ''}`}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                >
                    <Upload size={48} style={{ color: 'var(--primary-color)', marginBottom: '16px' }} />
                    <h3>Upload your photo</h3>
                    <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>Drag & Drop or click to browse</p>
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept="image/png, image/jpeg"
                        style={{ display: 'none' }}
                        onChange={(e) => e.target.files?.[0] && handleUpload(e.target.files[0])}
                    />

                    <div className="grid-cols-3" style={{ textAlign: 'left', marginTop: '40px', gap: '16px' }}>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', color: 'var(--text-muted)' }}>
                            <CheckCircle size={16} color="var(--success)" /> Natural Lighting
                        </div>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', color: 'var(--text-muted)' }}>
                            <CheckCircle size={16} color="var(--success)" /> No Makeup
                        </div>
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', color: 'var(--text-muted)' }}>
                            <CheckCircle size={16} color="var(--success)" /> Neutral Background
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    const seasonGradient =
        analysis.season === "Spring" ? "var(--season-spring)" :
            analysis.season === "Summer" ? "var(--season-summer)" :
                analysis.season === "Autumn" ? "var(--season-autumn)" :
                    "var(--season-winter)";

    const getFeatureName = (feature: any) => {
        return typeof feature === 'string' ? feature : feature?.name || 'Unknown';
    };

    const getFeatureHex = (feature: any) => {
        return typeof feature === 'object' ? feature?.hex : '#ccc';
    };

    return (
        <div className="animate-fade-in" style={{ paddingBottom: '80px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ fontSize: '2.5rem', marginBottom: '8px' }}>Hello, {profile?.full_name?.split(' ')[0]}</h1>
                    <div style={{ display: 'flex', gap: '12px', color: 'var(--text-muted)' }}>
                        <span>Est. Confidence: <strong>{Math.round(analysis.confidence_score * 100)}%</strong></span>
                    </div>
                </div>
                <button className="btn-secondary" onClick={() => setAnalysis(null)}>
                    <Camera size={18} style={{ marginRight: '8px' }} />
                    New Analysis
                </button>
            </div>

            {/* Make sure Explanation exists before rendering */}
            {analysis.explanation && analysis.explanation.length > 0 && (
                <div className="glass-panel" style={{ marginBottom: '32px', background: 'rgba(255, 255, 255, 0.03)' }}>
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                        <Info size={18} /> Analysis Insights
                    </h3>
                    <ul style={{ paddingLeft: '20px', color: 'var(--text-muted)' }}>
                        {analysis.explanation.map((reason, idx) => (
                            <li key={idx} style={{ marginBottom: '4px' }}>{reason}</li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Top Section: Season & Features */}
            <div className="grid-cols-3" style={{ marginBottom: '32px' }}>
                <div className="glass-panel card-hover" style={{ background: `linear-gradient(to bottom right, rgba(20,20,20,0.9), rgba(0,0,0,0.9)), ${seasonGradient}`, position: 'relative', overflow: 'hidden' }}>
                    <div style={{ position: 'relative', zIndex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                            <Palette size={20} color="white" />
                            <span style={{ textTransform: 'uppercase', letterSpacing: '2px', fontSize: '0.8rem', opacity: 0.8 }}>Your Season</span>
                        </div>
                        <h2 style={{ fontSize: '3rem', margin: '0 0 8px 0' }}>{analysis.season}</h2>
                        <div style={{ fontSize: '1.2rem', opacity: 0.8, marginBottom: '24px' }}>{analysis.season_subtype}</div>

                        <div className="tag" style={{ display: 'inline-block', background: 'rgba(255,255,255,0.2)', color: 'white' }}>
                            {analysis.undertone} Undertone
                        </div>
                    </div>
                </div>

                <div className="glass-panel card-hover" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Eye size={20} color="var(--primary-color)" /> Features
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        <div>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Eye Color</span>
                            <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>{getFeatureName(analysis.eye_color)}</div>
                        </div>
                        <div>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Hair Color</span>
                            <div style={{ fontSize: '1.2rem', fontWeight: 600 }}>{getFeatureName(analysis.hair_color)}</div>
                        </div>
                        <div>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Skin Tone</span>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <div style={{ width: '16px', height: '16px', borderRadius: '50%', background: getFeatureHex(analysis.skin_tone) }}></div>
                                <span style={{ fontSize: '1.2rem', fontWeight: 600 }}>{getFeatureName(analysis.skin_tone)}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="glass-panel card-hover">
                    <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Sparkles size={20} color="var(--primary-color)" /> Accessories
                    </h3>
                    <div style={{ marginTop: '16px' }}>
                        <div style={{ marginBottom: '16px' }}>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', display: 'block', marginBottom: '8px' }}>Best Metals</span>
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                {analysis.jewelry_metals.map((m: any, i) => (
                                    <span key={i} style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                        {typeof m === 'string' ? m : m.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                        <div>
                            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem', display: 'block', marginBottom: '8px' }}>Gemstones</span>
                            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                                {analysis.jewelry_stones.map((m: any, i) => (
                                    <span key={i} style={{ padding: '6px 12px', background: 'rgba(255,255,255,0.05)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                                        {typeof m === 'string' ? m : m.name}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Best Colors */}
            <div style={{ marginBottom: '40px' }} className="delay-100 animate-fade-in">
                <h2 style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
                    <span style={{ width: '4px', height: '24px', background: 'var(--primary-color)', borderRadius: '2px' }}></span>
                    Your Power Palette
                </h2>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(100px, 1fr))', gap: '16px' }}>
                    {analysis.best_colors.map((c, i) => (
                        <div key={i} className="swatch-card" style={{ background: c.hex }} title={c.name}>
                            <div style={{
                                position: 'absolute',
                                bottom: 0, left: 0, right: 0,
                                padding: '8px',
                                background: 'rgba(0,0,0,0.6)',
                                backdropFilter: 'blur(4px)',
                                fontSize: '0.7rem',
                                color: 'white'
                            }}>
                                <div style={{ fontWeight: 'bold' }}>{c.name}</div>
                                <div style={{ opacity: 0.8 }}>{c.category}</div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid-cols-2" style={{ marginBottom: '40px' }}>
                {/* Neutrals */}
                <div className="glass-panel delay-200 animate-fade-in">
                    <h3 style={{ marginBottom: '20px' }}>Essentials & Neutrals</h3>
                    <div className="grid-cols-auto-fit">
                        {analysis.neutral_colors.map((c, i) => (
                            <div key={i} style={{ textAlign: 'center' }}>
                                <div className="swatch-card" style={{ background: c.hex, marginBottom: '8px', borderRadius: '50%', aspectRatio: '1' }}></div>
                                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{c.name}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Complementary */}
                {/* Complementary & Accents */}
                <div className="glass-panel delay-200 animate-fade-in">
                    <h3 style={{ marginBottom: '20px' }}>Accents & Complementary</h3>
                    <div style={{ display: 'flex', gap: '16px', flexDirection: 'column' }}>
                        {/* Merge accent and complementary for display */}
                        {(analysis.accent_colors || []).concat(analysis.complementary_colors).map((c, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '12px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px' }}>
                                <div style={{ width: '48px', height: '48px', borderRadius: '8px', background: c.hex }}></div>
                                <div>
                                    <div style={{ fontWeight: 600 }}>{c.name}</div>
                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Perfect Accent</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Worst Colors */}
            <div className="glass-panel delay-300 animate-fade-in" style={{ border: '1px solid rgba(244, 67, 54, 0.2)' }}>
                <h3 style={{ marginBottom: '20px', color: 'var(--error)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={20} />
                    Colors to Avoid
                </h3>
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
                    {analysis.worst_colors.map((c, i) => (
                        <div key={i} style={{ textAlign: 'center', opacity: 0.6 }}>
                            <div className="swatch-card" style={{ background: c.hex, marginBottom: '8px', width: '60px', height: '60px' }}></div>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{c.name}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
