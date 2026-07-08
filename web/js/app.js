document.addEventListener('DOMContentLoaded', async () => {
    try {
        // Fetch data
        const response = await fetch('/data/dashboard_data.json');
        const data = await response.json();

        // Determine current page
        const path = window.location.pathname;

        if (path.includes('index.html') || path.endsWith('/')) {
            renderTrends(data);
        } else if (path.includes('replenishment.html')) {
            renderReplenishment(data);
        } else if (path.includes('display.html')) {
            renderDisplay(data);
        }

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        document.querySelector('main').innerHTML = `
            <div class="card" style="text-align: center; color: var(--danger-color)">
                <h2>Error Loading Data</h2>
                <p>Please ensure main.py has been run to generate dashboard_data.json and server is running.</p>
            </div>
        `;
    }
});

function getBadgeClass(action) {
    switch (action) {
        case 'URGENT BUY': return 'badge-urgent';
        case 'REPLENISH': return 'badge-replenish';
        case 'PROMOTE': return 'badge-promote';
        case 'NEW PRODUCT OPPORTUNITY': return 'badge-new';
        default: return '';
    }
}

function renderTrends(data) {
    const container = document.getElementById('trends-grid');
    const statsContainer = document.getElementById('stats-row');

    // Render Stats
    const totalTrends = data.trends.length;
    const aiMatches = data.recommendations.filter(r => r.match_confidence >= 80).length;
    const newOpps = data.recommendations.filter(r => r.action === 'NEW PRODUCT OPPORTUNITY').length;

    statsContainer.innerHTML = `
        <div class="stat-card">
            <div class="stat-value">${totalTrends}</div>
            <div class="stat-label">Trends Identified</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${aiMatches}</div>
            <div class="stat-label">High Confidence AI Matches</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">${newOpps}</div>
            <div class="stat-label">New Opportunities</div>
        </div>
    `;

    // Render Trends Cards
    container.innerHTML = data.trends.map((trend, index) => {
        const match = data.recommendations.find(r => r.trend === trend.name);
        const action = match ? match.action : 'ANALYZING';

        return `
        <div class="card">
            <div class="card-header">
                <span class="badge" style="background: rgba(255,255,255,0.1)">#${index + 1}</span>
                ${match ? `<span class="badge ${getBadgeClass(action)}">${action}</span>` : ''}
            </div>
            <h3 class="trend-name">${trend.name}</h3>
            <p style="color: var(--text-secondary); font-size: 0.9rem; margin: 0.5rem 0 1rem 0">
                ${trend.description || 'No description available'}
            </p>
            <ul class="details-list">
                <li>🎨 Colors: ${trend.colors.join(', ')}</li>
                <li>🏷️ Category: ${trend.category}</li>
                ${match ? `
                <li style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.1)">
                    🎯 Best Match: ${match.matched_item.name}
                </li>
                <li>
                    📊 Confidence: ${match.match_confidence.toFixed(1)}%
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${match.match_confidence}%"></div>
                    </div>
                </li>
                ` : ''}
            </ul>
        </div>
        `;
    }).join('');
}

function renderReplenishment(data) {
    console.log("Rendering Replenishment...");
    try {
        const container = document.getElementById('replenishment-list');
        if (!container) {
            console.error("Container 'replenishment-list' not found");
            return;
        }

        // Filter for actionable items
        const actionable = data.recommendations.filter(r =>
            ['URGENT BUY', 'REPLENISH', 'NEW PRODUCT OPPORTUNITY'].includes(r.action)
        ).sort((a, b) => {
            // Sort order: URGENT > NEW > REPLENISH
            const priority = { 'URGENT BUY': 3, 'NEW PRODUCT OPPORTUNITY': 2, 'REPLENISH': 1 };
            return priority[b.action] - priority[a.action];
        });

        console.log(`Found ${actionable.length} actionable items`);

        if (actionable.length === 0) {
            container.innerHTML = `
                <div class="card" style="text-align: center; padding: 3rem;">
                    <h3>✅ All Good!</h3>
                    <p style="color: var(--text-secondary)">No urgent replenishment or new product opportunities found.</p>
                </div>
            `;
            return;
        }

        container.innerHTML = actionable.map(item => {
            const isNew = item.action === 'NEW PRODUCT OPPORTUNITY';

            // Safety check for matched_item
            const matchedItem = item.matched_item || {};
            const imagePath = matchedItem.image_path ? '/' + matchedItem.image_path : null;
            const itemName = matchedItem.name || 'Unknown Item';
            const stockLevel = matchedItem.stock_level !== undefined ? matchedItem.stock_level : 'N/A';

            return `
            <div class="card" style="display: flex; gap: 1.5rem; align-items: center;">
                <div style="flex: 0 0 100px; height: 100px; background: rgba(0,0,0,0.2); border-radius: 0.5rem; overflow: hidden; display: flex; align-items: center; justify-content: center;">
                    ${imagePath && !isNew ?
                    `<img src="${imagePath}" style="width: 100%; height: 100%; object-fit: cover;" onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IiM2NDc0OGIiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIj48cmVjdCB4PSIzIiB5PSIzIiB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHJ4PSIyIiByeT0iMiI+PC9yZWN0PjxjaXJjbGUgY3g9IjguNSIgY3k9IjguNSIgcj0iMS41Ij48L2NpcmNsZT48cG9seWxpbmUgcG9pbnRzPSIyMSAxNSAxNiAxMCA1IDIxIj48L3BvbHlsaW5lPjwvc3ZnPg=='">` :
                    `<span style="font-size: 2rem;">${isNew ? '✨' : '📦'}</span>`
                }
                </div>
                
                <div style="flex: 1;">
                    <div class="card-header" style="margin-bottom: 0.5rem;">
                        <h3 class="trend-name">${item.trend}</h3>
                        <span class="badge ${getBadgeClass(item.action)}">${item.action}</span>
                    </div>
                    
                    <p style="margin: 0; color: var(--text-secondary)">
                        ${item.reason}
                    </p>
                    
                    <div style="margin-top: 0.5rem; font-size: 0.875rem; color: var(--text-primary);">
                        ${isNew ?
                    `<strong>Suggestion:</strong> Source variants in ${item.trend.toLowerCase()} style.` :
                    `<strong>Matched Item:</strong> ${itemName} (Stock: ${stockLevel})`
                }
                    </div>
                </div>
                
                <div style="text-align: right;">
                    <div style="font-weight: 700; font-size: 1.25rem;">
                        ${isNew ? 'New SKU' : (item.action === 'URGENT BUY' ? '+200' : '+50')}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-secondary);">Recommended Order</div>
                </div>
            </div>
            `;
        }).join('');
    } catch (e) {
        console.error("Error in renderReplenishment:", e);
        document.getElementById('replenishment-list').innerHTML = `
            <div class="card" style="color: var(--danger-color)">
                Error rendering list: ${e.message}
            </div>
        `;
    }
}

function renderDisplay(data) {
    const container = document.getElementById('display-grid');

    // Sort by confidence
    const sorted = data.recommendations
        .filter(r => r.action !== 'NEW PRODUCT OPPORTUNITY')
        .sort((a, b) => b.match_confidence - a.match_confidence);

    container.innerHTML = sorted.map(item => {
        const imagePath = item.matched_item.image_path ? '/' + item.matched_item.image_path : null;

        return `
        <div class="card">
            <div style="position: relative;">
                ${imagePath ?
                `<img src="${imagePath}" class="item-image" alt="${item.matched_item.name}">` :
                `<div class="item-image" style="background: #334155; display: flex; align-items: center; justify-content: center; color: #64748b;">No Image</div>`
            }
                <div style="position: absolute; top: 10px; right: 10px;">
                    <span class="badge ${getBadgeClass(item.action)}">${item.action}</span>
                </div>
            </div>
            
            <h3 class="trend-name" style="margin-top: 1rem;">${item.matched_item.name}</h3>
            <p style="color: var(--accent-color); font-size: 0.9rem; font-weight: 500; margin: 0.25rem 0;">
                Trending: ${item.trend}
            </p>
            
            <div style="margin-top: 1rem; background: rgba(0,0,0,0.2); padding: 1rem; border-radius: 0.5rem;">
                <h4 style="margin: 0 0 0.5rem 0; font-size: 0.875rem; color: var(--text-secondary);">MERCHANDISING TIP</h4>
                <p style="margin: 0; font-size: 0.9rem;">
                    Feature prominently. ${item.reason}
                </p>
            </div>
           
            <div style="margin-top: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap;">
                 ${item.detailed_method.includes('CLIP') || item.detailed_method.includes('GEMINI') ?
                `<span class="badge" style="background: rgba(59, 130, 246, 0.2); color: #93c5fd;">🖼️ AI Verified</span>` : ''
            }
                 <span class="badge" style="background: rgba(255, 255, 255, 0.1);">Confidence: ${item.match_confidence.toFixed(0)}%</span>
            </div>
        </div>
        `;
    }).join('');
}
