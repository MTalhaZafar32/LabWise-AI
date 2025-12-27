import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import ResultsDisplay from './components/ResultsDisplay';
import Statistics from './pages/Statistics';
import api from './services/api';
import './App.css';

function App() {
    const [isProcessing, setIsProcessing] = useState(false);
    const [uploadProgress, setUploadProgress] = useState(0);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);
    const [currentPage, setCurrentPage] = useState('upload'); // 'upload' or 'stats'

    const handleFileSelect = async (file) => {
        setIsProcessing(true);
        setUploadProgress(0);
        setError(null);
        setResults(null);

        try {
            const response = await api.analyzeReport(file, (progress) => {
                setUploadProgress(progress);
            });

            setResults(response);
        } catch (err) {
            console.error('Analysis error:', err);
            setError(err.response?.data?.detail || 'Failed to analyze report. Please try again.');
        } finally {
            setIsProcessing(false);
            setUploadProgress(0);
        }
    };

    const handleReset = () => {
        setResults(null);
        setError(null);
    };

    return (
        <div className="app">
            {/* Background */}
            <div className="background-gradient"></div>
            <div className="background-pattern"></div>

            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <div className="logo-section">
                        <div className="logo">🧬</div>
                        <div className="logo-text">
                            <h1>LabWise AI</h1>
                            <p>Autonomous Medical Lab Report Interpreter</p>
                        </div>
                    </div>
                </div>
                {currentPage === 'upload' && (
                    <button
                        className="stats-nav-button"
                        onClick={() => setCurrentPage('stats')}
                    >
                        📊 View KB Statistics
                    </button>
                )}
            </header>

            {/* Main Content */}
            <main className="app-main">
                {currentPage === 'stats' ? (
                    <Statistics onBack={() => setCurrentPage('upload')} />
                ) : (
                    <>
                        {!results && !error && (
                            <div className="upload-section">
                                <div className="intro-text">
                                    <h2>Upload Your Lab Report</h2>
                                    <p>Get instant AI-powered analysis with clear explanations</p>
                                </div>
                                <FileUpload onFileSelect={handleFileSelect} isProcessing={isProcessing} />

                                {isProcessing && (
                                    <div className="processing-indicator">
                                        <div className="spinner"></div>
                                        <p className="processing-text">
                                            {uploadProgress < 100 ? `Uploading... ${uploadProgress}%` : 'Analyzing your report...'}
                                        </p>
                                        <div className="progress-bar">
                                            <div className="progress-fill" style={{ width: `${uploadProgress}%` }}></div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {error && (
                            <div className="error-section">
                                <div className="error-message">
                                    <div className="error-icon">❌</div>
                                    <h3>Error</h3>
                                    <p>{error}</p>
                                    <button className="retry-button" onClick={handleReset}>
                                        Try Again
                                    </button>
                                </div>
                            </div>
                        )}

                        {results && (
                            <div className="results-section">
                                <button className="new-analysis-button" onClick={handleReset}>
                                    ← New Analysis
                                </button>
                                <ResultsDisplay results={results} />
                            </div>
                        )}
                    </>
                )}
            </main>

            {/* Footer */}
            <footer className="app-footer">
                <p>
                    LabWise AI uses OCR, RAG, and local LLM for privacy-preserving medical report analysis
                </p>
                <p className="footer-note">
                    All processing happens locally • No data leaves your device
                </p>
            </footer>
        </div>
    );
}

export default App;


