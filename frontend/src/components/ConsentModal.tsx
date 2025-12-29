import React, { useState } from 'react';
import { Shield, Loader2, Check } from 'lucide-react';
import { authService } from '../services/api';
import PolicyModal from './PolicyModal';

interface ConsentModalProps {
    isOpen: boolean;
    onSuccess: () => void;
}

const ConsentModal: React.FC<ConsentModalProps> = ({ isOpen, onSuccess }) => {
    const [termsAccepted, setTermsAccepted] = useState(false);
    const [privacyAccepted, setPrivacyAccepted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [policyModal, setPolicyModal] = useState<{ isOpen: boolean; type: 'terms' | 'privacy' }>({
        isOpen: false,
        type: 'terms'
    });

    if (!isOpen) return null;

    const handleAccept = async () => {
        if (!termsAccepted || !privacyAccepted) {
            setError('Please accept both the Terms of Service and Privacy Policy.');
            return;
        }

        setLoading(true);
        setError('');

        try {
            await authService.acceptTerms();
            onSuccess();
        } catch (err: any) {
            setError('Failed to accept terms. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const openPolicyModal = (type: 'terms' | 'privacy') => {
        setPolicyModal({ isOpen: true, type });
    };

    const closePolicyModal = () => {
        setPolicyModal({ ...policyModal, isOpen: false });
    };

    return (
        <>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
                <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 relative animate-in zoom-in-95 duration-200">
                    <div className="text-center mb-6">
                        <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-indigo-100 mb-4">
                            <Shield className="h-6 w-6 text-indigo-600" />
                        </div>
                        <h2 className="text-xl font-semibold text-gray-900">Final Step</h2>
                        <p className="text-sm text-gray-500 mt-1">
                            Please review and accept our policies to complete your account setup.
                        </p>
                    </div>

                    {error && (
                        <div className="mb-4 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-600">
                            {error}
                        </div>
                    )}

                    <div className="space-y-4 mb-6">
                        <div className="flex items-start p-3 bg-gray-50 rounded-lg border border-gray-100">
                            <input
                                id="modal-terms"
                                type="checkbox"
                                checked={termsAccepted}
                                onChange={(e) => setTermsAccepted(e.target.checked)}
                                className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
                            />
                            <label htmlFor="modal-terms" className="ml-3 block text-sm text-gray-600 cursor-pointer">
                                I agree to the{' '}
                                <button
                                    type="button"
                                    onClick={() => openPolicyModal('terms')}
                                    className="font-medium text-indigo-600 hover:text-indigo-500 underline"
                                >
                                    Terms of Service
                                </button>
                            </label>
                        </div>

                        <div className="flex items-start p-3 bg-gray-50 rounded-lg border border-gray-100">
                            <input
                                id="modal-privacy"
                                type="checkbox"
                                checked={privacyAccepted}
                                onChange={(e) => setPrivacyAccepted(e.target.checked)}
                                className="mt-1 h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
                            />
                            <label htmlFor="modal-privacy" className="ml-3 block text-sm text-gray-600 cursor-pointer">
                                I agree to the{' '}
                                <button
                                    type="button"
                                    onClick={() => openPolicyModal('privacy')}
                                    className="font-medium text-indigo-600 hover:text-indigo-500 underline"
                                >
                                    Privacy Policy
                                </button>
                            </label>
                        </div>
                    </div>

                    <button
                        onClick={handleAccept}
                        disabled={loading || !termsAccepted || !privacyAccepted}
                        className="w-full py-3 px-4 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 focus:ring-4 focus:ring-indigo-500/20 transition-all disabled:opacity-60 disabled:cursor-not-allowed flex justify-center items-center"
                    >
                        {loading ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                            <>
                                Complete Setup
                                <Check className="ml-2 h-4 w-4" />
                            </>
                        )}
                    </button>
                </div>
            </div>

            {/* Policy Modal */}
            <PolicyModal
                isOpen={policyModal.isOpen}
                onClose={closePolicyModal}
                type={policyModal.type}
            />
        </>
    );
};

export default ConsentModal;
