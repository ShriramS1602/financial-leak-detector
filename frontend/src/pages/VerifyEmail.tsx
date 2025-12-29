import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate, Link } from 'react-router-dom';
import { api } from '../services/api';

const VerifyEmail: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'no-token'>('loading');
    const [message, setMessage] = useState('');

    useEffect(() => {
        const token = searchParams.get('token');

        if (!token) {
            setStatus('no-token');
            setMessage('No verification token provided.');
            return;
        }

        const verifyEmail = async () => {
            try {
                const response = await api.auth.verifyEmail(token);
                setStatus('success');
                setMessage(response.message || 'Email verified successfully!');

                // Redirect to login after 3 seconds
                setTimeout(() => {
                    navigate('/login', {
                        state: { message: 'Email verified successfully! You can now log in.' }
                    });
                }, 3000);
            } catch (error: any) {
                setStatus('error');
                setMessage(error.message || 'Failed to verify email. The link may be expired or invalid.');
            }
        };

        verifyEmail();
    }, [searchParams, navigate]);

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
            <div className="max-w-md w-full mx-4">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl shadow-2xl p-8 border border-white/20">
                    {/* Logo */}
                    <div className="text-center mb-8">
                        <h1 className="text-3xl font-bold text-white mb-2">🛡️ FinGuard</h1>
                        <p className="text-gray-300 text-sm">Smart Insights for Smarter Spending</p>
                    </div>

                    {/* Status Display */}
                    <div className="text-center">
                        {status === 'loading' && (
                            <>
                                <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
                                <h2 className="text-xl font-semibold text-white mb-2">Verifying your email...</h2>
                                <p className="text-gray-300">Please wait while we verify your email address.</p>
                            </>
                        )}

                        {status === 'success' && (
                            <>
                                <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                    </svg>
                                </div>
                                <h2 className="text-xl font-semibold text-white mb-2">Email Verified! ✅</h2>
                                <p className="text-gray-300 mb-4">{message}</p>
                                <p className="text-gray-400 text-sm">Redirecting to login page...</p>
                            </>
                        )}

                        {status === 'error' && (
                            <>
                                <div className="w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </div>
                                <h2 className="text-xl font-semibold text-white mb-2">Verification Failed</h2>
                                <p className="text-gray-300 mb-6">{message}</p>
                                <div className="space-y-3">
                                    <Link
                                        to="/login"
                                        className="block w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 transition-all"
                                    >
                                        Go to Login
                                    </Link>
                                    <Link
                                        to="/signup"
                                        className="block w-full py-3 px-4 bg-white/10 text-white rounded-lg font-medium hover:bg-white/20 transition-all"
                                    >
                                        Sign Up Again
                                    </Link>
                                </div>
                            </>
                        )}

                        {status === 'no-token' && (
                            <>
                                <div className="w-16 h-16 bg-yellow-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg className="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                    </svg>
                                </div>
                                <h2 className="text-xl font-semibold text-white mb-2">Invalid Link</h2>
                                <p className="text-gray-300 mb-6">{message}</p>
                                <Link
                                    to="/login"
                                    className="block w-full py-3 px-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg font-medium hover:from-purple-700 hover:to-indigo-700 transition-all"
                                >
                                    Go to Login
                                </Link>
                            </>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <p className="text-center text-gray-400 text-sm mt-6">
                    © 2025 FinGuard. All rights reserved.
                </p>
            </div>
        </div>
    );
};

export default VerifyEmail;
