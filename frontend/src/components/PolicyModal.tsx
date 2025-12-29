import React from 'react';
import ReactDOM from 'react-dom';
import { X } from 'lucide-react';

interface PolicyModalProps {
    isOpen: boolean;
    onClose: () => void;
    type: 'terms' | 'privacy';
}

const PolicyModal: React.FC<PolicyModalProps> = ({ isOpen, onClose, type }) => {
    if (!isOpen) return null;

    const title = type === 'terms' ? 'Terms of Service' : 'Privacy Policy';

    const TermsContent = () => (
        <div className="space-y-6">
            <p className="text-gray-600">Last updated: {new Date().toLocaleDateString()}</p>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Agreement to Terms</h3>
                <p className="text-gray-600">
                    By accessing our website, you agree to be bound by these Terms of Service and to comply with all applicable laws and regulations.
                    If you do not agree with these terms, you are prohibited from using or accessing this site.
                </p>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Use License</h3>
                <p className="text-gray-600">
                    Permission is granted to temporarily download one copy of the materials (information or software) on FinGuard's website for personal,
                    non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.
                </p>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">3. Disclaimer</h3>
                <p className="text-gray-600">
                    The materials on FinGuard's website are provided on an 'as is' basis. FinGuard makes no warranties, expressed or implied,
                    and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability,
                    fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
                </p>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Limitations</h3>
                <p className="text-gray-600">
                    In no event shall FinGuard or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit,
                    or due to business interruption) arising out of the use or inability to use the materials on FinGuard's website.
                </p>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">5. Governing Law</h3>
                <p className="text-gray-600">
                    These terms and conditions are governed by and construed in accordance with the laws and you irrevocably submit to the exclusive
                    jurisdiction of the courts in that location.
                </p>
            </div>
        </div>
    );

    const PrivacyContent = () => (
        <div className="space-y-6">
            <p className="text-gray-600">Last updated: {new Date().toLocaleDateString()}</p>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">1. Introduction</h3>
                <p className="text-gray-600">
                    Welcome to FinGuard. We respect your privacy and are committed to protecting your personal data.
                    This privacy policy will inform you as to how we look after your personal data when you visit our website
                    and tell you about your privacy rights and how the law protects you.
                </p>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">2. Data We Collect</h3>
                <p className="text-gray-600 mb-2">
                    We may collect, use, store and transfer different kinds of personal data about you which we have grouped together follows:
                </p>
                <ul className="list-disc pl-5 space-y-2 text-gray-600">
                    <li><strong>Identity Data</strong> includes first name, last name, username or similar identifier.</li>
                    <li><strong>Contact Data</strong> includes email address and telephone numbers.</li>
                    <li><strong>Financial Data</strong> includes bank account and payment card details (encrypted).</li>
                    <li><strong>Transaction Data</strong> includes details about payments to and from you.</li>
                </ul>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">3. How We Use Your Data</h3>
                <p className="text-gray-600 mb-2">
                    We will only use your personal data when the law allows us to. Most commonly, we will use your personal data in the following circumstances:
                </p>
                <ul className="list-disc pl-5 space-y-2 text-gray-600">
                    <li>Where we need to perform the contract we are about to enter into or have entered into with you.</li>
                    <li>Where it is necessary for our legitimate interests (or those of a third party) and your interests and fundamental rights do not override those interests.</li>
                    <li>Where we need to comply with a legal or regulatory obligation.</li>
                </ul>
            </div>

            <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">4. Data Security</h3>
                <p className="text-gray-600">
                    We have put in place appropriate security measures to prevent your personal data from being accidentally lost, used or accessed in an unauthorized way, altered or disclosed.
                </p>
            </div>
        </div>
    );

    return ReactDOM.createPortal(
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
            <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[80vh] flex flex-col relative animate-in zoom-in-95 duration-200">
                <div className="flex items-center justify-between p-6 border-b border-gray-100">
                    <h2 className="text-xl font-semibold text-gray-900">{title}</h2>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-full hover:bg-gray-100"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>

                <div className="p-6 overflow-y-auto custom-scrollbar">
                    {type === 'terms' ? <TermsContent /> : <PrivacyContent />}
                </div>

                <div className="p-6 border-t border-gray-100 bg-gray-50 rounded-b-2xl flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-6 py-2.5 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-colors shadow-sm shadow-indigo-500/20"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>,
        document.body
    );
};

export default PolicyModal;
