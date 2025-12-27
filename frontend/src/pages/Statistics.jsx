import React, { useState, useEffect } from 'react';
import api from '../services/api';
import './Statistics.css';

const Statistics = ({ onBack }) => {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchStatistics();
    }, []);

    const fetchStatistics = async () => {
        try {
            setLoading(true);
            const data = await api.getStatistics();
            setStats(data);
        } catch (err) {
            console.error('Error fetching statistics:', err);
            setError('Failed to load statistics');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="stats-container">
                <div className="stats-loading">
                    <div className="spinner"></div>
                    <p>Loading statistics...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="stats-container">
                <div className="stats-error">
                    <div className="error-icon">⚠️</div>
                    <h3>Error</h3>
                    <p>{error}</p>
                    <button onClick={fetchStatistics} className="retry-button">Retry</button>
                </div>
            </div>
        );
    }

    if (!stats) return null;

    const { overview, distributions, top_sources } = stats;

    return (
        <div className="stats-container">
            <div className="stats-header">
                <button className="back-button" onClick={onBack}>
                    ← Back to Upload
                </button>
                <div className="stats-title">
                    <h1>📊 Knowledge Base Statistics</h1>
                    <p>Comprehensive overview of the LabWise AI medical test database</p>
                </div>
            </div>

            {/* Overview Cards */}
            <div className="overview-grid">
                <div className="stat-card secondary">
                    <div className="stat-icon">📚</div>
                    <div className="stat-content">
                        <div className="stat-value">{overview.total_sources.toLocaleString()}</div>
                        <div className="stat-label">Reference Sources</div>
                    </div>
                </div>

                <div className="stat-card tertiary">
                    <div className="stat-icon">📏</div>
                    <div className="stat-content">
                        <div className="stat-value">{overview.total_ranges.toLocaleString()}</div>
                        <div className="stat-label">Reference Ranges</div>
                    </div>
                </div>
            </div>



            {/* Distribution Charts */}
            <div className="distributions-section">
                <h2 className="section-title">📈 Distributions</h2>

                {/* Test Categories */}
                {distributions.by_category && distributions.by_category.length > 0 && (
                    <div className="distribution-card">
                        <h3>Tests by Category</h3>
                        <div className="bar-chart">
                            {distributions.by_category.map((item, idx) => {
                                const maxCount = Math.max(...distributions.by_category.map(i => i.count));
                                const percentage = (item.count / maxCount) * 100;
                                return (
                                    <div key={idx} className="bar-item">
                                        <div className="bar-label">{item.name}</div>
                                        <div className="bar-container">
                                            <div
                                                className="bar-fill"
                                                style={{ width: `${percentage}%` }}
                                            >
                                                
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Top Panels */}
                {distributions.by_panel && distributions.by_panel.length > 0 && (
                    <div className="distribution-card">
                        <h3>Top Test Panels</h3>
                        <div className="bar-chart">
                            {distributions.by_panel.map((item, idx) => {
                                const maxCount = Math.max(...distributions.by_panel.map(i => i.count));
                                const percentage = (item.count / maxCount) * 100;
                                return (
                                    <div key={idx} className="bar-item">
                                        <div className="bar-label">{item.name}</div>
                                        <div className="bar-container">
                                            <div
                                                className="bar-fill panel"
                                                style={{ width: `${percentage}%` }}
                                            >
                                                
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                )}

                {/* Source Types */}
                {distributions.by_source_type && distributions.by_source_type.length > 0 && (
                    <div className="distribution-card">
                        <h3>Sources by Type</h3>
                        <div className="pie-chart-container">
                            {distributions.by_source_type.map((item, idx) => (
                                <div key={idx} className="pie-item">
                                    <div className="pie-color" style={{ backgroundColor: `hsl(${idx * 60}, 70%, 60%)` }}></div>
                                    <div className="pie-label">{item.name}</div>
                                    <div className="pie-value">{item.count}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Specimen Types */}
                {distributions.by_specimen && distributions.by_specimen.length > 0 && (
                    <div className="distribution-card">
                        <h3>Specimen Types</h3>
                        <div className="pie-chart-container">
                            {distributions.by_specimen.map((item, idx) => (
                                <div key={idx} className="pie-item">
                                    <div className="pie-color" style={{ backgroundColor: `hsl(${idx * 45 + 180}, 70%, 60%)` }}></div>
                                    <div className="pie-label">{item.name}</div>
                                    <div className="pie-value">{item.count}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Sex Distribution */}
                {distributions.by_sex && distributions.by_sex.length > 0 && (
                    <div className="distribution-card">
                        <h3>Reference Ranges by Sex</h3>
                        <div className="pie-chart-container">
                            {distributions.by_sex.map((item, idx) => (
                                <div key={idx} className="pie-item">
                                    <div className="pie-color" style={{ backgroundColor: `hsl(${idx * 120}, 70%, 60%)` }}></div>
                                    <div className="pie-label">{item.name}</div>
                                    <div className="pie-value">{item.count}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* Top Sources Table */}
            <div className="top-sources-section">
                <h2 className="section-title">🏆 Top Reference Sources</h2>
                <div className="sources-table">
                    <div className="table-header">
                        <div className="table-cell">Rank</div>
                        <div className="table-cell">Source Name</div>
                        <div className="table-cell">Type</div>
                        <div className="table-cell">Range Count</div>
                    </div>
                    {top_sources.map((source, idx) => (
                        <div key={idx} className="table-row">
                            <div className="table-cell rank">#{idx + 1}</div>
                            <div className="table-cell source-name">{source.name}</div>
                            <div className="table-cell source-type">{source.type}</div>
                            <div className="table-cell range-count">{source.range_count.toLocaleString()}</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Statistics;

