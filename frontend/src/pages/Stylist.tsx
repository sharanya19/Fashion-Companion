import React, { useState } from 'react';
import api from '../api/client';
import { Sparkles, Loader, ShoppingBag } from 'lucide-react';

interface OutfitItem {
    item_id: number;
    reason: string;
}

interface OutfitResponse {
    outfit_name: string;
    items: OutfitItem[];
    explanation: string;
    missing_categories?: string[];
}

export default function Stylist() {
    const [occasion, setOccasion] = useState('');
    const [weather, setWeather] = useState('');
    const [vibe, setVibe] = useState('');
    const [loading, setLoading] = useState(false);
    const [outfit, setOutfit] = useState<OutfitResponse | null>(null);
    const [wardrobe, setWardrobe] = useState<any[]>([]);

    // Fetch wardrobe to display outfit images
    React.useEffect(() => {
        api.get('/wardrobe').then(res => setWardrobe(res.data));
    }, []);

    const generateOutfit = async () => {
        if (!occasion) return;
        setLoading(true);
        setOutfit(null);
        try {
            const res = await api.post('/outfits/generate', { occasion, weather, vibe });
            setOutfit(res.data);
        } catch (err: any) {
            console.error(err);
            alert("Failed to style: " + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    const getItemImage = (id: number) => {
        const item = wardrobe.find(i => i.id === id);
        return item ? `http://localhost:8000/${item.file_path}` : null;
    };

    return (
        <div className="animate-fade-in max-w-4xl mx-auto">
            <h1 className="mb-4 flex items-center gap-2">
                <Sparkles className="text-accent" />
                AI Personal Stylist
            </h1>
            <p className="text-secondary mb-8">
                Tell me where you're going, and I'll create the perfect outfit from your existing wardrobe.
            </p>

            <div className="glass-panel p-6 mb-8 grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                    <label className="block text-sm font-medium mb-2">Occasion</label>
                    <input
                        type="text"
                        className="input-field w-full"
                        placeholder="e.g. Date Night, Job Interview"
                        value={occasion}
                        onChange={e => setOccasion(e.target.value)}
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">Weather (Optional)</label>
                    <input
                        type="text"
                        className="input-field w-full"
                        placeholder="e.g. Sunny, Rain"
                        value={weather}
                        onChange={e => setWeather(e.target.value)}
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium mb-2">Vibe (Optional)</label>
                    <input
                        type="text"
                        className="input-field w-full"
                        placeholder="e.g. Minimalist, Edgy"
                        value={vibe}
                        onChange={e => setVibe(e.target.value)}
                    />
                </div>

                <div className="md:col-span-3 flex justify-end mt-2">
                    <button
                        className="btn-primary flex items-center gap-2"
                        onClick={generateOutfit}
                        disabled={loading || !occasion}
                    >
                        {loading ? <Loader className="animate-spin" /> : <Sparkles size={18} />}
                        {loading ? "Styling..." : "Generate Outfit"}
                    </button>
                </div>
            </div>

            {outfit && (
                <div className="animate-slide-up">
                    <div className="flex justify-between items-end mb-6">
                        <div>
                            <h2 className="text-2xl font-bold text-accent">{outfit.outfit_name}</h2>
                            <p className="text-secondary max-w-2xl mt-2">{outfit.explanation}</p>
                        </div>
                    </div>

                    {outfit.missing_categories && outfit.missing_categories.length > 0 && (
                        <div className="bg-yellow-900/20 border border-yellow-700/50 p-4 rounded-lg mb-6 text-yellow-200 text-sm flex items-center gap-2">
                            <ShoppingBag size={16} />
                            Missing items for complete look: {outfit.missing_categories.join(", ")}
                        </div>
                    )}

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                        {outfit.items.map(outfitItem => (
                            <div key={outfitItem.item_id} className="glass-panel overflow-hidden group">
                                <div className="aspect-[3/4] bg-black relative">
                                    {getItemImage(outfitItem.item_id) ? (
                                        <img
                                            src={getItemImage(outfitItem.item_id)!}
                                            alt="Item"
                                            className="w-full h-full object-cover"
                                        />
                                    ) : (
                                        <div className="w-full h-full flex items-center justify-center text-xs text-muted">
                                            Image Error
                                        </div>
                                    )}
                                </div>
                                <div className="p-3">
                                    <p className="text-xs text-secondary">{outfitItem.reason}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
