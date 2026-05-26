import logging
import re
import json
from .base import BaseScraper

logger = logging.getLogger(__name__)

class RightmoveScraper(BaseScraper):
    def fetch(self, max_rent: int = 2000) -> list[dict]:
        logger.info("🚀 Fetching property data from Rightmove...")
        properties = []
        
        page = 0
        while True:
            index = page * 24
            url = f"https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E87490&maxPrice={max_rent}&minPrice=100&propertyTypes=flat&includeLetAgreed=false&index={index}"
            
            html = self.fetch_html(url)
            if not html:
                break
                
            next_data_match = re.search(r'<script\b[^>]*id="__NEXT_DATA__"[^>]*>([\s\S]*?)</script>', html)
            if not next_data_match:
                break
                
            try:
                data = json.loads(next_data_match.group(1))
                search_results = data.get("props", {}).get("pageProps", {}).get("searchResults", {})
                raw_props = search_results.get("properties", [])
                
                if not raw_props:
                    break  # No more properties on this page, end of pagination
                    
                for rp in raw_props:
                    beds = rp.get('bedrooms', 0)
                    is_stud = rp.get('propertySubType', '').lower() == 'studio' or 'studio' in rp.get('propertyTypeFullDescription', '').lower()
                    
                    summary_lower = rp.get('summary', '').lower()
                    title_lower = rp.get('propertyTypeFullDescription', '').lower() + summary_lower
                    is_room = 'room' in title_lower or 'flatshare' in title_lower or 'house share' in title_lower or 'room to rent' in title_lower
                    
                    prop_type = '1 Bed Flat'
                    if is_stud:
                        prop_type = 'Studio'
                    elif is_room:
                        prop_type = 'Ensuite Room'
                    elif beds != 1:
                        continue
                    
                    furn_status = 'Unknown'
                    if 'unfurnished' in summary_lower:
                        furn_status = 'Unfurnished'
                    elif 'furnished' in summary_lower:
                        furn_status = 'Furnished'

                    bills_inc = 'bills included' in summary_lower or 'all bills' in summary_lower

                    # Single pass over keyFeatures for both furnished status and bills
                    for feat in rp.get('keyFeatures', []):
                        desc = feat.get('description', '').lower()
                        if 'unfurnished' in desc:
                            furn_status = 'Unfurnished'
                        elif 'furnished' in desc and furn_status == 'Unknown':
                            furn_status = 'Furnished'
                        if 'bills included' in desc or 'all bills' in desc:
                            bills_inc = True
                            
                    # Convert weekly prices to monthly (× 52 ÷ 12 = 4.333)
                    raw_amount = int(rp.get('price', {}).get('amount', 0))
                    frequency = rp.get('price', {}).get('frequency', 'monthly').upper()
                    if frequency == 'WEEKLY':
                        monthly_price = round(raw_amount * 52 / 12)
                    else:
                        monthly_price = raw_amount

                    if monthly_price > max_rent or monthly_price == 0:
                        continue

                    properties.append({
                        "id": f"rightmove-{rp.get('id')}",
                        "price": monthly_price,
                        "bedrooms": beds,
                        "is_studio": is_stud,
                        "property_type": prop_type,
                        "lat": float(rp.get('location', {}).get('latitude', 0)),
                        "lng": float(rp.get('location', {}).get('longitude', 0)),
                        "source": "Rightmove",
                        "address": rp.get('displayAddress', 'London, UK'),
                        "url": f"https://www.rightmove.co.uk{rp.get('propertyUrl')}",
                        "furnished": furn_status,
                        "bills_included": bills_inc,
                        "listing_age": rp.get('addedOrReduced', 'Active')
                    })
            except Exception as e:
                logger.error(f"Error fetching Rightmove page index {index}: {e}")
                break
                
            # Rightmove limits pagination index usually
            if page >= 40:  # Max ~1000 properties safeguard
                break
            page += 1
                
        logger.info(f"✅ Rightmove: Retrieved {len(properties)} properties.")
        return properties
