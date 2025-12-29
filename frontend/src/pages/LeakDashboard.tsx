
import React, { useEffect, useState } from 'react';
import api from '../services/api';

interface Leak {
    id: number;
    leak_type: string;
    title: string;
    description: string;
    severity: string;
    detected_amount: number;
    frequency: string;
    created_at: string;
}

const LeakDashboard: React.FC = () => {
    const [leaks, setLeaks] = useState<Leak[]>([]);
    const [loading, setLoading] = useState(true);
    const [detecting, setDetecting] = useState(false);

    const fetchLeaks = async () => {
        try {
            const data = await api.getLeaks();
            setLeaks(data);
        } catch (error) {
            console.error("Failed to fetch leaks", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDetect = async () => {
        setDetecting(true);
        try {
            await api.detectLeaks();
            await fetchLeaks();
        } catch (error) {
            console.error("Failed to detect leaks", error);
        } finally {
            setDetecting(false);
        }
    };

    const handleResolve = async (id: number) => {
        try {
            await api.resolveLeak(id);
            setLeaks(leaks.filter(l => l.id !== id));
        } catch (error) {
            console.error("Failed to resolve leak", error);
        }
    }

    useEffect(() => {
        fetchLeaks();
    }, []);

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Financial Leak Detector</h1>
                <button
                    onClick={handleDetect}
                    disabled={detecting}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow transition disabled:opacity-50"
                >
                    {detecting ? 'Analyzing...' : 'Run Detection'}
                </button>
            </div>

            {loading ? (
                <div className="text-center py-12">Loading...</div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {leaks.length === 0 ? (
                        <div className="col-span-full text-center py-12 text-gray-500">
                            No leaks detected! You are leak-free 🎉
                        </div>
                    ) : (
                        leaks.map((leak) => (
                            <div key={leak.id} className={`bg-white rounded-xl shadow-md p-6 border-l-4 ${leak.severity === 'high' ? 'border-red-500' :
                                    leak.severity === 'medium' ? 'border-yellow-500' : 'border-blue-500'
                                }`}>
                                <div className="flex justify-between items-start mb-4">
                                    <span className={`text-xs font-bold px-2 py-1 rounded uppercase ${leak.leak_type === 'subscription' ? 'bg-purple-100 text-purple-800' :
                                            leak.leak_type === 'small_recurring' ? 'bg-yellow-100 text-yellow-800' :
                                                leak.leak_type === 'price_creep' ? 'bg-red-100 text-red-800' :
                                                    'bg-gray-100 text-gray-800'
                                        }`}>
                                        {leak.leak_type.replace('_', ' ')}
                                    </span>
                                    <span className="text-sm text-gray-500">{leak.frequency}</span>
                                </div>

                                <h3 className="text-xl font-semibold text-gray-900 mb-2">{leak.title}</h3>
                                <p className="text-gray-600 mb-4">{leak.description}</p>

                                <div className="flex justify-between items-center mt-4 pt-4 border-t border-gray-100">
                                    <div className="text-2xl font-bold text-gray-900">
                                        ₹{leak.detected_amount.toFixed(2)}
                                    </div>
                                    <button
                                        onClick={() => handleResolve(leak.id)}
                                        className="text-sm text-gray-500 hover:text-gray-700 underline"
                                    >
                                        Dismiss
                                    </button>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}
        </div>
    );
};

export default LeakDashboard;
