import math
import time
import logging
from curl_cffi import requests

logger = logging.getLogger(__name__)


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate the great-circle distance between two points in km."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


class BaseScraper:
    def __init__(self):
        # curl_cffi impersonates Chrome to bypass Cloudflare TLS fingerprints
        self.session = requests.Session(impersonate="chrome120")
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        })

    def fetch_html(self, url: str) -> str | None:
        """Fetch HTML with exponential backoff on failures and rate-limit responses."""
        for attempt in range(3):
            try:
                time.sleep(0.5 * (attempt + 1))  # polite baseline delay
                resp = self.session.get(url, timeout=15)
                if resp.status_code == 200:
                    return resp.text
                if resp.status_code == 429:
                    # Respect rate-limit: back off and retry
                    wait = 5 * (2 ** attempt)
                    logger.warning(f"429 rate-limit from {url} — waiting {wait}s (attempt {attempt + 1}/3)")
                    time.sleep(wait)
                    continue
                if resp.status_code in (503, 502, 504):
                    wait = 3 * (2 ** attempt)
                    logger.warning(f"Server error {resp.status_code} from {url} — retrying in {wait}s")
                    time.sleep(wait)
                    continue
                # Other non-200 (403, 404, etc.) — no point retrying
                logger.warning(f"Non-retryable status {resp.status_code} for {url}")
                return None
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
        return None
