import logging
import re
from .base import BaseScraper

logger = logging.getLogger(__name__)

class OpenRentScraper(BaseScraper):
    def fetch(self, max_rent: int = 2000) -> list[dict]:
        logger.info("🚀 Fetching property data from OpenRent...")
        url = f"https://www.openrent.co.uk/properties-to-rent/london?term=London&price_min=100&price_max={max_rent}"

        html = self.fetch_html(url)
        if not html:
            return []

        def extract_array(name):
            """Extract a JS array variable from inline script as a list of strings.

            Uses findall on individual quoted tokens so values containing commas
            (e.g. 'Shoreditch, London') are preserved as single items.
            """
            match = re.search(
                r'var\s+' + re.escape(name) + r'\s*=\s*\[([^\]]*)\]',
                html, re.IGNORECASE
            )
            if not match:
                return []
            content = match.group(1)
            # Extract all single- or double-quoted tokens
            tokens = re.findall(r"['\"]([^'\"]*)['\"]" , content)
            if tokens:
                return tokens
            # Fallback: bare (unquoted) numbers
            return [x.strip() for x in content.split(',') if x.strip()]

        ids         = extract_array("PROPERTYIDS")
        prices      = extract_array("prices")
        bedrooms    = extract_array("bedrooms")
        isstudio    = extract_array("isstudio")
        isshared    = extract_array("isshared")
        lats        = extract_array("PROPERTYLISTLATITUDES")
        lngs        = extract_array("PROPERTYLISTLONGITUDES")
        bills       = extract_array("bills")
        furnished   = extract_array("furnished")
        unfurnished = extract_array("unfurnished")
        hours_live  = extract_array("hoursLive")
        # Attempt to extract per-property addresses; fall back gracefully if absent
        addresses   = (
            extract_array("PROPERTYLISTADDRESSES") or
            extract_array("addresses") or
            []
        )

        lengths = [len(ids), len(prices), len(bedrooms), len(isstudio), len(isshared), len(lats), len(lngs)]
        min_len = min(lengths) if ids else 0

        properties = []
        for i in range(min_len):
            is_stud = int(isstudio[i]) == 1
            beds    = int(bedrooms[i])
            shared  = int(isshared[i]) == 1

            if not is_stud and beds != 1 and not shared:
                continue

            prop_type = '1 Bed Flat'
            if is_stud:
                prop_type = 'Studio'
            elif shared:
                prop_type = 'Ensuite Room'

            furn_status = 'Unknown'
            if i < len(furnished) and int(furnished[i]) == 1:
                furn_status = 'Furnished'
            elif i < len(unfurnished) and int(unfurnished[i]) == 1:
                furn_status = 'Unfurnished'

            age_str = "Active"
            if i < len(hours_live):
                try:
                    hrs  = float(hours_live[i])
                    days = int(hrs // 24)
                    age_str = f"Listed {days} day{'s' if days > 1 else ''} ago" if days > 0 else f"Listed {int(hrs)}h ago"
                except (ValueError, TypeError):
                    age_str = "Active"

            price_val = int(float(prices[i]))
            if price_val > max_rent:
                continue

            address = "London, UK"
            if i < len(addresses) and addresses[i]:
                address = addresses[i]

            properties.append({
                "id":            f"openrent-{ids[i]}",
                "price":         price_val,
                "bedrooms":      beds,
                "is_studio":     is_stud,
                "property_type": prop_type,
                "lat":           float(lats[i]),
                "lng":           float(lngs[i]),
                "source":        "OpenRent",
                "address":       address,
                "url":           f"https://www.openrent.co.uk/{ids[i]}",
                "furnished":     furn_status,
                "bills_included": int(bills[i]) == 1 if i < len(bills) else False,
                "listing_age":   age_str
            })

        logger.info(f"✅ OpenRent: Retrieved {len(properties)} properties.")
        return properties
