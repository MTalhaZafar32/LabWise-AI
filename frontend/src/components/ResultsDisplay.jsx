import React from 'react';
import './ResultsDisplay.css';

const ResultsDisplay = ({ results }) => {
    if (!results || !results.success) {
        return (
            <div className="error-container">
                <div className="error-icon">⚠️</div>
                <h3>Analysis Failed</h3>
                <p>{results?.error || 'An error occurred during analysis'}</p>
            </div>
        );
    }

    const { summary, confidence, disclaimer, overall_summary } = results;

    const getConfidenceColor = (level) => {
        switch (level) {
            case 'HIGH':
                return '#10b981'; // Green
            case 'MEDIUM':
                return '#f59e0b'; // Amber
            case 'LOW':
                return '#ef4444'; // Red
            default:
                return '#6b7280'; // Gray
        }
    };

    return (
        <div className="results-container">
            {/* Header Section with Confidence Scores */}
            <div className="summary-grid">
                {/* KB Match Rate */}
                <div className="summary-card">
                    <div className="summary-icon">📚</div>
                    <div className="summary-content">
                        <div className="summary-value" style={{ color: '#3b82f6' }}>
                            {summary?.kb_match_rate || '0%'}
                        </div>
                        <div className="summary-label">KB Match Rate</div>
                    </div>
                </div>

                {/* Response Confidence */}
                <div className="summary-card">
                    <div className="summary-icon">🧠</div>
                    <div className="summary-content">
                        <div className="summary-value" style={{ color: getConfidenceColor(confidence?.response_level) }}>
                            {confidence?.response_confidence ? `${(confidence.response_confidence * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                        <div className="summary-label">AI Confidence</div>
                    </div>
                </div>

                {/* OCR Confidence */}
                <div className="summary-card">
                    <div className="summary-icon">👁️</div>
                    <div className="summary-content">
                        <div className="summary-value" style={{ color: getConfidenceColor(confidence?.ocr_level) }}>
                            {confidence?.ocr_confidence ? `${(confidence.ocr_confidence * 100).toFixed(0)}%` : 'N/A'}
                        </div>
                        <div className="summary-label">OCR Confidence</div>
                    </div>
                </div>
            </div>

            {/* Main Summary Section */}
            <div className="tests-section">
                <h2 className="section-title">Analysis Summary</h2>
                <div className="test-card" style={{ padding: '2rem' }}>
                    <div className="test-explanation" style={{ marginTop: 0, backgroundColor: 'transparent', padding: 0 }}>
                        <p style={{ fontSize: '1.1rem', lineHeight: '1.8', color: '#e2e8f0' }}>
                            {overall_summary || 'No summary available'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Disclaimer */}
            <div className="disclaimer">
                <div className="disclaimer-icon">⚠️</div>
                <p>{disclaimer}</p>
            </div>
        </div>
    );
};

export default ResultsDisplay;
