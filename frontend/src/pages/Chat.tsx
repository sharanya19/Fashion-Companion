import React, { useState, useEffect, useRef } from 'react';
import api from '../api/client';
import { Send, User, Bot } from 'lucide-react';

interface Message {
    role: string;
    content: string;
}

export default function Chat() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [conversationId, setConversationId] = useState<number | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(scrollToBottom, [messages]);

    const handleSend = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input;
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setIsLoading(true);

        try {
            const res = await api.post('/stylist/chat', {
                message: userMsg,
                conversation_id: conversationId
            });

            setConversationId(res.data.conversation_id);
            setMessages(prev => [...prev, { role: 'assistant', content: res.data.response }]);
        } catch (err) {
            setMessages(prev => [...prev, { role: 'system', content: "Error connecting to stylist." }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="glass-panel animate-fade-in" style={{ height: 'calc(100vh - 120px)', display: 'flex', flexDirection: 'column', padding: 0, overflow: 'hidden' }}>
            <div style={{ padding: '24px', borderBottom: '1px solid var(--border-color)' }}>
                <h2 style={{ margin: 0 }}>Ask Your Stylist</h2>
                <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)' }}>Powered by Grok</p>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {messages.length === 0 && (
                    <div style={{ textAlign: 'center', color: 'var(--text-muted)', marginTop: '40px' }}>
                        <Bot size={48} style={{ opacity: 0.5, marginBottom: '16px' }} />
                        <p>Hello! I'm Palette, your personal AI stylist.</p>
                        <p>Ask me about your colors, outfit ideas, or fashion advice!</p>
                    </div>
                )}

                {messages.map((msg, i) => (
                    <div key={i} style={{
                        alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                        maxWidth: '70%',
                        display: 'flex',
                        gap: '12px'
                    }}>
                        {msg.role !== 'user' && (
                            <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Bot size={18} color="#000" />
                            </div>
                        )}

                        <div style={{
                            background: msg.role === 'user' ? 'var(--primary-color)' : 'rgba(255,255,255,0.05)',
                            color: msg.role === 'user' ? '#000' : 'var(--text-main)',
                            padding: '12px 16px',
                            borderRadius: '16px',
                            borderTopLeftRadius: msg.role === 'assistant' ? '4px' : '16px',
                            borderTopRightRadius: msg.role === 'user' ? '4px' : '16px',
                            lineHeight: '1.5'
                        }}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div style={{ alignSelf: 'flex-start', marginLeft: '44px', color: 'var(--text-muted)' }}>
                        Stylist is thinking...
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            <div style={{ padding: '24px', borderTop: '1px solid var(--border-color)', background: 'rgba(0,0,0,0.2)' }}>
                <form onSubmit={handleSend} style={{ display: 'flex', gap: '12px' }}>
                    <input
                        className="input-field"
                        value={input}
                        onChange={e => setInput(e.target.value)}
                        placeholder="Type your fashion question..."
                        disabled={isLoading}
                    />
                    <button type="submit" className="btn-primary" disabled={isLoading} style={{ width: 'auto', padding: '0 24px' }}>
                        <Send size={20} />
                    </button>
                </form>
            </div>
        </div>
    );
}
