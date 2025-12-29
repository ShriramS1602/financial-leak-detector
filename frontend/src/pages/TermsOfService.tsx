import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

const TermsOfService: React.FC = () => {
    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden">
                <div className="px-8 py-6 border-b border-gray-100 flex items-center gap-4">
                    <Link to="/login" className="p-2 -ml-2 rounded-full hover:bg-gray-100 transition-colors">
                        <ArrowLeft className="h-5 w-5 text-gray-500" />
                    </Link>
                    <h1 className="text-2xl font-bold text-gray-900">Terms of Service</h1>
                </div>
                <div className="p-8 prose prose-indigo max-w-none">
                    <p className="text-gray-600">Last updated: {new Date().toLocaleDateString()}</p>

                    <h3>1. Agreement to Terms</h3>
                    <p>
                        By accessing our website, you agree to be bound by these Terms of Service and to comply with all applicable laws and regulations.
                        If you do not agree with these terms, you are prohibited from using or accessing this site.
                    </p>

                    <h3>2. Use License</h3>
                    <p>
                        Permission is granted to temporarily download one copy of the materials (information or software) on FinGuard's website for personal,
                        non-commercial transitory viewing only. This is the grant of a license, not a transfer of title.
                    </p>

                    <h3>3. Disclaimer</h3>
                    <p>
                        The materials on FinGuard's website are provided on an 'as is' basis. FinGuard makes no warranties, expressed or implied,
                        and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability,
                        fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.
                    </p>

                    <h3>4. Limitations</h3>
                    <p>
                        In no event shall FinGuard or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit,
                        or due to business interruption) arising out of the use or inability to use the materials on FinGuard's website.
                    </p>

                    <h3>5. Governing Law</h3>
                    <p>
                        These terms and conditions are governed by and construed in accordance with the laws and you irrevocably submit to the exclusive
                        jurisdiction of the courts in that location.
                    </p>
                </div>
            </div>
        </div>
    );
};

export default TermsOfService;
