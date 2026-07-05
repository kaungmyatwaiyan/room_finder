import json


def generate_interactive_dashboard(properties_data, output_path):
    """Generate a highly premium, fully interactive HTML dashboard."""

    properties_js = json.dumps(properties_data, indent=4)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Whitfield St London Room &amp; Commute Finder</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg:          #0d0f14;
            --card-bg:     rgba(22, 28, 38, 0.75);
            --card-border: rgba(255,255,255,0.08);
            --accent:      #6366f1;
            --accent-glow: rgba(99,102,241,0.15);
            --success:     #10b981;
            --warning:     #f59e0b;
            --danger:      #ef4444;
            --text:        #f3f4f6;
            --muted:       #9ca3af;
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            background: var(--bg);
            background-image:
                radial-gradient(at 10% 20%, rgba(99,102,241,0.06) 0, transparent 50%),
                radial-gradient(at 90% 80%, rgba(16,185,129,0.06) 0, transparent 50%);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 0 1.5rem 3rem;
            line-height: 1.5;
        }}

        h1, h2, h3 {{ font-family: 'Outfit', sans-serif; }}

        .container {{ max-width: 1280px; margin: 0 auto; }}

        /* ── Header ─────────────────────────────────────────── */
        header {{
            text-align: center;
            padding: 2.5rem 0 2rem;
        }}

        header h1 {{
            font-size: 2.4rem;
            font-weight: 700;
            background: linear-gradient(135deg, #a5b4fc, #6366f1, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }}

        header p {{
            color: var(--muted);
            font-size: 1rem;
            max-width: 680px;
            margin: 0 auto 1.5rem;
        }}

        /* ── Summary stats ───────────────────────────────────── */
        .summary-stats {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            flex-wrap: wrap;
            margin-bottom: 0;
        }}

        .stat-item {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 0.65rem 1.4rem;
            text-align: center;
            min-width: 160px;
            backdrop-filter: blur(8px);
        }}

        .stat-val {{
            display: block;
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--success);
            font-family: 'Outfit', sans-serif;
        }}

        .stat-lbl {{
            font-size: 0.75rem;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        /* ── Sticky filter panel ─────────────────────────────── */
        .filter-panel {{
            position: sticky;
            top: 0;
            z-index: 200;
            background: rgba(13,15,20,0.97);
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 0 0 16px 16px;
            padding: 1.25rem 1.75rem;
            margin: 1.5rem 0 0;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            transition: box-shadow 0.2s;
        }}

        .filter-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 1rem 1.5rem;
            align-items: end;
        }}

        .filter-group {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}

        .filter-label {{
            font-size: 0.8rem;
            font-weight: 600;
            color: var(--text);
            display: flex;
            justify-content: space-between;
        }}

        .filter-label sub {{
            font-size: 0.7rem;
            color: var(--muted);
            font-weight: 400;
            vertical-align: middle;
        }}

        .filter-value-display {{
            color: var(--accent);
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
        }}

        select, input[type="range"] {{
            width: 100%;
            background: #1f2937;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            color: var(--text);
            padding: 0.5rem 0.65rem;
            font-size: 0.85rem;
            outline: none;
            transition: border-color 0.2s;
        }}

        select:focus {{ border-color: var(--accent); }}

        input[type="range"] {{
            -webkit-appearance: none;
            height: 5px;
            background: #374151;
            border-radius: 9999px;
            padding: 0;
            cursor: pointer;
        }}

        input[type="range"]::-webkit-slider-thumb {{
            -webkit-appearance: none;
            width: 16px; height: 16px;
            border-radius: 50%;
            background: var(--accent);
            box-shadow: 0 0 8px var(--accent);
            transition: transform 0.1s;
        }}

        input[type="range"]::-webkit-slider-thumb:hover {{ transform: scale(1.25); }}

        .checkbox-container {{
            display: flex;
            align-items: center;
            gap: 0.6rem;
            cursor: pointer;
            font-size: 0.82rem;
            font-weight: 600;
            color: var(--text);
            user-select: none;
        }}

        .checkbox-container input {{
            width: 16px; height: 16px;
            cursor: pointer;
            accent-color: var(--accent);
        }}

        /* ── Results bar (bottom of filter panel) ────────────── */
        .results-bar {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding-top: 0.9rem;
            margin-top: 0.9rem;
            border-top: 1px solid var(--card-border);
            flex-wrap: wrap;
        }}

        .result-count {{
            font-size: 0.85rem;
            color: var(--muted);
            flex: 1;
        }}

        .result-count strong {{ color: var(--text); font-size: 1rem; }}

        .sort-group {{
            display: flex;
            align-items: center;
            gap: 0.4rem;
            font-size: 0.8rem;
            color: var(--muted);
        }}

        .sort-select {{
            background: #1a2030;
            border: 1px solid var(--card-border);
            color: var(--text);
            padding: 0.35rem 0.65rem;
            border-radius: 8px;
            font-size: 0.8rem;
            cursor: pointer;
            width: auto;
        }}

        .view-toggle {{
            display: flex;
            gap: 2px;
            background: rgba(255,255,255,0.06);
            border-radius: 8px;
            padding: 3px;
        }}

        .view-btn {{
            background: none;
            border: none;
            color: var(--muted);
            padding: 0.25rem 0.6rem;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.78rem;
            font-weight: 600;
            transition: all 0.15s;
        }}

        .view-btn.active {{
            background: var(--accent);
            color: #fff;
        }}

        .btn-row {{
            display: flex;
            gap: 0.5rem;
        }}

        .apply-btn {{
            padding: 0.4rem 1rem;
            font-size: 0.82rem;
            font-family: 'Outfit', sans-serif;
            font-weight: 700;
            background: linear-gradient(135deg, var(--accent), var(--success));
            color: #fff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .apply-btn:hover {{ transform: translateY(-1px); box-shadow: 0 4px 12px rgba(99,102,241,0.4); }}

        .reset-btn {{
            padding: 0.4rem 0.75rem;
            font-size: 0.78rem;
            background: transparent;
            border: 1px solid rgba(255,255,255,0.1);
            color: var(--muted);
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .reset-btn:hover {{ border-color: var(--muted); color: var(--text); }}

        /* ── Grid / List containers ──────────────────────────── */
        #properties-grid {{
            margin-top: 1.5rem;
        }}

        #properties-grid.view-mode-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
            gap: 1.5rem;
        }}

        #properties-grid.view-mode-list {{
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }}

        /* ── Cards (grid view) ───────────────────────────────── */
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            position: relative;
        }}

        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 12px 24px var(--accent-glow);
            border-color: rgba(99,102,241,0.3);
        }}

        .card.card--viewed {{
            opacity: 0.48;
        }}

        .card.card--viewed .rent-price {{ color: var(--muted); }}

        .viewed-tag {{
            position: absolute;
            top: 8px;
            right: 8px;
            font-size: 0.6rem;
            color: var(--muted);
            background: rgba(0,0,0,0.4);
            padding: 2px 6px;
            border-radius: 4px;
            pointer-events: none;
        }}

        .card-header {{
            padding: 1.1rem 1.4rem 0.9rem;
            border-bottom: 1px solid var(--card-border);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 0.5rem;
        }}

        .price-block {{ display: flex; flex-direction: column; gap: 2px; }}

        .rent-price {{
            font-size: 1.55rem;
            font-weight: 700;
            color: #fff;
            font-family: 'Outfit', sans-serif;
            line-height: 1.1;
        }}

        .rent-price small {{ font-size: 0.8rem; color: var(--muted); font-weight: 400; }}

        .all-in-note {{
            font-size: 0.72rem;
            font-weight: 500;
        }}

        .all-in-note.included {{ color: var(--success); }}
        .all-in-note.estimated {{ color: var(--warning); }}

        .header-right {{
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 0.35rem;
        }}

        /* ── Pills ───────────────────────────────────────────── */
        .pill-new {{
            display: inline-block;
            background: var(--success);
            color: #fff;
            font-size: 0.6rem;
            font-weight: 800;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            letter-spacing: 0.08em;
            animation: pulse-pill 2s ease-in-out infinite;
        }}

        .pill-reduced {{
            display: inline-block;
            background: var(--warning);
            color: #fff;
            font-size: 0.6rem;
            font-weight: 800;
            padding: 0.15rem 0.45rem;
            border-radius: 4px;
            letter-spacing: 0.08em;
        }}

        @keyframes pulse-pill {{
            0%, 100% {{ opacity: 1; }}
            50%       {{ opacity: 0.65; }}
        }}

        /* ── Platform badges ─────────────────────────────────── */
        .platform-badge {{
            padding: 0.2rem 0.55rem;
            border-radius: 9999px;
            font-size: 0.68rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .platform-badge.openrent    {{ background:rgba(16,185,129,0.15); color:#34d399; border:1px solid rgba(16,185,129,0.3); }}
        .platform-badge.rightmove   {{ background:rgba(99,102,241,0.15); color:#a5b4fc; border:1px solid rgba(99,102,241,0.3); }}
        .platform-badge.onthemarket {{ background:rgba(239,68,68,0.15);  color:#f87171; border:1px solid rgba(239,68,68,0.3); }}
        .platform-badge.zoopla      {{ background:rgba(139,92,246,0.15); color:#a78bfa; border:1px solid rgba(139,92,246,0.3); }}

        /* ── Card body ───────────────────────────────────────── */
        .card-body {{
            padding: 1rem 1.4rem;
            flex-grow: 1;
        }}

        .address {{
            font-size: 0.88rem;
            color: var(--text);
            font-weight: 600;
            margin-bottom: 0.85rem;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}

        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.55rem;
        }}

        .metric-label {{ color: var(--muted); font-size: 0.82rem; }}
        .metric-value {{ font-weight: 600; font-size: 0.95rem; }}

        .commute-fast  {{ color: var(--success); }}
        .commute-med   {{ color: var(--warning); }}
        .commute-slow  {{ color: #f97316; }}
        .commute-none  {{ color: var(--muted); font-size: 0.82rem; font-style: italic; }}

        .badges {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.35rem;
            margin-top: 0.85rem 0 0.65rem;
        }}

        .badge {{
            font-size: 0.68rem;
            font-weight: 600;
            padding: 0.18rem 0.4rem;
            border-radius: 5px;
        }}

        .badge.bills      {{ background:rgba(16,185,129,0.15); color:#34d399; }}
        .badge.no-bills   {{ background:rgba(239,68,68,0.1);  color:#f87171; }}
        .badge.furnished  {{ background:rgba(99,102,241,0.15); color:#a5b4fc; }}
        .badge.unfurnished{{ background:rgba(156,163,175,0.12); color:var(--muted); }}
        .badge.studio     {{ background:rgba(245,158,11,0.15); color:#fbbf24; }}
        .badge.onebed     {{ background:rgba(59,130,246,0.15); color:#60a5fa; }}
        .badge.ensuite    {{ background:rgba(16,185,129,0.12); color:#34d399; border:1px dashed rgba(16,185,129,0.4); }}

        .listing-age {{
            font-size: 0.72rem;
            color: var(--muted);
            margin-top: 0.7rem;
            border-top: 1px dashed var(--card-border);
            padding-top: 0.55rem;
        }}

        /* ── Card footer ─────────────────────────────────────── */
        .card-footer {{
            padding: 0.85rem 1.4rem;
            background: rgba(255,255,255,0.02);
            border-top: 1px solid var(--card-border);
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .btn-primary, .btn-secondary {{
            display: inline-flex;
            justify-content: center;
            align-items: center;
            padding: 0.45rem 0.75rem;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s;
            flex: 1;
        }}

        .btn-primary  {{ background: var(--accent); color: #fff; border: none; }}
        .btn-primary:hover {{ background: #4f46e5; box-shadow: 0 4px 12px rgba(99,102,241,0.3); }}
        .btn-secondary {{ background: transparent; color: var(--text); border: 1px solid var(--card-border); }}
        .btn-secondary:hover {{ background: rgba(255,255,255,0.05); border-color: var(--muted); }}

        /* ── List view rows ──────────────────────────────────── */
        .list-row {{
            display: flex;
            align-items: center;
            gap: 0.65rem;
            padding: 0.6rem 1rem;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 10px;
            transition: all 0.2s;
            position: relative;
            min-width: 0;
        }}

        .list-row:hover {{
            border-color: rgba(99,102,241,0.3);
            background: rgba(99,102,241,0.03);
        }}

        .list-row.card--viewed {{ opacity: 0.45; }}

        .list-pills {{
            display: flex;
            flex-direction: column;
            gap: 3px;
            min-width: 70px;
            flex-shrink: 0;
        }}

        .list-type {{
            font-size: 0.68rem;
        }}

        .list-address {{
            flex: 1;
            font-size: 0.83rem;
            font-weight: 500;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
            min-width: 0;
            color: var(--text);
        }}

        .list-price-block {{
            flex-shrink: 0;
            min-width: 105px;
            text-align: right;
        }}

        .list-price {{
            font-size: 0.92rem;
            font-weight: 700;
            color: #fff;
        }}

        .list-allin {{
            font-size: 0.68rem;
            color: var(--warning);
        }}

        .list-allin.included {{ color: var(--success); }}

        .list-commute {{
            min-width: 80px;
            text-align: center;
            font-size: 0.8rem;
            font-weight: 600;
            flex-shrink: 0;
        }}

        .list-walk {{
            min-width: 68px;
            text-align: center;
            font-size: 0.75rem;
            color: var(--muted);
            flex-shrink: 0;
        }}

        .list-platform {{
            flex-shrink: 0;
        }}

        .list-actions {{
            display: flex;
            gap: 0.3rem;
            flex-shrink: 0;
        }}

        .list-actions .btn-primary,
        .list-actions .btn-secondary {{
            padding: 0.28rem 0.55rem;
            font-size: 0.72rem;
            flex: none;
        }}

        .list-viewed-tag {{
            font-size: 0.58rem;
            color: var(--muted);
            white-space: nowrap;
        }}

        /* ── No results ──────────────────────────────────────── */
        .no-results {{
            grid-column: 1 / -1;
            text-align: center;
            padding: 4rem 2rem;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 16px;
        }}

        .no-results h2 {{ margin-bottom: 0.5rem; color: var(--muted); }}

        /* ── Responsive ──────────────────────────────────────── */
        @media (max-width: 768px) {{
            #properties-grid.view-mode-grid {{ grid-template-columns: 1fr; }}
            .filter-panel {{ padding: 1rem; border-radius: 0 0 12px 12px; }}
            .list-walk, .list-allin, .list-platform {{ display: none; }}
            header h1 {{ font-size: 1.8rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">

        <header>
            <h1>Whitfield St Room &amp; Commute Finder</h1>
            <p>Live listings from Rightmove, OpenRent, OnTheMarket and Zoopla.
               Commute times pre-calculated to 60 Whitfield St W1T&nbsp;4EU via live TfL data.</p>
            <div class="summary-stats">
                <div class="stat-item">
                    <span class="stat-val" id="stat-matches">0</span>
                    <span class="stat-lbl">Showing</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val" id="stat-min-rent">£0</span>
                    <span class="stat-lbl">Min Rent</span>
                </div>
                <div class="stat-item">
                    <span class="stat-val" id="stat-avg-commute">— mins</span>
                    <span class="stat-lbl">Avg Commute</span>
                </div>
            </div>
        </header>

        <!-- Sticky filter panel -->
        <div class="filter-panel" id="filter-panel">
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
                        <span>Max Total Commute</span>
                        <span class="filter-value-display" id="commute-val">40 mins</span>
                    </div>
                    <input type="range" id="filter-commute" min="10" max="60" step="5" value="40">
                </div>

                <div class="filter-group">
                    <div class="filter-label">
                        <span>Max Walk to Station <sub>(first leg)</sub></span>
                        <span class="filter-value-display" id="walk-val">10 mins</span>
                    </div>
                    <input type="range" id="filter-walk" min="1" max="25" step="1" value="10">
                </div>

                <div class="filter-group">
                    <div class="filter-label">Property Type</div>
                    <select id="filter-type">
                        <option value="all"         data-base="All Properties">All Properties</option>
                        <option value="Studio"       data-base="Studio">Studio</option>
                        <option value="1 Bed Flat"   data-base="1 Bedroom Flat">1 Bedroom Flat</option>
                        <option value="Ensuite Room" data-base="Ensuite Room">Ensuite Room</option>
                        <option value="Double Room"  data-base="Double Room">Double Room</option>
                        <option value="Single Room"  data-base="Single Room">Single Room</option>
                        <option value="Room"         data-base="Room (Shared)">Room (Shared)</option>
                    </select>
                </div>

                <div class="filter-group">
                    <div class="filter-label">Platform</div>
                    <select id="filter-source">
                        <option value="all">All Platforms</option>
                        <option value="OpenRent">OpenRent</option>
                        <option value="Rightmove">Rightmove</option>
                        <option value="OnTheMarket">OnTheMarket</option>
                        <option value="Zoopla">Zoopla</option>
                    </select>
                </div>

                <div class="filter-group" style="justify-content:flex-end; gap:0.6rem;">
                    <label class="checkbox-container">
                        <input type="checkbox" id="filter-walkonly">
                        <span>Walking distance only (&lt;20 min walk)</span>
                    </label>
                    <label class="checkbox-container">
                        <input type="checkbox" id="filter-bills">
                        <span>Bills included only</span>
                    </label>
                </div>

            </div>

            <!-- Results bar inside sticky panel -->
            <div class="results-bar">
                <span class="result-count" id="result-count"><strong>0</strong> properties</span>

                <div class="sort-group">
                    <span>Sort:</span>
                    <select class="sort-select" id="sort-select">
                        <option value="commute">Shortest Commute</option>
                        <option value="rent">Lowest Rent</option>
                        <option value="allin">Lowest All-in Cost</option>
                        <option value="newest">Newest First</option>
                        <option value="distance">Closest Distance</option>
                    </select>
                </div>

                <div class="view-toggle">
                    <button class="view-btn active" id="btn-grid" title="Grid view">⊞ Grid</button>
                    <button class="view-btn" id="btn-list" title="List view">☰ List</button>
                </div>

                <div class="btn-row">
                    <button class="reset-btn" id="btn-reset">✕ Reset</button>
                    <button class="apply-btn" id="btn-apply">⚡ Apply</button>
                </div>
            </div>
        </div>

        <!-- Property grid / list -->
        <div id="properties-grid" class="view-mode-grid"></div>

    </div>

    <script>
        const properties = {properties_js};
        const VIEWED_KEY = 'room_finder_viewed_v2';

        // ── DOM refs ──────────────────────────────────────────────────
        const rentSlider    = document.getElementById('filter-rent');
        const rentDisplay   = document.getElementById('rent-val');
        const commuteSlider = document.getElementById('filter-commute');
        const commuteDisplay= document.getElementById('commute-val');
        const walkSlider    = document.getElementById('filter-walk');
        const walkDisplay   = document.getElementById('walk-val');
        const typeSelect    = document.getElementById('filter-type');
        const sourceSelect  = document.getElementById('filter-source');
        const walkonlyCheck = document.getElementById('filter-walkonly');
        const billsCheck    = document.getElementById('filter-bills');
        const sortSelect    = document.getElementById('sort-select');
        const applyBtn      = document.getElementById('btn-apply');
        const resetBtn      = document.getElementById('btn-reset');
        const btnGrid       = document.getElementById('btn-grid');
        const btnList       = document.getElementById('btn-list');
        const grid          = document.getElementById('properties-grid');
        const resultCount   = document.getElementById('result-count');
        const statMatches   = document.getElementById('stat-matches');
        const statMinRent   = document.getElementById('stat-min-rent');
        const statAvgCommute= document.getElementById('stat-avg-commute');

        let currentView = 'grid'; // 'grid' | 'list'

        // ── Viewed state (localStorage) ───────────────────────────────
        function getViewedIds() {{
            try {{ return new Set(JSON.parse(localStorage.getItem(VIEWED_KEY) || '[]')); }}
            catch {{ return new Set(); }}
        }}

        function markAsViewed(id) {{
            const v = getViewedIds();
            if (v.has(id)) return;
            v.add(id);
            try {{ localStorage.setItem(VIEWED_KEY, JSON.stringify([...v])); }}
            catch {{}}
            // Refresh the currently rendered cards to show viewed state immediately
            document.querySelectorAll(`[data-prop-id="${{id}}"]`).forEach(el => {{
                const card = el.closest('.card, .list-row');
                if (card) {{
                    card.classList.add('card--viewed');
                    const tag = card.querySelector('.viewed-tag, .list-viewed-tag');
                    if (tag) tag.style.display = 'block';
                }}
            }});
        }}

        // ── Age helpers ───────────────────────────────────────────────
        function getAgeScore(p) {{
            const age = String(p.listing_age || '').toLowerCase().trim();
            if (!age || age === 'active') return 999;

            // Plain integer string (OnTheMarket returns e.g. "3")
            const asInt = parseInt(age, 10);
            if (!isNaN(asInt) && String(asInt) === age) return asInt;

            // "Xh ago" or "listed Xh ago" (OpenRent)
            const hIdx = age.indexOf('h ago');
            if (hIdx > 0) {{
                const hPart = parseInt(age.slice(0, hIdx).trim().split(' ').pop(), 10);
                if (!isNaN(hPart)) return hPart / 24;
            }}

            if (age.includes('today') || age.includes('just added')) return 0;
            if (age.includes('yesterday')) return 1;

            // "X day" / "X days" / "listed X days ago"
            const dayIdx = age.indexOf('day');
            if (dayIdx > 0) {{
                const tokens = age.slice(0, dayIdx).trim().split(' ').filter(t => t);
                const n = parseInt(tokens[tokens.length - 1], 10);
                if (!isNaN(n)) return n;
            }}

            return 999;
        }}

        function getAgePill(p) {{
            const age = String(p.listing_age || '').toLowerCase();
            if (age.includes('reduced')) return '<span class="pill-reduced">↓ REDUCED</span>';
            if (getAgeScore(p) < 1) return '<span class="pill-new">★ NEW</span>';
            return '';
        }}

        function getCardOpacity(p) {{
            const s = getAgeScore(p);
            if (s < 1)   return 1.0;
            if (s <= 2)  return 0.92;
            if (s <= 5)  return 0.82;
            if (s <= 10) return 0.72;
            return 0.60;
        }}

        // ── Bills estimate ────────────────────────────────────────────
        function billsExtra(p) {{
            if (p.bills_included) return 0;
            const rooms = ['Room','Double Room','Single Room','Ensuite Room'];
            return rooms.includes(p.property_type) ? 100 : 150;
        }}

        function allInCost(p) {{ return p.price + billsExtra(p); }}

        // ── Sort ──────────────────────────────────────────────────────
        function sortList(list) {{
            const by = sortSelect.value;
            return [...list].sort((a, b) => {{
                if (by === 'commute') {{
                    if (a.commute_time === null && b.commute_time === null) return a.distance_km - b.distance_km;
                    if (a.commute_time === null) return 1;
                    if (b.commute_time === null) return -1;
                    return a.commute_time - b.commute_time;
                }}
                if (by === 'rent')    return a.price - b.price;
                if (by === 'allin')   return allInCost(a) - allInCost(b);
                if (by === 'newest')  return getAgeScore(a) - getAgeScore(b);
                if (by === 'distance') return a.distance_km - b.distance_km;
                return 0;
            }});
        }}

        // ── Commute display ───────────────────────────────────────────
        function commuteText(p) {{
            if (p.commute_time !== null) {{
                return p.is_walk_only
                    ? `🚶 ${{p.commute_time}} min walk`
                    : `🚇 ${{p.commute_time}} min transit`;
            }}
            return p.distance_km > 10
                ? '⚠ Beyond 10km range'
                : '⚠ TfL data unavailable';
        }}

        function commuteCls(p) {{
            if (p.commute_time === null) return 'commute-none';
            if (p.commute_time <= 20)   return 'commute-fast';
            if (p.commute_time <= 35)   return 'commute-med';
            return 'commute-slow';
        }}

        function walkText(p) {{
            if (p.station_walk_time !== null) return `${{p.station_walk_time}} min walk`;
            if (p.is_walk_only) return 'Direct walk';
            return '—';
        }}

        // ── Type badge HTML ───────────────────────────────────────────
        function typeBadgeHtml(pt) {{
            const map = {{
                'Studio':       ['badge studio',  'Studio'],
                '1 Bed Flat':   ['badge onebed',  '1 Bed Flat'],
                'Ensuite Room': ['badge ensuite', 'Ensuite'],
                'Double Room':  ['badge ensuite', 'Double'],
                'Single Room':  ['badge ensuite', 'Single'],
                'Room':         ['badge ensuite', 'Room'],
            }};
            const [cls, label] = map[pt] || ['badge ensuite', pt || 'Room'];
            return `<span class="${{cls}}">${{label}}</span>`;
        }}

        // ── Platform badges HTML ──────────────────────────────────────
        function platformBadgesHtml(p) {{
            if (p.sources && p.sources.length > 0) {{
                return p.sources.map(s =>
                    `<span class="platform-badge ${{s.source.toLowerCase()}}">${{s.source}}</span>`
                ).join(' ');
            }}
            return `<span class="platform-badge ${{p.source.toLowerCase()}}">${{p.source}}</span>`;
        }}

        // ── Footer buttons HTML ───────────────────────────────────────
        function footerBtnsHtml(p) {{
            let btns = '';
            if (p.sources && p.sources.length > 0) {{
                p.sources.forEach((src, i) => {{
                    btns += `<a href="${{src.url}}" target="_blank" class="${{i === 0 ? 'btn-primary' : 'btn-secondary'}} view-link"
                               data-prop-id="${{p.id}}">View ${{src.source}}</a>`;
                }});
            }} else {{
                btns = `<a href="${{p.url}}" target="_blank" class="btn-primary view-link"
                           data-prop-id="${{p.id}}">View Listing</a>`;
            }}
            const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${{p.lat}},${{p.lng}}&destination=51.5215,-0.1361&travelmode=transit`;
            btns += `<a href="${{mapsUrl}}" target="_blank" class="btn-secondary">🗺 Map</a>`;
            return btns;
        }}

        // ── Bills note HTML ───────────────────────────────────────────
        function allInNoteHtml(p) {{
            if (p.bills_included) {{
                return `<span class="all-in-note included">✓ Bills included</span>`;
            }}
            const est = allInCost(p);
            return `<span class="all-in-note estimated">~£${{est.toLocaleString()}}/mo est. all-in</span>`;
        }}

        // ── Render: grid card ─────────────────────────────────────────
        function renderCard(p, viewedIds) {{
            const isViewed  = viewedIds.has(p.id);
            const opacity   = isViewed ? 1 : getCardOpacity(p);
            const agePill   = getAgePill(p);
            const billsBadge = p.bills_included
                ? '<span class="badge bills">Bills Incl.</span>'
                : '<span class="badge no-bills">Bills Excl.</span>';
            const furnBadge  = p.furnished !== 'Unknown'
                ? `<span class="badge furnished">${{p.furnished}}</span>`
                : '<span class="badge unfurnished">Furn. Unknown</span>';

            return `
            <div class="card${{isViewed ? ' card--viewed' : ''}}"
                 style="opacity:${{opacity}}">
                ${{isViewed ? '<span class="viewed-tag">✓ Viewed</span>' : ''}}
                <div class="card-header">
                    <div class="price-block">
                        <span class="rent-price">£${{p.price.toLocaleString()}} <small>/mo</small></span>
                        ${{allInNoteHtml(p)}}
                    </div>
                    <div class="header-right">
                        ${{agePill}}
                        ${{platformBadgesHtml(p)}}
                    </div>
                </div>
                <div class="card-body">
                    <div class="address" title="${{p.address}}">📍 ${{p.address}}</div>
                    <div class="metric">
                        <span class="metric-label">Commute:</span>
                        <span class="metric-value ${{commuteCls(p)}}">${{commuteText(p)}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Walk to station:</span>
                        <span class="metric-value">${{walkText(p)}}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Direct distance:</span>
                        <span class="metric-value">${{p.distance_km.toFixed(2)}} km</span>
                    </div>
                    <div class="badges">
                        ${{typeBadgeHtml(p.property_type)}}
                        ${{billsBadge}}
                        ${{furnBadge}}
                    </div>
                    <div class="listing-age">🕒 ${{p.listing_age || 'Active'}}</div>
                </div>
                <div class="card-footer">
                    ${{footerBtnsHtml(p)}}
                </div>
            </div>`;
        }}

        // ── Render: list row ──────────────────────────────────────────
        function renderListRow(p, viewedIds) {{
            const isViewed = viewedIds.has(p.id);
            const opacity  = isViewed ? 1 : getCardOpacity(p);
            const agePill  = getAgePill(p);
            const est      = allInCost(p);
            const allInLine = p.bills_included
                ? `<span class="list-allin included">Bills incl.</span>`
                : `<span class="list-allin">~£${{est.toLocaleString()}} all-in</span>`;

            // First source link only for list view
            let primaryUrl = p.url;
            let primarySrc = p.source;
            if (p.sources && p.sources.length > 0) {{
                primaryUrl = p.sources[0].url;
                primarySrc = p.sources[0].source;
            }}
            const mapsUrl = `https://www.google.com/maps/dir/?api=1&origin=${{p.lat}},${{p.lng}}&destination=51.5215,-0.1361&travelmode=transit`;

            return `
            <div class="list-row${{isViewed ? ' card--viewed' : ''}}" style="opacity:${{opacity}}">
                <div class="list-pills">
                    ${{typeBadgeHtml(p.property_type)}}
                    ${{agePill}}
                    ${{isViewed ? '<span class="list-viewed-tag">✓ Viewed</span>' : ''}}
                </div>
                <div class="list-address" title="${{p.address}}">${{p.address}}</div>
                <div class="list-price-block">
                    <span class="list-price">£${{p.price.toLocaleString()}}</span>
                    ${{allInLine}}
                </div>
                <div class="list-commute ${{commuteCls(p)}}">${{commuteText(p)}}</div>
                <div class="list-walk">${{walkText(p)}}</div>
                <div class="list-platform">${{platformBadgesHtml(p)}}</div>
                <div class="list-actions">
                    <a href="${{primaryUrl}}" target="_blank"
                       class="btn-primary view-link" data-prop-id="${{p.id}}">View</a>
                    <a href="${{mapsUrl}}" target="_blank" class="btn-secondary">🗺</a>
                </div>
            </div>`;
        }}

        // ── Render all ────────────────────────────────────────────────
        function renderCards(list) {{
            const viewedIds = getViewedIds();
            grid.innerHTML = '';

            if (list.length === 0) {{
                grid.innerHTML = `
                    <div class="no-results">
                        <h2>No properties matched your filters</h2>
                        <p>Try relaxing rent budget, commute time, or station walk limits.</p>
                    </div>`;
                return;
            }}

            const html = list.map(p =>
                currentView === 'list' ? renderListRow(p, viewedIds) : renderCard(p, viewedIds)
            ).join('');
            grid.innerHTML = html;
        }}

        // ── Update type dropdown counts ───────────────────────────────
        function updateTypeCounts(preTypeFiltered) {{
            const counts = {{}};
            preTypeFiltered.forEach(p => {{
                counts[p.property_type] = (counts[p.property_type] || 0) + 1;
            }});
            typeSelect.querySelectorAll('option').forEach(opt => {{
                const base = opt.dataset.base;
                if (!base) return;
                if (opt.value === 'all') {{
                    opt.textContent = `${{base}} (${{preTypeFiltered.length}})`;
                }} else {{
                    opt.textContent = `${{base}} (${{counts[opt.value] || 0}})`;
                }}
            }});
        }}

        // ── Stats panel ───────────────────────────────────────────────
        function updateStats(list) {{
            statMatches.textContent = list.length;
            if (!list.length) {{
                statMinRent.textContent = '£—';
                statAvgCommute.textContent = '— mins';
                return;
            }}
            statMinRent.textContent = '£' + Math.min(...list.map(p => p.price)).toLocaleString();
            const valid = list.filter(p => p.commute_time !== null).map(p => p.commute_time);
            statAvgCommute.textContent = valid.length
                ? Math.round(valid.reduce((a,b)=>a+b,0)/valid.length) + ' mins'
                : '— mins';
        }}

        // ── Main filter + render ──────────────────────────────────────
        function applyFilters() {{
            const maxRent    = parseInt(rentSlider.value);
            const maxCommute = parseInt(commuteSlider.value);
            const maxWalk    = parseInt(walkSlider.value);
            const selType    = typeSelect.value;
            const selSource  = sourceSelect.value;
            const walkOnly   = walkonlyCheck.checked;
            const billsOnly  = billsCheck.checked;

            rentDisplay.textContent    = '£' + maxRent.toLocaleString();
            commuteDisplay.textContent = maxCommute + ' mins';
            walkDisplay.textContent    = maxWalk + ' mins';

            // Pass 1: all filters EXCEPT type — for count display in dropdown
            const preType = properties.filter(p => {{
                if (p.price > maxRent) return false;
                if (walkOnly) {{
                    if (!(p.is_walk_only && p.commute_time !== null && p.commute_time <= 20) &&
                        !(p.distance_km <= 1.4)) return false;
                }}
                if (!walkOnly && p.commute_time !== null && p.commute_time > maxCommute) return false;
                if (p.station_walk_time !== null && p.station_walk_time > maxWalk) return false;
                if (billsOnly && !p.bills_included) return false;
                if (selSource !== 'all') {{
                    const has = p.sources?.some(s => s.source === selSource) || p.source === selSource;
                    if (!has) return false;
                }}
                return true;
            }});

            updateTypeCounts(preType);

            // Pass 2: apply type filter
            const filtered = preType.filter(p =>
                selType === 'all' || p.property_type === selType
            );

            const sorted = sortList(filtered);

            // Update results bar count
            const sortLabel = sortSelect.options[sortSelect.selectedIndex].text;
            resultCount.innerHTML = `<strong>${{sorted.length}}</strong> properties &nbsp;·&nbsp; ${{sortLabel}}`;

            renderCards(sorted);
            updateStats(sorted);
        }}

        // ── View toggle ───────────────────────────────────────────────
        function setView(v) {{
            currentView = v;
            grid.className = v === 'list' ? 'view-mode-list' : 'view-mode-grid';
            btnGrid.classList.toggle('active', v === 'grid');
            btnList.classList.toggle('active', v === 'list');
            applyFilters();
        }}

        // ── Reset ─────────────────────────────────────────────────────
        function resetFilters() {{
            rentSlider.value    = 1400;
            commuteSlider.value = 40;
            walkSlider.value    = 10;
            typeSelect.value    = 'all';
            sourceSelect.value  = 'all';
            walkonlyCheck.checked = false;
            billsCheck.checked    = false;
            sortSelect.value    = 'commute';
            applyFilters();
        }}

        // ── Click delegation for "viewed" tracking ────────────────────
        grid.addEventListener('click', e => {{
            const link = e.target.closest('.view-link');
            if (link) {{
                const id = link.dataset.propId;
                if (id) markAsViewed(id);
            }}
        }});

        // ── Slider live display updates ───────────────────────────────
        rentSlider.addEventListener('input',    () => rentDisplay.textContent    = '£' + parseInt(rentSlider.value).toLocaleString());
        commuteSlider.addEventListener('input', () => commuteDisplay.textContent = commuteSlider.value + ' mins');
        walkSlider.addEventListener('input',    () => walkDisplay.textContent    = walkSlider.value + ' mins');

        // ── Control events ────────────────────────────────────────────
        applyBtn.addEventListener('click', applyFilters);
        resetBtn.addEventListener('click', resetFilters);
        sortSelect.addEventListener('change', applyFilters);
        btnGrid.addEventListener('click', () => setView('grid'));
        btnList.addEventListener('click', () => setView('list'));

        // ── Initial render ────────────────────────────────────────────
        window.addEventListener('DOMContentLoaded', applyFilters);
    </script>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html_content)
    print(f"🔥 Dashboard generated at: {output_path}")
