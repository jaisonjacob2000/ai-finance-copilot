const { useState, useEffect, useRef } = React;

const API_URL = 'http://localhost:8000';

function App() {
    const [activeTab, setActiveTab] = useState('overview');
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [stats, setStats] = useState(null);
    const [categories, setCategories] = useState([]);
    const [insights, setInsights] = useState([]);
    const [nudges, setNudges] = useState([]);
    const chartInstanceRef = useRef(null);

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
        setError(null);
    };

    const uploadFile = async () => {
        if (!file) {
            setError('Please select a CSV file');
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${API_URL}/api/upload`, {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) throw new Error('Upload failed');

            const data = await response.json();
            
            // Fetch all data after upload
            await Promise.all([
                fetchStats(),
                fetchCategories(),
                fetchInsights(),
                fetchNudges()
            ]);

            setFile(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const fetchStats = async () => {
        try {
            const response = await fetch(`${API_URL}/api/stats`);
            const data = await response.json();
            setStats(data);
        } catch (err) {
            console.error('Error fetching stats:', err);
        }
    };

    const fetchCategories = async () => {
        try {
            const response = await fetch(`${API_URL}/api/categories`);
            const data = await response.json();
            console.log('Categories fetched:', data.categories);
            setCategories(data.categories || []);
        } catch (err) {
            console.error('Error fetching categories:', err);
        }
    };

    const fetchInsights = async () => {
        try {
            console.log('Fetching insights...');
            const response = await fetch(`${API_URL}/api/insights`);
            const data = await response.json();
            console.log('Insights received:', data.insights);
            setInsights(data.insights || []);
        } catch (err) {
            console.error('Error fetching insights:', err);
        }
    };

    const fetchNudges = async () => {
        try {
            console.log('Fetching nudges...');
            const response = await fetch(`${API_URL}/api/nudges`);
            const data = await response.json();
            console.log('Nudges received:', data.nudges);
            setNudges(data.nudges || []);
        } catch (err) {
            console.error('Error fetching nudges:', err);
        }
    };

    const updateChart = (categoryData) => {
        console.log('updateChart called with data:', categoryData);
        
        const ctx = document.getElementById('categoryChart');
        if (!ctx) {
            console.error('Canvas element not found!');
            return;
        }
        
        console.log('Canvas found:', ctx);

        // Destroy existing chart
        if (chartInstanceRef.current) {
            console.log('Destroying old chart');
            chartInstanceRef.current.destroy();
        }

        const newChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: categoryData.map(c => c.name),
                datasets: [{
                    data: categoryData.map(c => c.total),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#4facfe',
                        '#43e97b',
                        '#fa709a',
                        '#fee140',
                        '#30cfd0'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            color: '#ffffff',  // White text for legend
                            font: {
                                size: 14
                            },
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const percentage = categoryData[context.dataIndex].percentage;
                                return `${label}: $${value.toFixed(2)} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        chartInstanceRef.current = newChart;
        console.log('Chart created successfully!', newChart);
    };

    // Use useEffect to update chart when categories change
    useEffect(() => {
        if (categories.length > 0) {
            console.log('Categories updated, creating chart...');
            // Small delay to ensure DOM is ready
            setTimeout(() => {
                updateChart(categories);
            }, 100);
        }
        
        // Cleanup: destroy chart when component unmounts
        return () => {
            if (chartInstanceRef.current) {
                console.log('Cleaning up chart on unmount');
                chartInstanceRef.current.destroy();
            }
        };
    }, [categories]);

    // Recreate chart when switching back to Overview tab
    useEffect(() => {
        if (activeTab === 'overview' && categories.length > 0) {
            console.log('Switched to overview, recreating chart...');
            // Small delay to ensure canvas is in DOM
            setTimeout(() => {
                updateChart(categories);
            }, 150);
        }
    }, [activeTab]);

    // Debug: Monitor insights and nudges state
    useEffect(() => {
        console.log('Insights state changed:', insights.length, 'insights');
    }, [insights]);

    useEffect(() => {
        console.log('Nudges state changed:', nudges.length, 'nudges');
    }, [nudges]);

    const OverviewTab = () => (
        <>
            {!stats ? (
                <div className="card">
                    <div className="upload-section" onClick={() => document.getElementById('fileInput').click()}>
                        <h2>📊 Upload Your Transactions</h2>
                        <p style={{ marginBottom: '20px', color: '#666' }}>
                            Upload a CSV file with your transaction data to get started
                        </p>
                        <input
                            id="fileInput"
                            type="file"
                            accept=".csv"
                            onChange={handleFileChange}
                        />
                        {file && <p style={{ marginTop: '16px', color: '#667eea' }}>Selected: {file.name}</p>}
                        <button 
                            className="btn" 
                            onClick={(e) => { e.stopPropagation(); uploadFile(); }}
                            disabled={loading}
                            style={{ marginTop: '16px' }}
                        >
                            {loading ? 'Uploading...' : 'Upload & Analyze'}
                        </button>
                    </div>
                </div>
            ) : (
                <>
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3>Total Transactions</h3>
                            <p>{stats.total_transactions}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Total Spending</h3>
                            <p>${stats.total_spending.toFixed(2)}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Average Transaction</h3>
                            <p>${stats.average_transaction.toFixed(2)}</p>
                        </div>
                        <div className="stat-card">
                            <h3>Highest Transaction</h3>
                            <p>${stats.highest_transaction.toFixed(2)}</p>
                        </div>
                    </div>

                    <div className="card">
                        <h2>💰 Spending by Category</h2>
                        <div className="chart-container">
                            <canvas id="categoryChart"></canvas>
                        </div>
                    </div>

                    <div className="card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <h2>📋 Category Breakdown</h2>
                        </div>
                        {categories.map(cat => (
                            <div key={cat.name} style={{ 
                                display: 'flex', 
                                justifyContent: 'space-between',
                                alignItems: 'center',
                                padding: '12px',
                                background: '#f8f9ff',
                                borderRadius: '8px',
                                marginBottom: '8px'
                            }}>
                                <span style={{ fontWeight: '600' }}>{cat.name}</span>
                                <div style={{ textAlign: 'right' }}>
                                    <span style={{ fontSize: '1.2rem', fontWeight: '700', color: '#667eea' }}>
                                        ${cat.total.toFixed(2)}
                                    </span>
                                    <span style={{ marginLeft: '12px', color: '#666' }}>
                                        {cat.percentage}%
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </>
            )}
        </>
    );

    const InsightsTab = () => (
        <div className="card">
            <h2>🤖 AI-Powered Insights</h2>
            {loading && (
                <div className="loading">Analyzing your spending patterns...</div>
            )}
            {!loading && insights.length === 0 && (
                <p style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                    Upload transactions to see AI-generated insights
                </p>
            )}
            {!loading && insights.length > 0 && (
                <>
                    <p style={{ marginBottom: '20px', color: 'white' }}>
                        Our AI analyzed your spending patterns and found these insights:
                    </p>
                    {insights.map((insight, idx) => (
                        <div key={idx} className="insight-item">
                            <p style={{ fontSize: '1.05rem', color: 'white' }}>{insight}</p>
                        </div>
                    ))}
                </>
            )}
        </div>
    );

    const NudgesTab = () => (
        <div className="card">
            <h2>💡 Behavioral Nudges</h2>
            {loading && (
                <div className="loading">Generating personalized recommendations...</div>
            )}
            {!loading && nudges.length === 0 && (
                <p style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                    Upload transactions to see personalized recommendations
                </p>
            )}
            {!loading && nudges.length > 0 && (
                <>
                    <p style={{ marginBottom: '24px', color: 'white' }}>
                        Actionable recommendations to improve your financial health:
                    </p>
                    {nudges.map((nudge, idx) => (
                        <div key={idx} className="nudge-card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                                <div style={{ flex: 1 }}>
                                    <h3>
                                        {nudge.title}
                                        <span className={`priority-badge priority-${nudge.priority}`}>
                                            {nudge.priority}
                                        </span>
                                    </h3>
                                    <p style={{ color: '#e8e8e8', marginTop: '8px' }}>{nudge.description}</p>
                                    <p className="savings">
                                        💰 Potential savings: ${nudge.potential_savings.toFixed(2)}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))}
                </>
            )}
        </div>
    );

    return (
        <div className="container">
            <div className="header">
                <h1>🤖 AI Personal Finance Copilot</h1>
                <p>Smart insights • Behavioral nudges • Better financial decisions</p>
            </div>

            {error && <div className="error">{error}</div>}

            <div className="card">
                <div className="tabs">
                    <button 
                        className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Overview
                    </button>
                    <button 
                        className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
                        onClick={() => setActiveTab('insights')}
                    >
                        AI Insights
                    </button>
                    <button 
                        className={`tab ${activeTab === 'nudges' ? 'active' : ''}`}
                        onClick={() => setActiveTab('nudges')}
                    >
                        Nudges
                    </button>
                </div>
            </div>

            {activeTab === 'overview' && <OverviewTab />}
            {activeTab === 'insights' && <InsightsTab />}
            {activeTab === 'nudges' && <NudgesTab />}
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));