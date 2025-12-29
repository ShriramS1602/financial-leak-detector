import React, { useState } from 'react';
import { ShieldCheck, Activity, PieChart, Sparkles } from 'lucide-react';
import PolicyModal from './PolicyModal';

interface AuthLayoutProps {
    children: React.ReactNode;
    title: string;
    subtitle: string;
}

const AuthLayout: React.FC<AuthLayoutProps> = ({ children, title, subtitle }) => {
    const [showTerms, setShowTerms] = useState(false);
    const [showPrivacy, setShowPrivacy] = useState(false);

    return (
        <div className="min-h-screen w-full flex bg-gray-50">
            {/* Left Side - Form Container */}
            <div className="flex-1 flex flex-col justify-center items-center py-6 px-4 sm:px-6 lg:flex-none lg:px-20 xl:px-24 w-full lg:w-[55%] xl:w-[35%] shadow-2xl z-10 relative overflow-hidden bg-[#f8fafc]">

                {/* Funky Vibrant Background */}
                <div className="absolute inset-0 z-0">
                    <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
                    <div className="absolute top-0 -right-4 w-72 h-72 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
                    <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
                    <div className="absolute inset-0 bg-white/40 backdrop-blur-3xl"></div>
                </div>

                {/* Glass Card Container */}
                <div className="mx-auto w-full max-w-xl relative z-10 bg-white/60 backdrop-blur-xl p-6 rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.12)] border border-white/50">
                    <div className="flex flex-col items-center">
                        <div className="flex items-center gap-2 text-indigo-600 mb-4">
                            <div className="p-3 bg-indigo-600 rounded-2xl shadow-lg transform -rotate-6">
                                <ShieldCheck className="h-8 w-8 text-white" />
                            </div>
                            <span className="text-3xl font-black tracking-tighter text-gray-900">FinGuard</span>
                        </div>

                        <h2 className="text-2xl font-bold text-gray-900 text-center w-full mb-2">
                            {title}
                        </h2>
                        <p className="text-sm text-gray-600 text-center w-full mb-4">
                            {subtitle}
                        </p>
                    </div>

                    <div className="w-full">
                        {children}
                    </div>
                </div>

                {/* Mobile Footer/Copyright */}
                <div className="pt-8 flex flex-col sm:flex-row justify-between items-center text-xs text-gray-500 relative z-10 w-full max-w-xl mx-auto">
                    <span className="font-medium">&copy; {new Date().getFullYear()} FinGuard</span>
                    <div className="flex gap-4 mt-2 sm:mt-0 font-medium">
                        <button
                            onClick={() => setShowPrivacy(true)}
                            className="hover:text-indigo-600 transition-colors focus:outline-none"
                        >
                            Privacy
                        </button>
                        <button
                            onClick={() => setShowTerms(true)}
                            className="hover:text-indigo-600 transition-colors focus:outline-none"
                        >
                            Terms
                        </button>
                    </div>
                </div>

                <PolicyModal
                    isOpen={showTerms}
                    onClose={() => setShowTerms(false)}
                    type="terms"
                />
                <PolicyModal
                    isOpen={showPrivacy}
                    onClose={() => setShowPrivacy(false)}
                    type="privacy"
                />
            </div>

            {/* Right Side - Hero Section */}
            <div className="hidden lg:block relative flex-1 bg-indigo-900 overflow-hidden">
                {/* Dynamic Background */}
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-600 via-indigo-900 to-slate-900">
                    <div className="absolute inset-0 opacity-20"
                        style={{
                            backgroundImage: 'radial-gradient(#ffffff 1px, transparent 1px)',
                            backgroundSize: '30px 30px'
                        }}>
                    </div>
                </div>

                {/* Dashboard Mockup - Tilted Card */}
                <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[140%] h-[140%] opacity-40 pointer-events-none rotate-12 translate-x-20">
                    <div className="absolute inset-0 bg-gray-900 rounded-3xl border-8 border-gray-800 shadow-2xl overflow-hidden">
                        {/* Mock Header */}
                        <div className="h-16 bg-gray-800 border-b border-gray-700 flex items-center px-8 gap-4">
                            <div className="flex gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-500"></div>
                                <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                            </div>
                        </div>
                        {/* Mock Content */}
                        <div className="p-8 grid grid-cols-3 gap-6">
                            <div className="col-span-2 h-64 bg-gray-800/50 rounded-xl animate-pulse"></div>
                            <div className="h-64 bg-gray-800/50 rounded-xl animate-pulse"></div>
                            <div className="h-40 bg-gray-800/50 rounded-xl animate-pulse"></div>
                            <div className="col-span-2 h-40 bg-gray-800/50 rounded-xl animate-pulse"></div>
                        </div>
                    </div>
                </div>

                {/* Content Overlay */}
                <div className="absolute inset-0 flex flex-col justify-between p-20 text-white z-auto">
                    <div className="mt-10">
                        <h3 className="text-5xl font-bold leading-tight mb-6">
                            Smart Insights for<br />
                            <span className="text-indigo-300">Smarter Spending</span>
                        </h3>
                        <p className="text-indigo-100 text-xl max-w-lg leading-relaxed">
                            Experience the next generation of personal finance management.
                            Secure, intuitive, and powered by advanced AI.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 gap-6 max-w-md">
                        <div className="flex items-center gap-4 p-4 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 transform transition-all hover:translate-x-2 hover:bg-white/20 cursor-default">
                            <div className="p-3 bg-indigo-500/20 rounded-lg">
                                <Activity className="h-6 w-6 text-indigo-300" />
                            </div>
                            <div>
                                <h4 className="font-semibold text-lg">Real-time Monitoring</h4>
                                <p className="text-indigo-200 text-sm">Track every penny as it moves.</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 p-4 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 transform transition-all hover:translate-x-2 hover:bg-white/20 cursor-default">
                            <div className="p-3 bg-purple-500/20 rounded-lg">
                                <PieChart className="h-6 w-6 text-purple-300" />
                            </div>
                            <div>
                                <h4 className="font-semibold text-lg">Visual Analytics</h4>
                                <p className="text-indigo-200 text-sm">Understand your spending habits instantly.</p>
                            </div>
                        </div>

                        <div className="flex items-center gap-4 p-4 rounded-xl bg-white/10 backdrop-blur-md border border-white/10 transform transition-all hover:translate-x-2 hover:bg-white/20 cursor-default">
                            <div className="p-3 bg-emerald-500/20 rounded-lg">
                                <ShieldCheck className="h-6 w-6 text-emerald-300" />
                            </div>
                            <div>
                                <h4 className="font-semibold text-lg">Bank-Grade Security</h4>
                                <p className="text-indigo-200 text-sm">Your financial data is encrypted and safe.</p>
                            </div>
                        </div>
                    </div>
                    <div className="absolute bottom-5 right-5 inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full">
                        <Sparkles className="w-4 h-4 text-yellow-300" />
                        <span className="text-xs font-medium">AI-Powered Finance</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AuthLayout;
