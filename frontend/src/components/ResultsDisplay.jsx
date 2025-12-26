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

    const { summary, confidence, tests, disclaimer } = results;

    const getClassificationColor = (classification) => {
        switch (classification) {
            case 'LOW':
                return '#3b82f6'; // Blue
            case 'NORMAL':
                return '#10b981'; // Green
            case 'HIGH':
                return '#ef4444'; // Red
            default:
                return '#6b7280'; // Gray
        }
    };

    const getConfidenceColor = (level) => {
        switch (level) {
            case 'HIGH':
                return '#10b981';
            case 'MEDIUM':
                return '#f59e0b';
            case 'LOW':
                return '#ef4444';
            default:
                return '#6b7280';
        }
    };

    return (
        <div className="results-container">
            {/* Summary Cards */}
            <div className="summary-grid">
                <div className="summary-card">
                    <div className="summary-icon">🧪</div>
                    <div className="summary-content">
                        <div className="summary-value">{summary.total_tests}</div>
                        <div className="summary-label">Total Tests</div>
                    </div>
                </div>

                <div className="summary-card">
                    <div className="summary-icon">📊</div>
                    <div className="summary-content">
                        <div className="summary-value">{summary.kb_match_rate}</div>
                        <div className="summary-label">KB Match Rate</div>
                    </div>
                </div>

                <div className="summary-card">
                    <div className="summary-icon">🎯</div>
                    <div className="summary-content">
                        <div className="summary-value" style={{ color: getConfidenceColor(confidence.confidence_level) }}>
                            {confidence.confidence_level}
                        </div>
                        <div className="summary-label">OCR Confidence</div>
                    </div>
                </div>

                <div className="summary-card">
                    <div className="summary-icon">✅</div>
                    <div className="summary-content">
                        <div className="summary-value">{summary.normal_results}</div>
                        <div className="summary-label">Normal Results</div>
                    </div>
                </div>
            </div>

            {/* Test Results */}
            <div className="tests-section">
                <h2 className="section-title">Test Results</h2>

                <div className="tests-grid">
                    {tests.map((test, index) => (
                        <div key={index} className="test-card">
                            <div className="test-header">
                                <div className="test-name-section">
                                    <h3 className="test-name">{test.test_name}</h3>
                                    {test.panel_name && (
                                        <span className="panel-badge">{test.panel_name}</span>
                                    )}
                                </div>
                                <span
                                    className="classification-badge"
                                    style={{ backgroundColor: getClassificationColor(test.classification) }}
                                >
                                    {test.classification}
                                </span>
                            </div>

                            <div className="test-value-section">
                                <div className="test-value">
                                    {test.value} <span className="test-unit">{test.unit}</span>
                                </div>
                                <div className="test-reference">
                                    Reference: {test.reference_range}
                                </div>
                            </div>

                            {test.ai_explanation && (
                                <div className="test-explanation">
                                    <div className="explanation-icon">💡</div>
                                    <p>{test.ai_explanation}</p>
                                </div>
                            )}

                            <div className="test-footer">
                                {test.kb_found ? (
                                    <span className="kb-badge kb-found">✓ In Knowledge Base</span>
                                ) : (
                                    <span className="kb-badge kb-not-found">⚠ Not in KB</span>
                                )}
                            </div>
                        </div>
                    ))}
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
