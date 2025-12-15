import React, { useEffect, useState } from 'react';
import api from '../api/client';
import { Plus, Upload } from 'lucide-react';

interface Item {
    id: number;
    file_path: string;
    category: string;
    match_level: string;
    color_hex?: string;
}

export default function Wardrobe() {
    const [items, setItems] = useState<Item[]>([]);
    const [isUploading, setIsUploading] = useState(false);

    useEffect(() => {
        fetchItems();
    }, []);

    const fetchItems = () => {
        api.get('/wardrobe').then(res => setItems(res.data));
    };

    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;

        const file = e.target.files[0];
        const formData = new FormData();
        formData.append('file', file);
        formData.append('category', 'Uncategorized'); // Ideally a modal asks for this

        // For demo: extract a random hex or just use default
        // In real app, we'd pick this from UI or CV
        formData.append('color_hex', '#000000');

        setIsUploading(true);
        try {
            await api.post('/wardrobe', formData);
            fetchItems();
        } catch (err) {
            console.error(err);
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
                <h1>Digital Wardrobe</h1>
                <label className="btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Plus size={20} />
                    Add Item
                    <input type="file" accept="image/*" style={{ display: 'none' }} onChange={handleUpload} disabled={isUploading} />
                </label>
            </div>

            <div className="grid-cols-3">
                {items.map(item => (
                    <div key={item.id} className="glass-panel" style={{ padding: '12px', position: 'relative' }}>
                        <div style={{
                            position: 'absolute',
                            top: '12px',
                            right: '12px',
                            background: getMatchColor(item.match_level),
                            padding: '4px 8px',
                            borderRadius: '4px',
                            fontSize: '0.8rem',
                            fontWeight: 'bold',
                            textTransform: 'uppercase'
                        }}>
                            {item.match_level} Match
                        </div>

                        {/* Fix path for local dev: prefix with API URL */}
                        <div style={{ height: '240px', borderRadius: '8px', overflow: 'hidden', marginBottom: '12px', background: '#000' }}>
                            <img
                                src={`http://localhost:8000/${item.file_path}`}
                                alt={item.category}
                                style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                            />
                        </div>

                        <div>
                            <span style={{ color: 'var(--text-muted)' }}>{item.category}</span>
                        </div>
                    </div>
                ))}
                {items.length === 0 && (
                    <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '60px', color: 'var(--text-muted)' }}>
                        <Upload size={48} style={{ marginBottom: '16px', opacity: 0.5 }} />
                        <p>No items yet. Upload your wardrobe to get started.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
