import React, { useEffect, useState } from "react";
import api from "../api/client";
import { Plus, Sparkles, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";

interface WardrobeItem {
    id: number;
    file_path: string;
    category: string;
    subcategory?: string;
    seasonality?: string[];
    match_level: "best" | "neutral" | "worst";
    color_name?: string;
}

export default function Wardrobe() {
    const [items, setItems] = useState<WardrobeItem[]>([]);
    const [isUploading, setIsUploading] = useState(false);
    const navigate = useNavigate();

    // ---------------------------------------
    // Load wardrobe
    // ---------------------------------------
    const fetchItems = async () => {
        try {
            const res = await api.get("/wardrobe");
            setItems(res.data);
        } catch (err) {
            console.error("Failed to load wardrobe", err);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    // ---------------------------------------
    // Upload handler
    // ---------------------------------------
    const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        if (!e.target.files?.[0]) return;

        const file = e.target.files[0];

        if (!file.type.startsWith("image/")) {
            alert("Please upload an image file");
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            alert("Image too large (max 10MB)");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);
        // ❗ DO NOT send category — backend AI decides

        setIsUploading(true);
        try {
            await api.post("/wardrobe", formData, {
                timeout: 30000,
                headers: { "Content-Type": "multipart/form-data" },
            });
            await fetchItems();
        } catch (err: any) {
            alert(err.response?.data?.detail || "Upload failed");
        } finally {
            setIsUploading(false);
            e.target.value = "";
        }
    };

    // ---------------------------------------
    // Delete handler
    // ---------------------------------------
    const deleteItem = async (id: number) => {
        console.log("🗑️ Delete clicked for item:", id);

        // TEMPORARILY DISABLED CONFIRMATION FOR TESTING
        // if (!confirm("Delete this item?")) {
        //     console.log("Delete cancelled by user");
        //     return;
        // }

        console.log("📡 Sending DELETE request to /wardrobe/" + id);
        try {
            const response = await api.delete(`/wardrobe/${id}`);
            console.log("✅ Delete successful:", response.status, response.data);

            // Immediately remove from local state for instant feedback
            setItems(prevItems => prevItems.filter(item => item.id !== id));

            // Then fetch fresh data from server
            await fetchItems();
            console.log("✅ Wardrobe refreshed");
        } catch (err: any) {
            console.error("❌ Delete failed:", err);
            console.error("Error details:", err.response?.data);
            alert(`Failed to delete item: ${err.response?.data?.detail || err.message}`);
        }
    };

    // ---------------------------------------
    // UI helpers
    // ---------------------------------------
    const matchBadgeColor = (level: string) => {
        if (level === "best") return "var(--success)";
        if (level === "worst") return "var(--error)";
        return "var(--text-muted)";
    };

    // ---------------------------------------
    // Render
    // ---------------------------------------
    return (
        <div className="animate-fade-in">
            {/* HEADER */}
            <div
                style={{
                    display: "flex",
                    justifyContent: "space-between",
                    marginBottom: 32,
                }}
            >
                <div>
                    <h1>Digital Wardrobe</h1>
                    <p style={{ color: "var(--text-secondary)" }}>
                        AI automatically categorizes your uploads
                    </p>
                </div>

                <div style={{ display: "flex", gap: 12 }}>
                    <button
                        className="btn-secondary"
                        onClick={() => navigate("/stylist")}
                    >
                        <Sparkles size={18} />
                        AI Stylist
                    </button>

                    <label className="btn-primary">
                        <Plus size={18} />
                        {isUploading ? "Scanning..." : "Add Item"}
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

            {/* GRID */}
            <div className="grid-cols-3">
                {items.map((item) => (
                    <div
                        key={item.id}
                        className="glass-panel"
                        style={{ padding: 12, position: "relative" }}
                    >
                        {/* DELETE */}
                        <button
                            onClick={() => deleteItem(item.id)}
                            style={{
                                position: "absolute",
                                top: 12,
                                left: 12,
                                background: "rgba(0,0,0,0.55)",
                                borderRadius: "50%",
                                width: 28,
                                height: 28,
                                color: "#fff",
                                border: "none",
                            }}
                        >
                            <Trash2 size={14} />
                        </button>

                        {/* MATCH LEVEL */}
                        <div
                            style={{
                                position: "absolute",
                                top: 12,
                                right: 12,
                                background: matchBadgeColor(item.match_level),
                                padding: "4px 8px",
                                borderRadius: 4,
                                fontSize: "0.7rem",
                                fontWeight: 700,
                            }}
                        >
                            {item.match_level}
                        </div>

                        {/* IMAGE */}
                        <div
                            style={{
                                height: 240,
                                marginBottom: 12,
                                background: "#000",
                                borderRadius: 8,
                                overflow: "hidden",
                            }}
                        >
                            <img
                                src={`http://127.0.0.1:8000/${item.file_path}`}
                                alt={item.category}
                                style={{
                                    width: "100%",
                                    height: "100%",
                                    objectFit: "contain",
                                }}
                            />
                        </div>

                        {/* DETAILS */}
                        <div>
                            {/* CATEGORY (authoritative) */}
                            <h3>{item.category}</h3>

                            {/* SUBCATEGORY (optional) */}
                            {item.subcategory && (
                                <div
                                    style={{
                                        fontSize: 12,
                                        color: "var(--text-muted)",
                                        marginBottom: 4,
                                    }}
                                >
                                    {item.subcategory}
                                </div>
                            )}

                            {/* COLOR */}
                            {item.color_name && (
                                <span className="badge">{item.color_name}</span>
                            )}

                            {/* SEASON */}
                            {item.seasonality?.[0] && (
                                <div
                                    style={{
                                        fontSize: 12,
                                        color: "var(--text-muted)",
                                        marginTop: 4,
                                    }}
                                >
                                    {item.seasonality[0]}
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {!items.length && (
                    <div style={{ color: "var(--text-muted)", marginTop: 40 }}>
                        Your wardrobe is empty. Upload items to get started ✨
                    </div>
                )}
            </div>
        </div>
    );
}
