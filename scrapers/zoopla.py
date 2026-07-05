import logging
import re
import json
import os
from .base import BaseScraper, classify_room_type

logger = logging.getLogger(__name__)

class ZooplaScraper(BaseScraper):
    def fetch(self, max_rent: int = 2000) -> list[dict]:
        logger.info("🚀 Fetching property data from Zoopla...")
        properties = []
        
        out_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_html_path = os.path.join(out_dir, "zoopla.html")
        has_local = os.path.exists(local_html_path)
        
        page = 1
        while True:
            html = None
            if has_local:
                if page == 1:
                    logger.info(f"📂 Found local '{local_html_path}'. Parsing saved Zoopla HTML to bypass Cloudflare...")
                    try:
                        with open(local_html_path, "r", encoding="utf-8") as f:
                            html = f.read()
                    except Exception as e:
                        logger.error(f"Error reading local 'zoopla.html': {e}")
                else:
                    break # Local fallback only provides page 1
            else:
                url = f"https://www.zoopla.co.uk/to-rent/property/london/?price_max={max_rent}&pn={page}"
                html = self.fetch_html(url)

            if not html:
                if page == 1:
                    logger.warning("⚠️ Zoopla fetch failed. Cloudflare may be blocking GitHub Actions IPs.")
                    logger.info("💡 TIP: Drop a 'zoopla.html' file (saved from browser) into the project folder as a fallback.")
                break

            try:
                next_data_match = re.search(r'<script\b[^>]*id="__NEXT_DATA__"[^>]*>([\s\S]*?)</script>', html)
                if not next_data_match:
                    if page == 1:
                        logger.warning("⚠️ Could not find __NEXT_DATA__ tag in Zoopla HTML.")
                    break
                    
                data = json.loads(next_data_match.group(1))
                props = data.get("props", {})
                page_props = props.get("pageProps", {})
                
                listings = []
                if "data" in page_props and isinstance(page_props["data"], dict):
                    psearch = page_props["data"].get("propertiesSearch", {})
                    if isinstance(psearch, dict):
                        listings = psearch.get("listings", [])
                if not listings and "propertiesSearch" in page_props:
                    psearch = page_props["propertiesSearch"]
                    if isinstance(psearch, dict):
                        listings = psearch.get("listings", [])
                if not listings and "initialProps" in page_props:
                    init_props = page_props["initialProps"]
                    if isinstance(init_props, dict):
                        psearch = init_props.get("propertiesSearch", {})
                        if isinstance(psearch, dict):
                            listings = psearch.get("listings", [])
                            
                if not listings:
                    break
                
                def parse_price(val):
                    if isinstance(val, (int, float)):
                        return int(val)
                    if isinstance(val, str):
                        match = re.search(r'£([\d,]+)', val)
                        if match:
                            return int(match.group(1).replace(',', ''))
                    return 0
                    
                for rp in listings:
                    l_id = rp.get('listingId') or rp.get('id')
                    if not l_id:
                        continue
                        
                    # Parse price
                    price = 0
                    price_val = rp.get('price')
                    if isinstance(price_val, dict):
                        price = parse_price(price_val.get('monthlyRent') or price_val.get('price') or price_val.get('label'))
                    elif price_val:
                        price = parse_price(price_val)
                    if not price:
                        pricing_val = rp.get('pricing')
                        if isinstance(pricing_val, dict):
                            price = parse_price(pricing_val.get('monthlyRent') or pricing_val.get('price') or pricing_val.get('label'))
                        elif pricing_val:
                            price = parse_price(pricing_val)
                            
                    if not price or price > max_rent:
                        continue
                        
                    beds = rp.get('bedrooms') or rp.get('numBedrooms') or rp.get('beds') or 0
                    
                    title = rp.get('title', '').lower()
                    summary = rp.get('description', '').lower()
                    ptype_str = str(rp.get('propertyType', '')).lower()
                    
                    is_stud = 'studio' in title or 'studio' in summary or 'studio' in ptype_str
                    is_room = 'room' in title or 'room' in ptype_str or 'flatshare' in title or 'flat share' in title or 'house share' in title or 'room to rent' in title or 'shared accommodation' in ptype_str
                    
                    prop_type = '1 Bed Flat'
                    if is_stud:
                        prop_type = 'Studio'
                    elif is_room:
                        prop_type = classify_room_type(
                            rp.get('title', ''),
                            rp.get('description', '')
                        )
                    elif beds != 1:
                        continue
                        
                    coords = rp.get('coordinates', {}) or rp.get('location', {}).get('coordinates', {})
                    lat = float(coords.get('lat') or coords.get('latitude') or 0)
                    lng = float(coords.get('lng') or coords.get('lon') or coords.get('longitude') or 0)
                    
                    if not lat or not lng:
                        continue
                        
                    addr = rp.get('address')
                    if isinstance(addr, dict):
                        addr = addr.get('brief') or addr.get('full') or addr.get('displayAddress')
                    if not addr:
                        addr = rp.get('displayAddress') or rp.get('addressText') or 'London, UK'
                        
                    furn_status = 'Unknown'
                    features = rp.get('features', [])
                    for feat in features:
                        feat_lower = feat.lower()
                        if 'unfurnished' in feat_lower:
                            furn_status = 'Unfurnished'
                            break
                        elif 'furnished' in feat_lower:
                            furn_status = 'Furnished'
                            
                    p_url = rp.get('url') or rp.get('listingUrl')
                    if p_url and not p_url.startswith('http'):
                        p_url = f"https://www.zoopla.co.uk{p_url}"
                    if not p_url:
                        p_url = f"https://www.zoopla.co.uk/to-rent/details/{l_id}/"
                        
                    bills_inc = 'bills included' in summary or 'all bills' in summary
                    for feat in features:
                        if 'bills included' in feat.lower() or 'all bills' in feat.lower():
                            bills_inc = True
                            break
                            
                    listing_age = rp.get('addedOrReduced') or rp.get('publishedOn') or 'Active'
                    
                    properties.append({
                        "id": f"zoopla-{l_id}",
                        "price": price,
                        "bedrooms": beds,
                        "is_studio": is_stud,
                        "property_type": prop_type,
                        "lat": lat,
                        "lng": lng,
                        "source": "Zoopla",
                        "address": addr,
                        "url": p_url,
                        "furnished": furn_status,
                        "bills_included": bills_inc,
                        "listing_age": listing_age
                    })
                    
            except Exception as e:
                logger.error(f"Error parsing Zoopla properties on page {page}: {e}")
                break
                
            if page >= 40:
                break
            page += 1
                
        logger.info(f"✅ Zoopla: Extracted {len(properties)} matching properties.")
        return properties
