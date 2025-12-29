import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Lock, User, ArrowRight, AlertCircle, Eye, EyeOff, Loader2, CheckCircle2, XCircle, Check } from 'lucide-react';
import { authService } from '../services/api';
import AuthLayout from '../components/AuthLayout';
import PolicyModal from '../components/PolicyModal';

interface PasswordStrength {
    score: number;
    label: string;
    color: string;
}

const Signup: React.FC = () => {
    const [formData, setFormData] = useState({
        username: '',
        name: '',
        email: '',
        password: '',
        confirmPassword: ''
    });
    const [termsAccepted, setTermsAccepted] = useState(false);
    const [privacyAccepted, setPrivacyAccepted] = useState(false);
    const [showTerms, setShowTerms] = useState(false);
    const [showPrivacy, setShowPrivacy] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [googleLoading, setGoogleLoading] = useState(false);
    const [emailExists, setEmailExists] = useState(false);
    const [checkingEmail, setCheckingEmail] = useState(false);

    // Password validation criteria
    const passwordCriteria = {
        minLength: formData.password.length >= 8,
        hasUppercase: /[A-Z]/.test(formData.password),
        hasLowercase: /[a-z]/.test(formData.password),
        hasNumber: /\d/.test(formData.password),
        hasSpecial: /[@$!%*?&]/.test(formData.password),
    };

    const passwordsMatch = formData.password === formData.confirmPassword && formData.confirmPassword !== '';

    // Calculate password strength
    const getPasswordStrength = (): PasswordStrength => {
        const criteriaCount = Object.values(passwordCriteria).filter(Boolean).length;
        if (criteriaCount <= 1) return { score: 1, label: 'Weak', color: 'bg-red-500' };
        if (criteriaCount <= 2) return { score: 2, label: 'Fair', color: 'bg-orange-500' };
        if (criteriaCount <= 3) return { score: 3, label: 'Good', color: 'bg-yellow-500' };
        if (criteriaCount <= 4) return { score: 4, label: 'Strong', color: 'bg-lime-500' };
        return { score: 5, label: 'Excellent', color: 'bg-green-500' };
    };

    const passwordStrength = getPasswordStrength();

    // Check if email exists (debounced)
    useEffect(() => {
        const checkEmail = async () => {
            if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
                setEmailExists(false);
                return;
            }
            setCheckingEmail(true);
            try {
                const result = await authService.checkEmail(formData.email);
                setEmailExists(result.exists);
            } catch (err) {
                // Ignore errors for email check
            } finally {
                setCheckingEmail(false);
            }
        };

        const timeoutId = setTimeout(checkEmail, 500);
        return () => clearTimeout(timeoutId);
    }, [formData.email]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        setError('');
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        // Validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(formData.email)) {
            setError('Please enter a valid email address.');
            return;
        }

        if (emailExists) {
            setError('This email is already registered. Please sign in instead.');
            return;
        }

        if (!Object.values(passwordCriteria).every(Boolean)) {
            setError('Password does not meet all requirements.');
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match.');
            return;
        }

        if (!termsAccepted || !privacyAccepted) {
            setError('Please accept the Terms of Service and Privacy Policy.');
            return;
        }

        if (!formData.username) {
            setError('Username is required.');
            return;
        }

        setLoading(true);
        try {
            await authService.signup(
                formData.email,
                formData.password,
                formData.username,
                formData.name,
                termsAccepted,
                privacyAccepted
            );
            setSuccess(true);
        } catch (err: any) {
            setError(err.message || 'Failed to create account. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleSignup = async () => {
        if (!termsAccepted || !privacyAccepted) {
            setError('Please accept the Terms of Service and Privacy Policy before continuing with Google.');
            return;
        }

        setGoogleLoading(true);
        try {
            const data = await authService.initiateGoogleSignup();
            window.location.href = data.authorization_url;
        } catch (err: any) {
            setError('Failed to initiate Google signup. Please try again.');
            setGoogleLoading(false);
        }
    };

    // Success State
    if (success) {
        return (
            <AuthLayout
                title="Check Your Email"
                subtitle="We've sent you a verification link"
            >
                <div className="text-center space-y-6">
                    <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 shadow-lg">
                        <CheckCircle2 className="h-10 w-10 text-white" />
                    </div>
                    <div className="space-y-2">
                        <h3 className="text-lg font-semibold text-gray-900">Almost there!</h3>
                        <p className="text-sm text-gray-600">
                            We've sent a verification email to <span className="font-medium text-gray-900">{formData.email}</span>
                        </p>
                        <p className="text-sm text-gray-500">
                            Click the link in your email to activate your account and start your journey to financial freedom.
                        </p>
                    </div>
                    <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
                        <p className="text-sm text-amber-800">
                            <span className="font-medium">💡 Tip:</span> Check your spam folder if you don't see the email within a few minutes.
                        </p>
                    </div>
                    <div className="space-y-3">
                        <Link
                            to="/login"
                            className="block w-full py-3 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg shadow-indigo-500/25 text-center"
                        >
                            Go to Login
                        </Link>
                        <button
                            onClick={() => {
                                authService.resendVerification(formData.email);
                                alert('Verification email resent!');
                            }}
                            className="w-full py-3 px-4 border border-gray-200 text-gray-700 font-medium rounded-xl hover:bg-gray-50 transition-all duration-200"
                        >
                            Resend Verification Email
                        </button>
                    </div>
                </div>
            </AuthLayout>
        );
    }

    return (
        <AuthLayout
            title="Create an account"
            subtitle="Start your journey to financial freedom"
        >
            <form className="space-y-3" onSubmit={handleSubmit}>
                {error && (
                    <div className="rounded-xl bg-red-50 p-4 border border-red-100 animate-in slide-in-from-top-2 duration-200">
                        <div className="flex items-start">
                            <AlertCircle className="h-5 w-5 text-red-400 mr-3 flex-shrink-0 mt-0.5" />
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                )}

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {/* Username Field */}
                    <div>
                        <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-1.5">
                            Username
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                <User className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                            </div>
                            <input
                                id="username"
                                name="username"
                                type="text"
                                autoComplete="username"
                                required
                                className="block w-full pl-11 pr-4 py-2 border border-gray-200 rounded-xl bg-gray-50/50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm"
                                placeholder="johndoe123"
                                value={formData.username}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    {/* Name Field */}
                    <div>
                        <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1.5">
                            Full Name
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                <User className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                            </div>
                            <input
                                id="name"
                                name="name"
                                type="text"
                                autoComplete="name"
                                required
                                className="block w-full pl-11 pr-4 py-2 border border-gray-200 rounded-xl bg-gray-50/50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm"
                                placeholder="John Doe"
                                value={formData.name}
                                onChange={handleInputChange}
                            />
                        </div>
                    </div>

                    {/* Email Field */}
                    <div className="col-span-1 sm:col-span-2">
                        <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1.5">
                            Email address
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                <Mail className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                            </div>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                autoComplete="email"
                                required
                                className={`block w-full pl-11 pr-12 py-2 border rounded-xl bg-gray-50/50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 transition-all duration-200 sm:text-sm ${emailExists
                                    ? 'border-red-300 focus:ring-red-500/20 focus:border-red-500'
                                    : 'border-gray-200 focus:ring-indigo-500/20 focus:border-indigo-500'
                                    }`}
                                placeholder="you@example.com"
                                value={formData.email}
                                onChange={handleInputChange}
                            />
                            <div className="absolute inset-y-0 right-0 pr-3.5 flex items-center">
                                {checkingEmail ? (
                                    <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
                                ) : emailExists ? (
                                    <XCircle className="h-5 w-5 text-red-500" />
                                ) : formData.email && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email) ? (
                                    <CheckCircle2 className="h-5 w-5 text-green-500" />
                                ) : null}
                            </div>
                        </div>
                        {emailExists && (
                            <p className="mt-1.5 text-sm text-red-600">
                                This email is already registered. <Link to="/login" className="font-medium underline">Sign in instead</Link>
                            </p>
                        )}
                    </div>

                    {/* Password Field */}
                    <div>
                        <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1.5">
                            Password
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                            </div>
                            <input
                                id="password"
                                name="password"
                                type={showPassword ? 'text' : 'password'}
                                autoComplete="new-password"
                                required
                                className="block w-full pl-11 pr-12 py-2 border border-gray-200 rounded-xl bg-gray-50/50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 sm:text-sm"
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={handleInputChange}
                            />
                            <button
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                            >
                                {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                        </div>

                        {/* Password Strength Indicator */}
                        {formData.password && (
                            <div className="mt-3 space-y-2">
                                <div className="flex items-center justify-between">
                                    <span className="text-xs text-gray-500">Password strength</span>
                                    <span className={`text-xs font-medium ${passwordStrength.score <= 2 ? 'text-red-600' :
                                        passwordStrength.score <= 3 ? 'text-yellow-600' : 'text-green-600'
                                        }`}>{passwordStrength.label}</span>
                                </div>
                                <div className="h-1 bg-gray-200 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${passwordStrength.color} transition-all duration-300`}
                                        style={{ width: `${(passwordStrength.score / 5) * 100}%` }}
                                    />
                                </div>
                                <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2">
                                    {!passwordsMatch && [
                                        { key: 'minLength', label: '8+ characters' },
                                        { key: 'hasUppercase', label: 'Uppercase' },
                                        { key: 'hasLowercase', label: 'Lowercase' },
                                        { key: 'hasNumber', label: 'Number' },
                                        { key: 'hasSpecial', label: 'Special (@$!%*?&)' },
                                    ].map(({ key, label }) => (
                                        <div key={key} className="flex items-center text-xs">
                                            {passwordCriteria[key as keyof typeof passwordCriteria] ? (
                                                <Check className="h-3.5 w-3.5 text-green-500 mr-1.5" />
                                            ) : (
                                                <div className="h-3.5 w-3.5 border border-gray-300 rounded mr-1.5" />
                                            )}
                                            <span className={passwordCriteria[key as keyof typeof passwordCriteria] ? 'text-green-700' : 'text-gray-500'}>
                                                {label}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Confirm Password Field */}
                    <div>
                        <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1.5">
                            Confirm Password
                        </label>
                        <div className="relative group">
                            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                            </div>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type={showConfirmPassword ? 'text' : 'password'}
                                autoComplete="new-password"
                                required
                                className={`block w-full pl-11 pr-12 py-2 border rounded-xl bg-gray-50/50 text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 transition-all duration-200 sm:text-sm ${formData.confirmPassword && !passwordsMatch
                                    ? 'border-red-300 focus:ring-red-500/20 focus:border-red-500'
                                    : 'border-gray-200 focus:ring-indigo-500/20 focus:border-indigo-500'
                                    }`}
                                placeholder="••••••••"
                                value={formData.confirmPassword}
                                onChange={handleInputChange}
                            />
                            <button
                                type="button"
                                onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors"
                            >
                                {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                            </button>
                        </div>
                        {formData.confirmPassword && !passwordsMatch && (
                            <p className="mt-1.5 text-sm text-red-600">Passwords do not match</p>
                        )}
                        {passwordsMatch && (
                            <p className="mt-1.5 text-sm text-green-600 flex items-center">
                                <Check className="h-4 w-4 mr-1" /> Passwords match
                            </p>
                        )}
                    </div>
                </div>

                {/* Terms & Privacy */}
                <div className="space-y-3 pt-2">
                    <div className="flex items-start">
                        <input
                            id="terms"
                            name="terms"
                            type="checkbox"
                            checked={termsAccepted}
                            onChange={(e) => setTermsAccepted(e.target.checked)}
                            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer mt-0.5"
                        />
                        <label htmlFor="terms" className="ml-2 block text-sm text-gray-600 cursor-pointer">
                            I agree to the{' '}
                            <button
                                type="button"
                                onClick={() => setShowTerms(true)}
                                className="font-medium text-indigo-600 hover:text-indigo-500 focus:outline-none"
                            >
                                Terms of Service
                            </button>
                        </label>
                    </div>
                    <div className="flex items-start">
                        <input
                            id="privacy"
                            name="privacy"
                            type="checkbox"
                            checked={privacyAccepted}
                            onChange={(e) => setPrivacyAccepted(e.target.checked)}
                            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer mt-0.5"
                        />
                        <label htmlFor="privacy" className="ml-2 block text-sm text-gray-600 cursor-pointer">
                            I agree to the{' '}
                            <button
                                type="button"
                                onClick={() => setShowPrivacy(true)}
                                className="font-medium text-indigo-600 hover:text-indigo-500 focus:outline-none"
                            >
                                Privacy Policy
                            </button>
                        </label>
                    </div>
                </div>

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={loading || emailExists}
                    className="w-full py-2.5 px-4 bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-medium rounded-xl hover:from-indigo-700 hover:to-purple-700 transition-all duration-200 shadow-lg shadow-indigo-500/25 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center group sm:text-sm"
                >
                    {loading ? (
                        <>
                            <Loader2 className="animate-spin h-5 w-5 mr-2" />
                            Creating account...
                        </>
                    ) : (
                        <>
                            Create Account
                            <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                        </>
                    )}
                </button>
            </form>

            {/* Divider */}
            <div className="my-4 relative">
                <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-200" />
                </div>
                <div className="relative flex justify-center text-sm">
                    <span className="px-4 bg-white text-gray-500 font-medium">or continue with</span>
                </div>
            </div>

            {/* Google Signup */}
            <button
                onClick={handleGoogleSignup}
                disabled={googleLoading}
                className="w-full flex items-center justify-center py-2.5 px-4 border-2 border-gray-200 rounded-xl bg-white text-gray-700 font-medium hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 disabled:opacity-60 disabled:cursor-not-allowed group sm:text-sm"
            >
                {googleLoading ? (
                    <Loader2 className="animate-spin h-5 w-5 mr-2" />
                ) : (
                    <svg className="h-5 w-5 mr-3" viewBox="0 0 24 24">
                        <path
                            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                            fill="#4285F4"
                        />
                        <path
                            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                            fill="#34A853"
                        />
                        <path
                            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.84z"
                            fill="#FBBC05"
                        />
                        <path
                            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                            fill="#EA4335"
                        />
                    </svg>
                )}
                Sign up with Google
            </button>

            {/* Login Link */}
            <p className="mt-4 text-center text-sm text-gray-600">
                Already have an account?{' '}
                <Link
                    to="/login"
                    className="font-semibold text-indigo-600 hover:text-indigo-500 transition-colors"
                >
                    Sign in
                </Link>
            </p>

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
        </AuthLayout>
    );
};

export default Signup;
