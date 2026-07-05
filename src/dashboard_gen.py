import json

def generate_interactive_dashboard(properties_data, output_path):
    """Generate a highly premium, fully interactive HTML Dashboard with embedded JSON properties database."""
    
    properties_js = json.dumps(properties_data, indent=4)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whitfield St London Live Room & Commute Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0d0f14;
            --card-bg: rgba(22, 28, 38, 0.7);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-color: #6366f1;
            --accent-glow: rgba(99, 102, 241, 0.15);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }}
        
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 10% 20%, rgba(99, 102, 241, 0.05) 0px, transparent 50%),
                radial-gradient(at 90% 80%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
            color: var(--text-main);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 2rem 1.5rem;
            line-height: 1.5;
        }}
        
        h1, h2, h3 {{
            font-family: 'Outfit', sans-serif;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        
        header {{
            text-align: center;
            margin-bottom: 2.5rem;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a5b4fc, #6366f1, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            color: var(--text-muted);
            font-size: 1.1rem;
            max-width: 700px;
            margin: 0 auto 1.5rem auto;
        }}
        
        /* Stats Panel */
        .summary-stats {{
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-bottom: 2.5rem;
            flex-wrap: wrap;
        }}
        
        .stat-item {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 0.75rem 1.5rem;
            text-align: center;
            min-width: 180px;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }}
        
        .stat-val {{
            display: block;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--success);
            font-family: 'Outfit', sans-serif;
        }}
        
        .stat-lbl {{
            font-size: 0.8rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        /* Dynamic Filter Panel */
        .filter-panel {{
            background: rgba(22, 28, 38, 0.9);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 2.5rem;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        
        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 1.5rem;
            align-items: end;
        }}
        
        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }}
        
        .filter-label {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-main);
            display: flex;
            justify-content: space-between;
        }}
        
        .filter-value-display {{
            color: var(--accent-color);
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }}
        
        select, input[type="range"] {{
            width: 100%;
            background: #1f2937;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            color: var(--text-main);
            padding: 0.6rem;
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s ease;
        }}
        
        select:focus {{
            border-color: var(--accent-color);
        }}
        
        input[type="range"] {{
            -webkit-appearance: none;
            height: 6px;
            background: #4b5563;
            border-radius: 9999px;
            padding: 0;
            cursor: pointer;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            background: var(--accent-color);
            box-shadow: 0 0 10px var(--accent-color);
            transition: transform 0.1s ease;
        }}
        
        input[type="range"]::-webkit-slider-thumb:hover {{
            transform: scale(1.2);
        }}
        
        /* Checkbox Styling */
        .checkbox-container {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--text-main);
            user-select: none;
            margin-bottom: 0.5rem;
        }}
        
        .checkbox-container input {{
            width: 18px;
            height: 18px;
            cursor: pointer;
            accent-color: var(--accent-color);
        }}
        
        /* Apply Button Styling */
        .apply-btn {{
            width: 100%;
            padding: 0.7rem 1.5rem;
            font-size: 0.95rem;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent-color), var(--success));
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
            text-align: center;
        }}
        
        .apply-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(99, 102, 241, 0.4);
        }}
        
        .apply-btn:active {{
            transform: translateY(0);
        }}
        
        /* Grid and Cards */
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 2rem;
            transition: all 0.3s ease;
        }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 24px var(--accent-glow);
            border-color: rgba(99, 102, 241, 0.3);
        }}
        
        .card-header {{
            padding: 1.25rem 1.5rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .rent-price {{
            font-size: 1.6rem;
            font-weight: 700;
            color: #fff;
            font-family: 'Outfit', sans-serif;
        }}
        
        .rent-price small {{
            font-size: 0.85rem;
            color: var(--text-muted);
            font-weight: 400;
        }}
        
        .platform-badge {{
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .platform-badge.openrent {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}
        
        .platform-badge.rightmove {{
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }}
        
        .platform-badge.onthemarket {{
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}
        
        .platform-badge.zoopla {{
            background: rgba(139, 92, 246, 0.15);
            color: #a78bfa;
            border: 1px solid rgba(139, 92, 246, 0.3);
        }}
        
        .card-body {{
            padding: 1.25rem 1.5rem;
            flex-grow: 1;
        }}
        
        .address {{
            font-size: 0.9rem;
            color: var(--text-main);
            font-weight: 600;
            margin-bottom: 1rem;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.65rem;
        }}
        
        .metric-label {{
            color: var(--text-muted);
            font-size: 0.85rem;
        }}
        
        .metric-value {{
            font-weight: 600;
            font-size: 1rem;
        }}
        
        .commute-fast {{
            color: var(--success);
        }}
        
        .commute-med {{
            color: var(--warning);
        }}
        
        .commute-slow {{
            color: #f97316;
        }}
        
        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.4rem;
            margin-top: 1rem;
            margin-bottom: 0.75rem;
        }}
        
        .badge {{
            font-size: 0.7rem;
            font-weight: 600;
            padding: 0.2rem 0.4rem;
            border-radius: 6px;
        }}
        
        .badge.bills {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
        }}
        
        .badge.no-bills {{
            background: rgba(239, 68, 68, 0.1);
            color: #f87171;
        }}
        
        .badge.furnished {{
            background: rgba(99, 102, 241, 0.15);
            color: #a5b4fc;
        }}
        
        .badge.unfurnished {{
            background: rgba(156, 163, 175, 0.15);
            color: var(--text-muted);
        }}
        
        .badge.studio {{
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
        }}
        
        .badge.onebed {{
            background: rgba(59, 130, 246, 0.15);
            color: #60a5fa;
        }}
        
        .badge.ensuite {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px dashed rgba(16, 185, 129, 0.5);
        }}
        
        .listing-age {{
            font-size: 0.75rem;
            color: var(--text-muted);
            margin-top: 0.75rem;
            border-top: 1px dashed var(--card-border);
            padding-top: 0.65rem;
        }}
        
        .card-footer {{
            padding: 1rem 1.5rem;
            background: rgba(255, 255, 255, 0.02);
            border-top: 1px solid var(--card-border);
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
        }}
        
        .btn-primary, .btn-secondary {{
            display: inline-flex;
            justify-content: center;
            align-items: center;
            padding: 0.5rem 0.75rem;
            border-radius: 8px;
            font-size: 0.8rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .btn-primary {{
            background: var(--accent-color);
            color: white;
            border: none;
        }}
        
        .btn-primary:hover {{
            background: #4f46e5;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}
        
        .btn-secondary {{
            background: transparent;
            color: var(--text-main);
            border: 1px solid var(--card-border);
        }}
        
        .btn-secondary:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: var(--text-muted);
        }}
        
        .no-results {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
        }}
        
        .no-results h2 {{
            margin-bottom: 0.5rem;
            color: var(--text-muted);
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
            .filter-panel {{
                padding: 1rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Whitfield St Room & Commute Dashboard</h1>
            <p>Live matching properties from Rightmove, OpenRent, OnTheMarket, and Zoopla. Travel times and route mappings are pre-calculated to Whitfield St postcode W1T 4EU using live TfL Unified transit data.</p>
            
            <div class="summary-stats">
                <div class="stat-item">
                    <span class="stat-val" id="stat-matches">0</span>
                    <span class="stat-lbl">Matches Filtered</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val" id="stat-min-rent">£0</span>
                    <span class="stat-lbl">Min Rent</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val" id="stat-avg-commute">0 mins</span>
                    <span class="stat-lbl">Avg Commute</span>
                </div>
            </div>
        </header>
        
        <!-- Dynamic Filter Control Panel -->
        <div class="filter-panel">
            <div class="filter-grid">
                <div class="filter-group">
                    <div class="filter-label">
                        <span>Max Monthly Rent</span>
                        <span class="filter-value-display" id="rent-val">£1,400</span>
                    </div>
                    <input type="range" id="filter-rent" min="400" max="2000" step="50" value="1400">
                </div>
                
                <div class="filter-group">
                    <div class="filter-label">
                        <span>Max Commute to Whitfield St</span>
                        <span class="filter-value-display" id="commute-val">40 mins</span>
                    </div>
                    <input type="range" id="filter-commute" min="10" max="60" step="5" value="40">
                </div>
                
                <div class="filter-group">
                    <div class="filter-label">
                        <span>Max Station Walk Proximity</span>
                        <span class="filter-value-display" id="walk-val">5 mins</span>
                    </div>
                    <input type="range" id="filter-walk" min="1" max="20" step="1" value="5">
                </div>
                
                <div class="filter-group">
                    <div class="filter-label">Property Type</div>
                    <select id="filter-type">
                        <option value="all">All Properties</option>
                        <option value="Studio">Studio Only</option>
                        <option value="1 Bed Flat">1 Bedroom Flat Only</option>
                        <option value="Ensuite Room">Ensuite Room Only</option>
                        <option value="Double Room">Double Room Only</option>
                        <option value="Single Room">Single Room Only</option>
                        <option value="Room">Room (Shared) Only</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <div class="filter-label">Platform Source</div>
                    <select id="filter-source">
                        <option value="all">All Platforms</option>
                        <option value="OpenRent">OpenRent</option>
                        <option value="Rightmove">Rightmove</option>
                        <option value="OnTheMarket">OnTheMarket</option>
                        <option value="Zoopla">Zoopla</option>
                    </select>
                </div>
                
                <div class="filter-group">
                    <label class="checkbox-container">
                        <input type="checkbox" id="filter-walkonly">
                        <span>Only show direct walking (<20 min walk to Whitfield St)</span>
                    </label>
                </div>
                
                <div class="filter-group">
                    <button id="btn-apply" class="apply-btn">⚡ Apply Filters</button>
                </div>
            </div>
        </div>
        
        <div class="grid" id="properties-grid">
            <!-- Dynamic JavaScript card rendering -->
        </div>
    </div>

    <script>
        // Directly embedding property database to solve local file CORS issue!
        const properties = {properties_js};

        // Filter elements
        const rentSlider = document.getElementById('filter-rent');
        const rentDisplay = document.getElementById('rent-val');
        const commuteSlider = document.getElementById('filter-commute');
        const commuteDisplay = document.getElementById('commute-val');
        const walkSlider = document.getElementById('filter-walk');
        const walkDisplay = document.getElementById('walk-val');
        const typeSelect = document.getElementById('filter-type');
        const sourceSelect = document.getElementById('filter-source');
        const walkonlyCheck = document.getElementById('filter-walkonly');
        const applyBtn = document.getElementById('btn-apply');
        
        const grid = document.getElementById('properties-grid');
        
        // Stats elements
        const statMatches = document.getElementById('stat-matches');
        const statMinRent = document.getElementById('stat-min-rent');
        const statAvgCommute = document.getElementById('stat-avg-commute');

        // Apply filters dynamically
        function applyFilters() {{
            const maxRent = parseInt(rentSlider.value);
            const maxCommute = parseInt(commuteSlider.value);
            const maxWalk = parseInt(walkSlider.value);
            const selectedType = typeSelect.value;
            const selectedSource = sourceSelect.value;
            const walkOnly = walkonlyCheck.checked;

            // Update range text displays
            rentDisplay.textContent = '£' + maxRent.toLocaleString();
            commuteDisplay.textContent = maxCommute + ' mins';
            walkDisplay.textContent = maxWalk + ' mins';

            // Filtering logic
            const filtered = properties.filter(p => {{
                // Price Filter
                if (p.price > maxRent) return false;
                
                // Walk-only Filter (Direct walk to Whitfield StNW12PG must be under 20 mins)
                if (walkOnly) {{
                    if (p.is_walk_only && p.commute_time !== null && p.commute_time <= 20) {{
                        // Pass walk-only checks
                    }} else if (p.distance_km <= 1.4) {{
                        // estimated walking time under 20 mins
                    }} else {{
                        return false;
                    }}
                }}
                
                // Commute Filter (only filter if TfL commute time was successfully calculated)
                if (!walkOnly && p.commute_time !== null && p.commute_time > maxCommute) return false;
                
                // Station Walk Proximity Filter (first walking leg duration)
                if (p.station_walk_time !== null && p.station_walk_time > maxWalk) return false;

                // Property Type Filter
                if (selectedType !== 'all' && p.property_type !== selectedType) return false;

                // Source Filter
                if (selectedSource !== 'all') {{
                    let hasSource = false;
                    if (p.sources && p.sources.length > 0) {{
                        hasSource = p.sources.some(s => s.source === selectedSource);
                    }} else {{
                        hasSource = (p.source === selectedSource);
                    }}
                    if (!hasSource) return false;
                }}

                return true;
            }});

            // Render filtered cards
            renderCards(filtered);
            updateStats(filtered);
        }}

        // Render card layouts
        function renderCards(list) {{
            grid.innerHTML = '';
            
            if (list.length === 0) {{
                grid.innerHTML = `
                    <div class="no-results">
                        <h2>No properties matched your filters</h2>
                        <p>Relax your rent budget or transit commute times to discover properties.</p>
                    </div>
                `;
                return;
            }}

            list.forEach(p => {{
                const card = document.createElement('div');
                card.className = 'card';
                
                const commuteCls = p.commute_time !== null 
                    ? (p.commute_time <= 20 ? 'commute-fast' : p.commute_time <= 30 ? 'commute-med' : 'commute-slow')
                    : 'text-muted';
                
                let commuteText = 'Unknown';
                if (p.commute_time !== null) {{
                    if (p.is_walk_only) {{
                        commuteText = `🏃 ${{p.commute_time}} mins walk`;
                    }} else {{
                        commuteText = `🚇 ${{p.commute_time}} mins transit`;
                    }}
                }} else {{
                    commuteText = `${{p.distance_km.toFixed(2)}} km (Est. ${{Math.round(p.distance_km * 12.5)}} mins walk)`;
                }}
                
                const proximityText = p.station_walk_time !== null 
                    ? `${{p.station_walk_time}} mins walk`
                    : (p.is_walk_only ? 'Direct walk' : 'Unknown');
                
                const billsBadge = p.bills_included 
                    ? '<span class="badge bills">Bills Included</span>' 
                    : '<span class="badge no-bills">Bills Excluded</span>';
                    
                const furnishedBadge = p.furnished !== 'Unknown' 
                    ? `<span class="badge furnished">${{p.furnished}}</span>`
                    : '<span class="badge unfurnished">Furnished Unknown</span>';
                    
                let typeBadge = '';
                if (p.property_type === 'Studio') {{
                    typeBadge = '<span class="badge studio">Studio</span>';
                }} else if (p.property_type === '1 Bed Flat') {{
                    typeBadge = '<span class="badge onebed">1 Bed Flat</span>';
                }} else if (p.property_type === 'Ensuite Room') {{
                    typeBadge = '<span class="badge ensuite">Ensuite Room</span>';
                }} else if (p.property_type === 'Double Room') {{
                    typeBadge = '<span class="badge ensuite">Double Room</span>';
                }} else if (p.property_type === 'Single Room') {{
                    typeBadge = '<span class="badge ensuite">Single Room</span>';
                }} else {{
                    typeBadge = `<span class="badge ensuite">${{p.property_type || 'Room'}}</span>`;
                }}

                const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${{p.lat}},${{p.lng}}&destination=51.5262,-0.1368&travelmode=transit`;
                let badgesHtml = '';
                let footerButtonsHtml = '';
                if (p.sources && p.sources.length > 0) {{
                    p.sources.forEach((src, idx) => {{
                        const srcClass = src.source.toLowerCase();
                        badgesHtml += `<span class="platform-badge ${{srcClass}}">${{src.source}}</span> `;
                        const btnCls = idx === 0 ? 'btn-primary' : 'btn-secondary';
                        footerButtonsHtml += `<a href="${{src.url}}" target="_blank" class="${{btnCls}}">View ${{src.source}}</a> `;
                    }});
                }} else {{
                    const platformBadgeCls = p.source.toLowerCase();
                    badgesHtml = `<span class="platform-badge ${{platformBadgeCls}}">${{p.source}}</span>`;
                    footerButtonsHtml = `<a href="${{p.url}}" target="_blank" class="btn-primary">View Listing</a>`;
                }}

                card.innerHTML = `
                    <div class="card-header">
                        <span class="rent-price">£${{p.price.toLocaleString()}} <small>/month</small></span>
                        ${{badgesHtml}}
                    </div>
                    <div class="card-body">
                        <div class="address" title="${{p.address}}">📍 ${{p.address}}</div>
                        <div class="metric">
                            <span class="metric-label">Whitfield St Commute:</span>
                            <span class="metric-value ${{commuteCls}}">${{commuteText}}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Walk to Station:</span>
                            <span class="metric-value">${{proximityText}}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Direct Distance:</span>
                            <span class="metric-value">${{p.distance_km.toFixed(2)}} km</span>
                        </div>
                        <div class="badges">
                            ${{typeBadge}}
                            ${{billsBadge}}
                            ${{furnishedBadge}}
                        </div>
                        <div class="listing-age">🕒 ${{p.listing_age}}</div>
                    </div>
                    <div class="card-footer">
                        ${{footerButtonsHtml}}
                        <a href="${{mapsUrl}}" target="_blank" class="btn-secondary">🗺️ Route Map</a>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        // Update stats summary panel
        function updateStats(list) {{
            statMatches.textContent = list.length;
            
            if (list.length === 0) {{
                statMinRent.textContent = '£0';
                statAvgCommute.textContent = '0 mins';
                return;
            }}

            const rents = list.map(p => p.price);
            const minRent = Math.min(...rents);
            statMinRent.textContent = '£' + minRent.toLocaleString();

            const validCommutes = list.filter(p => p.commute_time !== null).map(p => p.commute_time);
            if (validCommutes.length > 0) {{
                const avg = Math.round(validCommutes.reduce((a, b) => a + b, 0) / validCommutes.length);
                statAvgCommute.textContent = avg + ' mins';
            }} else {{
                statAvgCommute.textContent = 'N/A';
            }}
        }}

        // Sliders only update text displays dynamically for lightning-fast performance
        rentSlider.addEventListener('input', () => {{
            rentDisplay.textContent = '£' + parseInt(rentSlider.value).toLocaleString();
        }});
        commuteSlider.addEventListener('input', () => {{
            commuteDisplay.textContent = commuteSlider.value + ' mins';
        }});
        walkSlider.addEventListener('input', () => {{
            walkDisplay.textContent = walkSlider.value + ' mins';
        }});

        // Dynamic filtering is only triggered on click or on load
        applyBtn.addEventListener('click', applyFilters);

        // Run on page load
        window.addEventListener('DOMContentLoaded', applyFilters);
    </script>
</body>
</html>
"""

    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"🔥 Dashboard generated successfully at: {output_path}")
