import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Plus, Upload, Sparkles, Trash2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Item {
    id: number;
    file_path: string;
    category: string;
    subcategory?: string;
    seasonality?: string[];
    match_level: string;
    color_name?: string;
}

export default function Wardrobe() {
    const [items, setItems] = useState<Item[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = () => {
        api.get('/wardrobe').then(res => setItems(res.data));
    };

    const deleteItem = async (id: number) => {
        if (!confirm("Delete item?")) return;
        try {
            await api.delete(`/wardrobe/${id}`);
            fetchItems();
        } catch (err) {
            console.error(err);
        }
    };

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;

        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', 'Top'); // Default, AI will refine

        setIsUploading(true);
        try {
            await api.post('/wardrobe', formData);
            fetchItems();
        } catch (err) {
            console.error(err);
            alert("Upload failed. Check backend console.");
        } finally {
            setIsUploading(false);
        }
    };

    const getMatchColor = (level: string) => {
        switch (level) {
            case 'best': return 'var(--success)';
            case 'worst': return 'var(--error)';
            default: return 'var(--text-muted)';
        }
    };

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                    <h1>Digital Wardrobe</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>AI Auto-Tags your uploads!</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="btn-secondary" onClick={() => navigate('/stylist')} style={{ display: 'flex', gap: '8px' }}>
                        <Sparkles size={20} />
                        AI Stylist
                    </button>
                    <label className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Plus size={20} />
                        {isUploading ? "Scanning..." : "Add Item"}
                        <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleUpload} disabled={isUploading} />
                    </label>
                </div>
            </div>

            <div className="grid-cols-3">
                {items.map(item => (
                    <div key={item.id} className="glass-panel" style={{ padding: '12px', position: 'relative' }}>
                        <button
                            onClick={(e) => { e.stopPropagation(); deleteItem(item.id); }}
                            style={{
                                position: 'absolute',
                                top: '12px',
                                left: '12px',
                                background: 'rgba(0,0,0,0.5)',
                                color: '#fff',
                                border: 'none',
                                borderRadius: '50%',
                                width: '28px',
                                height: '28px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: 'pointer',
                                zIndex: 10
                            }}
                        >
                            <Trash2 size={16} />
                        </button>
                        <div style={{
                            position: 'absolute',
                            top: '12px',
                            right: '12px',
                            background: getMatchColor(item.match_level),
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '0.8rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase',
                            zIndex: 2
                        }}>
                            {item.match_level}
                        </div>

                        <div style={{ height: '240px', borderRadius: '8px', overflow: 'hidden', marginBottom: '12px', background: '#000' }}>
                            <img
                                src={`http://localhost:8000/${item.file_path}`}
                                alt={item.category}
                                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                            />
                        </div>

                        <div>
                            <h3 style={{ fontSize: '1rem', marginBottom: '4px' }}>
                                {item.subcategory || item.category}
                            </h3>
                            {item.color_name && (
                                <span className="badge" style={{ marginRight: '4px' }}>{item.color_name}</span>
                            )}
                            {item.seasonality && item.seasonality.length > 0 && (
                                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                    • {item.seasonality[0]}
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
