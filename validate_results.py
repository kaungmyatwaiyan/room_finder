#!/usr/bin/env python
import os
import json
import logging
from scrapers.base import haversine_distance
from src.config import (
    MAX_RENT, TFL_MAX_DISTANCE_KM,
    DEDUPLICATION_RADIUS_KM, DEDUPLICATION_PRICE_THRESHOLD
)

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("validator")


def validate():
    logger.info("🔍 Starting data validation for room_finder output...")

    # 1. Check file existence — paths are relative to this script, not the CWD
    json_path = os.path.join(_BASE_DIR, "properties.json")
    html_path = os.path.join(_BASE_DIR, "commute_matching_rentals.html")

    if not os.path.exists(json_path):
        logger.error(f"❌ '{json_path}' not found!")
        return False
    if not os.path.exists(html_path):
        logger.error(f"❌ '{html_path}' not found!")
        return False

    # 2. Parse properties.json
    try:
        with open(json_path, 'r') as f:
            properties = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to parse '{json_path}' as JSON: {e}")
        return False

    if not isinstance(properties, list):
        logger.error(f"❌ Expected a list of properties, got {type(properties)}")
        return False

    total_count = len(properties)
    logger.info(f"📊 Loaded {total_count} properties from '{json_path}'")
    if total_count == 0:
        logger.error("❌ The properties list is empty!")
        return False

    # 3. Schema, price limit, and London bounding-box checks
    errors = 0
    required_fields = ["id", "price", "lat", "lng", "url", "source", "distance_km"]

    for idx, p in enumerate(properties):
        for field in required_fields:
            if field not in p:
                logger.error(
                    f"❌ Property at index {idx} (ID: {p.get('id', 'unknown')}) "
                    f"is missing required field '{field}'"
                )
                errors += 1

        price = p.get("price")
        if price is not None:
            if not isinstance(price, (int, float)):
                logger.error(f"❌ Property ID {p.get('id')} has non-numeric price: {price}")
                errors += 1
            elif price > MAX_RENT:
                logger.error(
                    f"❌ Property ID {p.get('id')} exceeds MAX_RENT! "
                    f"Price: £{price} > £{MAX_RENT}"
                )
                errors += 1

        lat, lng = p.get("lat"), p.get("lng")
        if lat is not None and lng is not None:
            if not (51.2 <= lat <= 51.7) or not (-0.6 <= lng <= 0.3):
                logger.warning(
                    f"⚠️ Property ID {p.get('id')} coordinates look suspicious "
                    f"for London: ({lat}, {lng})"
                )

    # 4. Deduplication audit
    # Sort by latitude first so the inner loop can break early once properties
    # are too far away by latitude alone — O(n*k) instead of O(n²).
    logger.info("🧪 Auditing deduplication logic...")
    lat_deg_per_km = 1.0 / 111.0
    sorted_props    = sorted(properties, key=lambda x: x.get('lat', 0))
    duplicates_found = 0

    for i, p1 in enumerate(sorted_props):
        for j in range(i + 1, len(sorted_props)):
            p2 = sorted_props[j]
            if (p2.get('lat', 0) - p1.get('lat', 0)) > DEDUPLICATION_RADIUS_KM * lat_deg_per_km:
                break  # all remaining properties are too far north — stop
            dist       = haversine_distance(p1['lat'], p1['lng'], p2['lat'], p2['lng'])
            price_diff = abs(p1['price'] - p2['price'])
            if dist <= DEDUPLICATION_RADIUS_KM and price_diff <= DEDUPLICATION_PRICE_THRESHOLD:
                logger.error(
                    f"❌ Unmerged duplicate: "
                    f"P1 (ID {p1['id']}, {p1['source']}, £{p1['price']}) and "
                    f"P2 (ID {p2['id']}, {p2['source']}, £{p2['price']}) "
                    f"are {dist * 1000:.1f}m apart with £{price_diff} price diff."
                )
                duplicates_found += 1
                errors += 1

    if duplicates_found == 0:
        logger.info("✅ Deduplication check passed — no unmerged duplicates found.")

    # 5. TfL commute coverage audit
    logger.info("🧪 Auditing TfL commute coverage...")
    queried_props = [p for p in properties if p.get('commute_time') is not None]
    within_range  = [p for p in properties if p.get('distance_km', 999) <= TFL_MAX_DISTANCE_KM]
    logger.info(f"🚇 {len(queried_props)} properties have live commute times.")
    logger.info(f"📍 {len(within_range)} properties within {TFL_MAX_DISTANCE_KM}km (expected to be queried).")
    tfl_coverage = len(queried_props) / len(within_range) * 100 if within_range else 0
    logger.info(f"✅ TfL coverage: {tfl_coverage:.1f}% of in-range properties have commute times.")

    # 6. Conclusion
    if errors == 0:
        logger.info("✨ SUCCESS: All validation checks passed!")
        return True
    else:
        logger.error(f"❌ FAILURE: Found {errors} error(s) in validation.")
        return False


if __name__ == "__main__":
    import sys
    sys.exit(0 if validate() else 1)
