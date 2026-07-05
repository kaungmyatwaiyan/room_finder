import logging
import re
import json
from .base import BaseScraper, classify_room_type

logger = logging.getLogger(__name__)

class OnTheMarketScraper(BaseScraper):
    def fetch(self, max_rent: int = 2000) -> list[dict]:
        logger.info("🚀 Fetching property data from OnTheMarket...")
        properties = []

        page = 1
        while True:
            url  = f"https://www.onthemarket.com/to-rent/property/london/?max-price={max_rent}&page={page}"
            html = self.fetch_html(url)
            if not html:
                break

            next_data_match = re.search(r'<script\b[^>]*id="__NEXT_DATA__"[^>]*>([\s\S]*?)</script>', html)
            if not next_data_match:
                break

            try:
                data      = json.loads(next_data_match.group(1))
                results   = data.get("props", {}).get("initialReduxState", {}).get("results", {})
                raw_props = results.get("list", [])

                if not raw_props:
                    break

                for rp in raw_props:
                    beds      = rp.get('bedrooms', 0)
                    title     = rp.get('property-title', '').lower()
                    is_stud   = 'studio' in title or rp.get('humanised-property-type', '').lower() == 'studio'
                    is_room   = (
                        'room' in title or 'flatshare' in title or 'house share' in title or
                        'room to rent' in rp.get('humanised-property-type', '').lower()
                    )

                    prop_type = '1 Bed Flat'
                    if is_stud:
                        prop_type = 'Studio'
                    elif is_room:
                        prop_type = classify_room_type(
                            rp.get('property-title', ''),
                            rp.get('description', '')
                        )
                    elif beds != 1:
                        continue

                    price_str   = rp.get('price', '0')
                    price_match = re.search(r'£([\d,]+)', price_str)
                    if price_match:
                        raw_price = int(price_match.group(1).replace(',', ''))
                        price_num = round(raw_price * 52 / 12) if 'pw' in price_str.lower() else raw_price
                    else:
                        continue

                    if price_num > max_rent:
                        continue

                    furn_status = 'Unknown'
                    bills_inc   = False
                    features    = rp.get('features', [])
                    for feat in features:
                        feat_lower = feat.lower()
                        if 'unfurnished' in feat_lower:
                            furn_status = 'Unfurnished'
                        elif 'furnished' in feat_lower and furn_status == 'Unknown':
                            furn_status = 'Furnished'
                        if 'bills included' in feat_lower or 'all bills' in feat_lower:
                            bills_inc = True

                    # Also check the property description if present
                    desc_lower = rp.get('description', '').lower()
                    if not bills_inc and ('bills included' in desc_lower or 'all bills' in desc_lower):
                        bills_inc = True

                    properties.append({
                        "id":            f"onthemarket-{rp.get('id')}",
                        "price":         price_num,
                        "bedrooms":      beds,
                        "is_studio":     is_stud,
                        "property_type": prop_type,
                        "lat":           float(rp.get('location', {}).get('lat', 0)),
                        "lng":           float(rp.get('location', {}).get('lon', 0)),
                        "source":        "OnTheMarket",
                        "address":       rp.get('address', 'London, UK'),
                        "url":           f"https://www.onthemarket.com{rp.get('details-url')}",
                        "furnished":     furn_status,
                        "bills_included": bills_inc,
                        "listing_age":   rp.get('days-since-added-reduced', 'Active')
                    })
            except Exception as e:
                logger.error(f"Error fetching OnTheMarket page {page}: {e}")
                break

            if page >= 40:
                break
            page += 1

        logger.info(f"✅ OnTheMarket: Retrieved {len(properties)} properties.")
        return properties
