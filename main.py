import os
import json
import logging
from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from scrapers import OpenRentScraper, RightmoveScraper, OnTheMarketScraper, ZooplaScraper
from src.tfl_api import get_tfl_commute_time
from src.dashboard_gen import generate_interactive_dashboard
from scrapers.base import haversine_distance
from src.config import (
    TARGET_LAT, TARGET_LNG, TARGET_POSTCODE, MAX_RENT,
    TFL_MAX_DISTANCE_KM, TFL_CACHE_TTL_DAYS,
    DEDUPLICATION_RADIUS_KM, DEDUPLICATION_PRICE_THRESHOLD, setup_logging
)

logger = logging.getLogger(__name__)


def load_tfl_cache(json_path: str) -> dict:
    """Load the TfL commute cache from the previous run's properties.json.

    Keyed by (lat rounded to 4dp, lng rounded to 4dp) — ~11m precision.
    Entries older than TFL_CACHE_TTL_DAYS are excluded so stale journey times
    are periodically refreshed from the live API.

    Returns an empty dict if no previous data exists.
    """
    if not os.path.exists(json_path):
        return {}
    try:
        with open(json_path) as f:
            old_props = json.load(f)
        today = date.today()
        cache = {}
        expired = 0
        for p in old_props:
            if p.get("commute_time") is None:
                continue
            cached_on_str = p.get("tfl_cached_on", "")
            if not cached_on_str:
                continue  # unknown age — treat as expired and skip
            try:
                cached_date = date.fromisoformat(cached_on_str)
                if (today - cached_date).days > TFL_CACHE_TTL_DAYS:
                    expired += 1
                    continue  # expired — will re-query from TfL
            except ValueError:
                continue  # malformed date — treat as expired, skip
            key = (round(p["lat"], 4), round(p["lng"], 4))
            cache[key] = {
                "commute_time":     p["commute_time"],
                "station_walk_time": p.get("station_walk_time"),
                "is_walk_only":     p.get("is_walk_only", False),
                "tfl_cached_on":    cached_on_str,
            }
        logger.info(
            f"📚 TfL cache loaded: {len(cache)} valid entries "
            f"({expired} expired and queued for refresh)."
        )
        return cache
    except Exception as e:
        logger.warning(f"Could not load TfL cache from {json_path}: {e}. Starting cold.")
        return {}


def apply_tfl_cache(
    properties: list[dict], cache: dict
) -> tuple[list[dict], list[dict], int]:
    """Apply cached TfL data and split into hits vs misses.

    Cache hits get commute data applied immediately (no API call).
    Cache misses are returned for live TfL queries.
    """
    misses = []
    for p in properties:
        key = (round(p["lat"], 4), round(p["lng"], 4))
        if key in cache:
            p["commute_time"]      = cache[key]["commute_time"]
            p["station_walk_time"] = cache[key]["station_walk_time"]
            p["is_walk_only"]      = cache[key]["is_walk_only"]
            p["tfl_cached_on"]     = cache[key]["tfl_cached_on"]
        else:
            misses.append(p)
    hits = len(properties) - len(misses)
    return properties, misses, hits


def deduplicate_properties(properties: list[dict]) -> list[dict]:
    """Deduplicate by geographic proximity and price, merging cross-platform sources."""
    source_priority = {"OpenRent": 0, "Rightmove": 1, "Zoopla": 2, "OnTheMarket": 3}
    properties = sorted(properties, key=lambda x: source_priority.get(x.get("source", ""), 9))

    deduped = []
    for p in properties:
        is_dup = False
        for existing in deduped:
            dist = haversine_distance(p["lat"], p["lng"], existing["lat"], existing["lng"])
            price_diff = abs(p["price"] - existing["price"])
            if dist <= DEDUPLICATION_RADIUS_KM and price_diff <= DEDUPLICATION_PRICE_THRESHOLD:
                is_dup = True
                if "sources" not in existing:
                    existing["sources"] = [{"source": existing["source"], "url": existing["url"]}]
                if not any(s["source"] == p["source"] for s in existing["sources"]):
                    existing["sources"].append({"source": p["source"], "url": p["url"]})
                break
        if not is_dup:
            if "sources" not in p:
                p["sources"] = [{"source": p.get("source", "Unknown"), "url": p.get("url", "")}]
            deduped.append(p)
    return deduped


def fetch_commute(p: dict) -> dict:
    """Call the live TfL API for a single property and stamp the result date.

    Defined at module level (not inside a conditional) so it is always available
    and importable for testing.
    """
    duration, station_walk, is_walk = get_tfl_commute_time(p["lat"], p["lng"])
    if duration is not None:
        p["commute_time"]      = duration
        p["station_walk_time"] = station_walk
        p["is_walk_only"]      = is_walk
        p["tfl_cached_on"]     = date.today().isoformat()
    return p


def main():
    setup_logging()

    out_dir   = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(out_dir, "properties.json")

    # ── Step 1: Load TfL cache from previous run ─────────────────────────────
    tfl_cache = load_tfl_cache(json_path)

    # ── Step 2: Scrape all platforms ──────────────────────────────────────────
    combined = []
    combined.extend(OpenRentScraper().fetch(MAX_RENT))
    combined.extend(RightmoveScraper().fetch(MAX_RENT))
    combined.extend(OnTheMarketScraper().fetch(MAX_RENT))
    combined.extend(ZooplaScraper().fetch(MAX_RENT))
    logger.info(f"📦 Total raw properties retrieved: {len(combined)}")

    # ── Step 3: Deduplicate ───────────────────────────────────────────────────
    combined = deduplicate_properties(combined)
    logger.info(f"✨ Properties after deduplication: {len(combined)}")

    # ── Step 4: Calculate direct distances ───────────────────────────────────
    for p in combined:
        p["distance_km"]     = haversine_distance(p["lat"], p["lng"], TARGET_LAT, TARGET_LNG)
        p["commute_time"]    = None
        p["station_walk_time"] = None
        p["is_walk_only"]    = False
        p["tfl_cached_on"]   = ""

    combined.sort(key=lambda x: x["distance_km"])

    # ── Step 5: Split into within-range and beyond-range ─────────────────────
    tfl_targets  = [p for p in combined if p["distance_km"] <= TFL_MAX_DISTANCE_KM]
    beyond_range = [p for p in combined if p["distance_km"] >  TFL_MAX_DISTANCE_KM]

    # ── Step 6: Apply cache — only call TfL for genuine cache misses ──────────
    tfl_targets, tfl_misses, cache_hits = apply_tfl_cache(tfl_targets, tfl_cache)

    logger.info(f"⚡ TfL cache hits : {cache_hits} properties (no API call needed)")
    logger.info(f"🆕 TfL cache misses: {len(tfl_misses)} new/expired — calling live API")
    logger.info(f"⏭️  Beyond {TFL_MAX_DISTANCE_KM}km range: {len(beyond_range)} properties (skipping TfL)")

    # ── Step 7: Call TfL only for cache misses ────────────────────────────────
    if tfl_misses:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(fetch_commute, p): p for p in tfl_misses}
            for future in as_completed(futures):
                p = future.result()
                if p["commute_time"] is not None:
                    sources_str = ", ".join(
                        s["source"] for s in p.get("sources", [{"source": p["source"]}])
                    )
                    logger.info(
                        f"   🚇 [{sources_str}] {p['property_type']} — "
                        f"£{p['price']}/mo — Commute: {p['commute_time']} mins"
                    )

    # ── Step 8: Save and render ───────────────────────────────────────────────
    final_dataset = tfl_targets + beyond_range

    with open(json_path, "w") as f:
        json.dump(final_dataset, f, indent=4)
    logger.info(f"🔥 Saved {len(final_dataset)} properties to {json_path}")

    html_path = os.path.join(out_dir, "commute_matching_rentals.html")
    generate_interactive_dashboard(final_dataset, html_path)


if __name__ == "__main__":
    main()
