import React, { useState } from 'react';
import { Mail, Upload, FileText, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import api from '../services/api';

interface DataSourceSelectionProps {
    onDataLoaded: () => void;
}

const DataSourceSelection: React.FC<DataSourceSelectionProps> = ({ onDataLoaded }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [useAi, setUseAi] = useState(true);

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setLoading(true);
        setError(null);
        try {
            await api.uploadCsv(file);
            onDataLoaded();
        } catch (err) {
            console.error('Upload failed:', err);
            setError('Failed to upload CSV. Please check the file format.');
        } finally {
            setLoading(false);
        }
    };

    const handleGmailSync = async () => {
        setLoading(true);
        setError(null);
        try {
            await api.syncEmails(30, 100, useAi);
            onDataLoaded();
        } catch (err) {
            console.error('Sync failed:', err);
            setError('Failed to sync emails. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-4xl w-full space-y-8">
                <div className="text-center">
                    <h2 className="text-3xl font-extrabold text-gray-900">
                        Choose Your Data Source
                    </h2>
                    <p className="mt-2 text-lg text-gray-600">
                        How would you like to import your financial data?
                    </p>
                </div>

                {error && (
                    <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
                        <div className="flex">
                            <AlertCircle className="h-5 w-5 text-red-400" />
                            <p className="ml-3 text-sm text-red-700">{error}</p>
                        </div>
                    </div>
                )}

                {loading ? (
                    <div className="flex flex-col items-center justify-center py-12">
                        <Loader2 className="h-12 w-12 text-blue-600 animate-spin" />
                        <p className="mt-4 text-lg font-medium text-gray-900">Processing your data...</p>
                        <p className="text-gray-500">This might take a moment.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-8">
                        {/* CSV Upload Option */}
                        <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
                            <div className="p-8 text-center">
                                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
                                    <FileText className="h-8 w-8 text-green-600" />
                                </div>
                                <h3 className="mt-6 text-xl font-medium text-gray-900">Upload CSV</h3>
                                <p className="mt-2 text-gray-500">
                                    Upload your bank statement or transaction history in CSV format.
                                </p>
                                <div className="mt-8">
                                    <label className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 cursor-pointer">
                                        <Upload className="mr-2 -ml-1 h-5 w-5" />
                                        Select File
                                        <input
                                            type="file"
                                            accept=".csv"
                                            className="hidden"
                                            onChange={handleFileUpload}
                                        />
                                    </label>
                                </div>
                            </div>
                        </div>

                        {/* Gmail Sync Option */}
                        <div className="bg-white overflow-hidden shadow rounded-lg hover:shadow-xl transition-shadow duration-300 border border-gray-200">
                            <div className="p-8 text-center">
                                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-blue-100">
                                    <Mail className="h-8 w-8 text-blue-600" />
                                </div>
                                <h3 className="mt-6 text-xl font-medium text-gray-900">Sync from Gmail</h3>
                                <p className="mt-2 text-gray-500">
                                    Connect your Gmail account to automatically find transaction emails.
                                </p>

                                <div className="mt-4 flex items-center justify-center space-x-2">
                                    <input
                                        id="use-ai"
                                        type="checkbox"
                                        checked={useAi}
                                        onChange={(e) => setUseAi(e.target.checked)}
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                    <label htmlFor="use-ai" className="text-sm text-gray-700">
                                        Use AI Analysis (Slower but more accurate)
                                    </label>
                                </div>

                                <div className="mt-6">
                                    <button
                                        onClick={handleGmailSync}
                                        className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                    >
                                        <CheckCircle className="mr-2 -ml-1 h-5 w-5" />
                                        Sync Now
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DataSourceSelection;
