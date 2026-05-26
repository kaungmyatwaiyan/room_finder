import os
import logging

# Centralised Configuration for Room Finder

# Target location — configurable via environment variables so the pipeline can be
# retargeted without any code change. Set TARGET_LAT, TARGET_LNG, TARGET_POSTCODE
# as GitHub Actions variables (Settings > Variables) to point at a different address.
# Defaults to 60 Whitfield St, London W1T 4EU.
TARGET_LAT      = float(os.getenv("TARGET_LAT",      "51.5215"))
TARGET_LNG      = float(os.getenv("TARGET_LNG",      "-0.1361"))
TARGET_POSTCODE = os.getenv("TARGET_POSTCODE", "W1T4EU")

# Scraper limits
MAX_RENT = 2000

# TfL API - query all properties within this direct distance from the target location.
# 10km covers all realistic commute candidates; beyond that we skip TfL to save time.
TFL_MAX_DISTANCE_KM = 10.0

# TfL cached journey times expire after this many days and are re-fetched.
# TfL timetables change roughly twice a year; 30 days is a conservative TTL.
TFL_CACHE_TTL_DAYS = 30

# Deduplication thresholds
DEDUPLICATION_RADIUS_KM = 0.05       # 50 metres
DEDUPLICATION_PRICE_THRESHOLD = 20   # £20


# Logging Configuration
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
    )
