import React, { useEffect, useState } from "react";
import api from "../api/client";
import { Sparkles, Loader, ShoppingBag } from "lucide-react";

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
  const [occasion, setOccasion] = useState("");
  const [weather, setWeather] = useState("");
  const [vibe, setVibe] = useState("");
  const [loading, setLoading] = useState(false);
  const [outfit, setOutfit] = useState<OutfitResponse | null>(null);
  const [wardrobe, setWardrobe] = useState<any[]>([]);

  // Load wardrobe once
  useEffect(() => {
    api.get("/wardrobe").then(res => setWardrobe(res.data));
  }, []);

  const generateOutfit = async () => {
    if (!occasion) return;
    setLoading(true);
    setOutfit(null);
    try {
      const res = await api.post("/outfits/generate", {
        occasion,
        weather,
        vibe,
      });
      setOutfit(res.data);
    } catch (err) {
      console.error(err);
      alert("Failed to generate outfit");
    } finally {
      setLoading(false);
    }
  };

  const getImage = (id: number) => {
    const item = wardrobe.find(i => i.id === id);
    return item ? `http://localhost:8000/${item.file_path}` : "";
  };

  return (
    <div className="max-w-6xl mx-auto animate-fade-in">
      {/* HEADER */}
      <h1 className="flex items-center gap-2 mb-2">
        <Sparkles className="text-accent" />
        AI Personal Stylist
      </h1>

      <p className="text-secondary mb-6">
        Tell me where you're going, and I'll style a complete outfit from your wardrobe.
      </p>

      {/* CONTROLS */}
      <div className="glass-panel p-4 grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <select
          className="input-field"
          value={occasion}
          onChange={e => setOccasion(e.target.value)}
        >
          <option value="">Occasion *</option>
          <option>Date</option>
          <option>Casual</option>
          <option>Office</option>
          <option>Party</option>
          <option>Wedding</option>
        </select>

        <select
          className="input-field"
          value={weather}
          onChange={e => setWeather(e.target.value)}
        >
          <option value="">Weather</option>
          <option>Hot</option>
          <option>Cold</option>
          <option>Rainy</option>
        </select>

        <select
          className="input-field"
          value={vibe}
          onChange={e => setVibe(e.target.value)}
        >
          <option value="">Vibe</option>
          <option>Minimal</option>
          <option>Edgy</option>
          <option>Elegant</option>
          <option>Street</option>
        </select>

        <button
          className="btn-primary col-span-full"
          onClick={generateOutfit}
          disabled={loading || !occasion}
        >
          {loading ? <Loader className="animate-spin" /> : "Generate Outfit"}
        </button>
      </div>

      {/* RESULT */}
      {outfit && (
        <>
          <h2 className="text-xl font-bold text-accent mb-1">
            {outfit.outfit_name}
          </h2>

          <p className="text-secondary mb-4 max-w-3xl">
            {outfit.explanation}
          </p>

          {outfit.missing_categories?.length ? (
            <div className="bg-yellow-900/20 border border-yellow-700/40 p-3 rounded mb-4 text-sm flex items-center gap-2">
              <ShoppingBag size={16} />
              Missing: {outfit.missing_categories.join(", ")}
            </div>
          ) : null}

          {/* OUTFIT GRID */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {outfit.items.map(item => (
              <div
                key={item.item_id}
                className="glass-panel p-2 flex flex-col items-center"
              >
                {/* IMAGE */}
                <div
                  className="bg-black rounded-md overflow-hidden flex items-center justify-center"
                  style={{ height: 120, width: "100%" }}
                >
                  <img
                    src={getImage(item.item_id)}
                    alt=""
                    style={{
                      maxHeight: "100%",
                      maxWidth: "100%",
                      objectFit: "contain",
                    }}
                  />
                </div>

                {/* REASON */}
                <p className="text-[11px] text-secondary mt-2 text-center leading-snug">
                  {item.reason}
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
