import urllib.request
import urllib.error
import json
import time
import random
import logging
from .config import TARGET_POSTCODE

logger = logging.getLogger(__name__)


def get_tfl_commute_time(from_lat, from_lng, to_postcode=TARGET_POSTCODE):
    """Query TfL Unified API for commute time, station walk duration, and walk-only flag.

    Called only for genuinely new property coordinates (cache misses). Volume is
    typically 20-50 calls per daily run, so no semaphore or burst control is needed.
    Retries on 429 by waiting the full Retry-After period rather than bailing out.
    """
    url = f"https://api.tfl.gov.uk/Journey/JourneyResults/{from_lat},{from_lng}/to/{to_postcode}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    max_retries = 5

    for attempt in range(max_retries):
        req = urllib.request.Request(url, headers=headers)
        try:
            time.sleep(0.5 + random.uniform(0, 0.5))  # polite gap between calls
            with urllib.request.urlopen(req, timeout=15) as response:
                data = json.loads(response.read().decode("utf-8"))
                journeys = data.get("journeys", [])
                if not journeys:
                    return None, None, None

                shortest = min(journeys, key=lambda j: j.get("duration", 999))
                duration = shortest.get("duration", 999)
                legs = shortest.get("legs", [])

                is_walk_only = (
                    len(legs) == 1 and legs[0].get("mode", {}).get("id") == "walking"
                )

                station_walk = 0
                if legs and legs[0].get("mode", {}).get("id") == "walking":
                    station_walk = legs[0].get("duration", 0)

                return duration, station_walk, is_walk_only

        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = e.headers.get("Retry-After")
                try:
                    wait = float(retry_after) if retry_after else 2.0 * (2 ** attempt) + random.uniform(0, 2)
                except (ValueError, TypeError):
                    wait = 2.0 * (2 ** attempt) + random.uniform(0, 2)

                logger.warning(
                    f"TfL 429 for ({from_lat:.4f},{from_lng:.4f}) — "
                    f"waiting {wait:.0f}s (attempt {attempt + 1}/{max_retries})"
                )
                time.sleep(wait)
                continue
            else:
                logger.error(f"TfL HTTP {e.code} for ({from_lat:.4f},{from_lng:.4f}): {e}")
                break

        except Exception as e:
            logger.error(f"TfL request error for ({from_lat:.4f},{from_lng:.4f}): {e}")
            break

    return None, None, None
