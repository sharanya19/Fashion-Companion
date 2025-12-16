import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Plus, Sparkles, Trash2 } from 'lucide-react';
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
        await api.delete(`/wardrobe/${id}`);
        fetchItems();
    };

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;

        const file = e.target.files[0];

        if (!file.type.startsWith('image/')) {
            alert("Please upload an image");
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            alert("Image too large (max 10MB)");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        // 🚫 DO NOT SEND CATEGORY — AI decides

        setIsUploading(true);
        try {
            await api.post('/wardrobe', formData, { timeout: 30000 });
            fetchItems();
        } catch (err: any) {
            alert(err.response?.data?.detail || "Upload failed");
        } finally {
            setIsUploading(false);
            e.target.value = '';
        }
    };

    const getMatchColor = (level: string) => {
        if (level === 'best') return 'var(--success)';
        if (level === 'worst') return 'var(--error)';
        return 'var(--text-muted)';
    };

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 32 }}>
                <div>
                    <h1>Digital Wardrobe</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        AI Auto-Tags your uploads
                    </p>
                </div>

                <div style={{ display: 'flex', gap: 12 }}>
                    <button className="btn-secondary" onClick={() => navigate('/stylist')}>
                        <Sparkles size={18} /> AI Stylist
                    </button>

                    <label className="btn-primary">
                        <Plus size={18} /> {isUploading ? "Scanning..." : "Add Item"}
                        <input
                            type="file"
                            accept="image/*"
                            hidden
                            disabled={isUploading}
                            onChange={handleUpload}
                        />
                    </label>
                </div>
            </div>

            <div className="grid-cols-3">
                {items.map(item => (
                    <div key={item.id} className="glass-panel" style={{ padding: 12, position: 'relative' }}>
                        <button
                            onClick={() => deleteItem(item.id)}
                            style={{
                                position: 'absolute',
                                top: 12,
                                left: 12,
                                background: 'rgba(0,0,0,0.5)',
                                borderRadius: '50%',
                                width: 28,
                                height: 28,
                                color: '#fff',
                                border: 'none'
                            }}
                        >
                            <Trash2 size={14} />
                        </button>

                        <div
                            style={{
                                position: 'absolute',
                                top: 12,
                                right: 12,
                                background: getMatchColor(item.match_level),
                                padding: '4px 8px',
                                borderRadius: 4,
                                fontSize: '0.75rem',
                                fontWeight: 'bold'
                            }}
                        >
                            {item.match_level}
                        </div>

                        <div style={{ height: 240, marginBottom: 12, background: '#000', borderRadius: 8 }}>
                            <img
                                src={`http://localhost:8000/${item.file_path}`}
                                alt={item.subcategory || item.category}
                                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                            />
                        </div>

                        <div>
                            <h3>
                                {item.subcategory || item.category}
                            </h3>

                            {item.color_name && (
                                <span className="badge">{item.color_name}</span>
                            )}

                            {item.seasonality?.[0] && (
                                <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>
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
