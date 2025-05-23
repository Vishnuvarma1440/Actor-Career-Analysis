// Global variables
let currentActor = null;
let ratingChart = null;
let boxOfficeChart = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadPopularActors();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    const searchInput = document.getElementById('actorSearch');
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            searchActor();
        }
    });
}

// Load popular actors
async function loadPopularActors() {
    try {
        const response = await fetch('/api/popular-actors');
        const actors = await response.json();
        
        const container = document.getElementById('popularActors');
        
        if (actors.length > 0) {
            container.innerHTML = actors.map(actor => `
                <div class="actor-card" onclick="selectActor('${actor.name}')">
                    <h3>${actor.name}</h3>
                    <p class="popularity">Popularity: ${Math.round(actor.popularity || 0)}</p>
                </div>
            `).join('');
        } else {
            container.innerHTML = '<div class="error">No popular actors found</div>';
        }
    } catch (error) {
        console.error('Error loading popular actors:', error);
        document.getElementById('popularActors').innerHTML = 
            '<div class="error">Error loading popular actors</div>';
    }
}

// Search for actors
async function searchActor() {
    const query = document.getElementById('actorSearch').value.trim();
    if (!query) return;
    
    const resultsContainer = document.getElementById('searchResults');
    resultsContainer.innerHTML = '<div class="loading">Searching...</div>';
    
    try {
        const response = await fetch(`/api/search-actor?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        if (results.error) {
            resultsContainer.innerHTML = `<div class="error">${results.error}</div>`;
            return;
        }
        
        if (results.length > 0) {
            resultsContainer.innerHTML = results.map(actor => `
                <div class="search-result" onclick="selectActor('${actor.name}')">
                    <h4>${actor.name}</h4>
                    <p>ID: ${actor.id}</p>
                </div>
            `).join('');
        } else {
            resultsContainer.innerHTML = '<div class="error">No actors found</div>';
        }
    } catch (error) {
        console.error('Error searching actors:', error);
        resultsContainer.innerHTML = '<div class="error">Search failed</div>';
    }
}

// Select and analyze an actor
async function selectActor(actorName) {
    currentActor = actorName;
    
    // Show loading state
    const detailsSection = document.getElementById('actorDetails');
    detailsSection.style.display = 'block';
    detailsSection.innerHTML = '<div class="loading">Loading actor analysis...</div>';
    
    try {
        const response = await fetch(`/api/actor/${encodeURIComponent(actorName)}`);
        const actorData = await response.json();
        
        if (actorData.error) {
            detailsSection.innerHTML = `<div class="error">${actorData.error}</div>`;
            return;
        }
        
        displayActorDetails(actorData);
        loadChartsData(actorName);
        
    } catch (error) {
        console.error('Error loading actor details:', error);
        detailsSection.innerHTML = '<div class="error">Failed to load actor details</div>';
    }
}

// Display actor details
function displayActorDetails(actorData) {
    const analysis = actorData.analysis || {};
    
    const detailsHTML = `
        <h2>Actor Analysis</h2>
        <div class="actor-info">
            <div class="basic-info">
                <h3 id="actorName">${actorData.name}</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="label">Birth Year:</span>
                        <span id="birthYear">${actorData.birth_year || 'N/A'}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Career Start:</span>
                        <span id="careerStart">${actorData.career_start || 'N/A'}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Total Movies:</span>
                        <span id="totalMovies">${actorData.total_movies || 0}</span>
                    </div>
                    <div class="info-item">
                        <span class="label">Career Score:</span>
                        <span id="careerScore" class="score">${analysis.career_score || 'N/A'}/100</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="analysis-section">
            <div class="analysis-card">
                <h4>Performance Metrics</h4>
                <div class="metrics-grid">
                    <div class="metric">
                        <span class="metric-label">Average Rating</span>
                        <span class="metric-value">${analysis.avg_rating || 'N/A'}/10</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Total Box Office</span>
                        <span class="metric-value">$${analysis.total_box_office || 0}M</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Career Trend</span>
                        <span class="metric-value">${analysis.performance_trend || 'N/A'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Consistency</span>
                        <span class="metric-value">${analysis.consistency || 'N/A'}</span>
                    </div>
                </div>
            </div>

            <div class="analysis-card">
                <h4>AI Recommendations</h4>
                <ul class="recommendations">
                    ${(analysis.recommendations || ['No recommendations available']).map(rec => 
                        `<li>${rec}</li>`
                    ).join('')}
                </ul>
            </div>
        </div>

        <div class="movies-section">
            <h4>Recent Movies</h4>
            <div class="movies-list">
                ${(actorData.movies || []).slice(0, 6).map(movie => `
                    <div class="movie-card">
                        <h5>${movie.title}</h5>
                        <div class="movie-info">
                            <span>Year: ${movie.year || 'N/A'}</span>
                            <span class="movie-rating">Rating: ${movie.rating || 'N/A'}/10</span>
                        </div>
                        <div class="movie-info">
                            <span>Box Office: ${movie.box_office || 0}M</span>
                        </div>
                    </div>
                `).join('') || '<div class="loading">No movie data available</div>'}
            </div>
        </div>

        <div class="charts-section">
            <h4>Career Visualization</h4>
            <div class="charts-container">
                <div class="chart-item">
                    <canvas id="ratingChart"></canvas>
                </div>
                <div class="chart-item">
                    <canvas id="boxOfficeChart"></canvas>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('actorDetails').innerHTML = detailsHTML;
}

// Load and display charts
async function loadChartsData(actorName) {
    try {
        const response = await fetch(`/api/charts-data/${encodeURIComponent(actorName)}`);
        const chartsData = await response.json();
        
        if (chartsData.error) {
            console.error('Charts data error:', chartsData.error);
            return;
        }
        
        // Create rating progression chart
        createRatingChart(chartsData);
        
        // Create box office chart
        createBoxOfficeChart(chartsData);
        
    } catch (error) {
        console.error('Error loading charts data:', error);
    }
}

// Create rating progression chart
function createRatingChart(chartsData) {
    const ctx = document.getElementById('ratingChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (ratingChart) {
        ratingChart.destroy();
    }
    
    // Get progression data for the current actor
    const progressionKey = Object.keys(chartsData).find(key => key.includes('_progression'));
    const progressionData = chartsData[progressionKey] || [];
    
    if (progressionData.length === 0) {
        ctx.getContext('2d').fillText('No rating data available', 10, 50);
        return;
    }
    
    // Sort by year
    const sortedData = progressionData.sort((a, b) => a.year - b.year);
    
    ratingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedData.map(d => d.year),
            datasets: [{
                label: 'Movie Ratings',
                data: sortedData.map(d => d.rating),
                borderColor: 'rgb(102, 126, 234)',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: 'rgb(102, 126, 234)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Rating Progression Over Time'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    min: 0,
                    max: 10,
                    title: {
                        display: true,
                        text: 'Rating (0-10)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Year'
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const dataIndex = context.dataIndex;
                            const movie = sortedData[dataIndex];
                            return `Movie: ${movie.title}`;
                        }
                    }
                }
            }
        }
    });
}

// Create box office chart
function createBoxOfficeChart(chartsData) {
    const ctx = document.getElementById('boxOfficeChart');
    if (!ctx) return;
    
    // Destroy existing chart
    if (boxOfficeChart) {
        boxOfficeChart.destroy();
    }
    
    // Get progression data for the current actor
    const progressionKey = Object.keys(chartsData).find(key => key.includes('_progression'));
    const progressionData = chartsData[progressionKey] || [];
    
    if (progressionData.length === 0) {
        ctx.getContext('2d').fillText('No box office data available', 10, 50);
        return;
    }
    
    // Filter movies with box office data and sort by box office
    const boxOfficeData = progressionData
        .filter(d => d.box_office > 0)
        .sort((a, b) => b.box_office - a.box_office)
        .slice(0, 8); // Top 8 movies
    
    if (boxOfficeData.length === 0) {
        ctx.getContext('2d').fillText('No box office data available', 10, 50);
        return;
    }
    
    boxOfficeChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: boxOfficeData.map(d => d.title.length > 15 ? 
                d.title.substring(0, 15) + '...' : d.title),
            datasets: [{
                label: 'Box Office ($M)',
                data: boxOfficeData.map(d => d.box_office),
                backgroundColor: [
                    'rgba(102, 126, 234, 0.8)',
                    'rgba(118, 75, 162, 0.8)',
                    'rgba(255, 99, 132, 0.8)',
                    'rgba(54, 162, 235, 0.8)',
                    'rgba(255, 205, 86, 0.8)',
                    'rgba(75, 192, 192, 0.8)',
                    'rgba(153, 102, 255, 0.8)',
                    'rgba(255, 159, 64, 0.8)'
                ],
                borderColor: [
                    'rgb(102, 126, 234)',
                    'rgb(118, 75, 162)',
                    'rgb(255, 99, 132)',
                    'rgb(54, 162, 235)',
                    'rgb(255, 205, 86)',
                    'rgb(75, 192, 192)',
                    'rgb(153, 102, 255)',
                    'rgb(255, 159, 64)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Top Movies by Box Office'
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Box Office ($M)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Movies'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        afterLabel: function(context) {
                            const dataIndex = context.dataIndex;
                            const movie = boxOfficeData[dataIndex];
                            return [
                                `Year: ${movie.year}`,
                                `Rating: ${movie.rating}/10`
                            ];
                        }
                    }
                }
            }
        }
    });
}

// Utility functions
function formatCurrency(amount) {
    if (amount >= 1000) {
        return `${(amount / 1000).toFixed(1)}B`;
    } else {
        return `${amount}M`;
    }
}

function getScoreColor(score) {
    if (score >= 80) return '#27ae60';
    if (score >= 60) return '#f39c12';
    if (score >= 40) return '#e67e22';
    return '#e74c3c';
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Handle API errors gracefully
function handleApiError(error, context) {
    console.error(`Error in ${context}:`, error);
    return {
        error: `Failed to load ${context}. Please try again.`
    };
}