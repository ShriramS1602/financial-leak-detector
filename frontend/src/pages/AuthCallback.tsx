import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { api } from '../services/api';
import ConsentModal from '../components/ConsentModal';

const AuthCallback: React.FC = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    const [showConsent, setShowConsent] = useState(false);
    const [error, setError] = useState('');

    useEffect(() => {
        const token = searchParams.get('token');
        const needsConsent = searchParams.get('needs_consent') === 'true';
        const errorParam = searchParams.get('error');

        if (errorParam) {
            navigate(`/login?error=${errorParam}`);
            return;
        }

        if (token) {
            api.setToken(token);
            if (needsConsent) {
                setShowConsent(true);
            } else {
                navigate('/');
            }
        } else {
            navigate('/login?error=no_token');
        }
    }, [searchParams, navigate]);

    const handleConsentSuccess = () => {
        navigate('/');
    };

    if (showConsent) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <ConsentModal isOpen={true} onSuccess={handleConsentSuccess} />
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center">
            <Loader2 className="h-10 w-10 text-indigo-600 animate-spin mb-4" />
            <p className="text-gray-600 font-medium">Completing authentication...</p>
            {error && <p className="text-red-500 mt-2">{error}</p>}
        </div>
    );
};

export default AuthCallback;
