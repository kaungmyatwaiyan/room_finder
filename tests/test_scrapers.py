import json
import os
import tempfile
import unittest
from datetime import date, timedelta
from unittest.mock import patch

from scrapers import OpenRentScraper, RightmoveScraper, OnTheMarketScraper, ZooplaScraper
from main import load_tfl_cache, apply_tfl_cache, deduplicate_properties


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_property(**overrides):
    """Return a minimal valid property dict with sensible defaults."""
    base = {
        "id": "test-1",
        "price": 1200,
        "bedrooms": 1,
        "is_studio": False,
        "property_type": "1 Bed Flat",
        "lat": 51.51,
        "lng": -0.13,
        "source": "OpenRent",
        "address": "Baker Street, London",
        "url": "https://example.com/1",
        "furnished": "Furnished",
        "bills_included": False,
        "listing_age": "Active",
        "sources": [{"source": "OpenRent", "url": "https://example.com/1"}],
        "commute_time": None,
        "station_walk_time": None,
        "is_walk_only": False,
        "tfl_cached_on": "",
        "distance_km": 1.0,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Offline scraper tests  (#12)
# ---------------------------------------------------------------------------

class TestRightmoveOffline(unittest.TestCase):
    """Validates Rightmove parser logic using mock __NEXT_DATA__ HTML."""

    def _make_html(self, props_list):
        data = {"props": {"pageProps": {"searchResults": {"properties": props_list}}}}
        return f'<html><body><script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script></body></html>'

    def _scraper_with_pages(self, scraper, pages):
        """Patch fetch_html to return each page in sequence, then empty string."""
        call_count = [0]

        def side_effect(url):
            idx = call_count[0]
            call_count[0] += 1
            return pages[idx] if idx < len(pages) else ""

        with patch.object(scraper, 'fetch_html', side_effect=side_effect):
            return scraper.fetch(max_rent=2000)

    def test_monthly_price_flat(self):
        raw = [{
            "id": 111, "bedrooms": 1, "propertySubType": "Flat",
            "propertyTypeFullDescription": "1 bed flat", "summary": "Modern flat",
            "keyFeatures": [], "price": {"amount": 1500, "frequency": "monthly"},
            "location": {"latitude": 51.51, "longitude": -0.13},
            "displayAddress": "Baker Street, London",
            "propertyUrl": "/property/111.html", "addedOrReduced": "Added today"
        }]
        scraper = RightmoveScraper()
        props = self._scraper_with_pages(scraper, [self._make_html(raw)])
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['price'], 1500)
        self.assertEqual(props[0]['property_type'], '1 Bed Flat')
        self.assertEqual(props[0]['source'], 'Rightmove')

    def test_weekly_price_converted_to_monthly(self):
        """£400 pw should be converted to £1,733/mo (400 × 52 ÷ 12, rounded)."""
        raw = [{
            "id": 222, "bedrooms": 0, "propertySubType": "Studio",
            "propertyTypeFullDescription": "Studio", "summary": "Cozy studio",
            "keyFeatures": [], "price": {"amount": 400, "frequency": "WEEKLY"},
            "location": {"latitude": 51.52, "longitude": -0.14},
            "displayAddress": "Oxford St, London",
            "propertyUrl": "/property/222.html", "addedOrReduced": "Reduced"
        }]
        scraper = RightmoveScraper()
        props = self._scraper_with_pages(scraper, [self._make_html(raw)])
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['price'], round(400 * 52 / 12))
        self.assertEqual(props[0]['property_type'], 'Studio')

    def test_price_above_max_rent_excluded(self):
        raw = [{
            "id": 333, "bedrooms": 1, "propertySubType": "Flat",
            "propertyTypeFullDescription": "1 bed flat", "summary": "Expensive flat",
            "keyFeatures": [], "price": {"amount": 2500, "frequency": "monthly"},
            "location": {"latitude": 51.51, "longitude": -0.13},
            "displayAddress": "Mayfair, London",
            "propertyUrl": "/property/333.html", "addedOrReduced": "Added today"
        }]
        scraper = RightmoveScraper()
        props = self._scraper_with_pages(scraper, [self._make_html(raw)], )
        self.assertEqual(len(props), 0)

    def test_bills_included_detected_from_key_features(self):
        raw = [{
            "id": 444, "bedrooms": 1, "propertySubType": "Flat",
            "propertyTypeFullDescription": "1 bed flat", "summary": "Nice flat",
            "keyFeatures": [
                {"description": "Furnished"},
                {"description": "Bills included in rent"},
            ],
            "price": {"amount": 1200, "frequency": "monthly"},
            "location": {"latitude": 51.51, "longitude": -0.13},
            "displayAddress": "Camden, London",
            "propertyUrl": "/property/444.html", "addedOrReduced": "Added today"
        }]
        scraper = RightmoveScraper()
        props = self._scraper_with_pages(scraper, [self._make_html(raw)])
        self.assertEqual(len(props), 1)
        self.assertTrue(props[0]['bills_included'])
        self.assertEqual(props[0]['furnished'], 'Furnished')

    def test_multi_bed_flat_excluded(self):
        raw = [{
            "id": 555, "bedrooms": 3, "propertySubType": "Flat",
            "propertyTypeFullDescription": "3 bed flat", "summary": "Large flat",
            "keyFeatures": [], "price": {"amount": 1800, "frequency": "monthly"},
            "location": {"latitude": 51.51, "longitude": -0.13},
            "displayAddress": "Battersea, London",
            "propertyUrl": "/property/555.html", "addedOrReduced": "Added today"
        }]
        scraper = RightmoveScraper()
        props = self._scraper_with_pages(scraper, [self._make_html(raw)])
        self.assertEqual(len(props), 0)


class TestOpenRentOffline(unittest.TestCase):
    """Validates OpenRent inline-JS parser logic using mock HTML."""

    def _make_html(self, ids, prices, bedrooms, isstudio, isshared, lats, lngs,
                   bills=None, furnished=None, unfurnished=None, hours_live=None, addresses=None):
        def arr(name, values):
            items = ", ".join(f"'{v}'" for v in (values or []))
            return f"var {name} = [{items}];"

        return f"""<html><body><script>
            {arr("PROPERTYIDS", ids)}
            {arr("prices", prices)}
            {arr("bedrooms", bedrooms)}
            {arr("isstudio", isstudio)}
            {arr("isshared", isshared)}
            {arr("PROPERTYLISTLATITUDES", lats)}
            {arr("PROPERTYLISTLONGITUDES", lngs)}
            {arr("bills", bills or ['0'] * len(ids))}
            {arr("furnished", furnished or ['0'] * len(ids))}
            {arr("unfurnished", unfurnished or ['0'] * len(ids))}
            {arr("hoursLive", hours_live or ['24'] * len(ids))}
            {arr("PROPERTYLISTADDRESSES", addresses) if addresses else ''}
        </script></body></html>"""

    def test_basic_parsing(self):
        html = self._make_html(
            ids=['101'], prices=['1100'], bedrooms=['1'],
            isstudio=['0'], isshared=['0'],
            lats=['51.51'], lngs=['-0.13'],
            furnished=['1'], bills=['1'],
        )
        scraper = OpenRentScraper()
        with patch.object(scraper, 'fetch_html', return_value=html):
            props = scraper.fetch(max_rent=2000)
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['price'], 1100)
        self.assertEqual(props[0]['source'], 'OpenRent')
        self.assertTrue(props[0]['bills_included'])
        self.assertEqual(props[0]['furnished'], 'Furnished')

    def test_address_extracted_when_available(self):
        html = self._make_html(
            ids=['202'], prices=['900'], bedrooms=['0'],
            isstudio=['1'], isshared=['0'],
            lats=['51.52'], lngs=['-0.14'],
            addresses=['Shoreditch, London'],
        )
        scraper = OpenRentScraper()
        with patch.object(scraper, 'fetch_html', return_value=html):
            props = scraper.fetch(max_rent=2000)
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['address'], 'Shoreditch, London')

    def test_address_falls_back_to_london(self):
        """When no address variable is present, address should be 'London, UK'."""
        html = self._make_html(
            ids=['303'], prices=['1200'], bedrooms=['1'],
            isstudio=['0'], isshared=['0'],
            lats=['51.53'], lngs=['-0.15'],
        )
        scraper = OpenRentScraper()
        with patch.object(scraper, 'fetch_html', return_value=html):
            props = scraper.fetch(max_rent=2000)
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['address'], 'London, UK')

    def test_price_above_max_excluded(self):
        html = self._make_html(
            ids=['404'], prices=['2500'], bedrooms=['1'],
            isstudio=['0'], isshared=['0'],
            lats=['51.51'], lngs=['-0.13'],
        )
        scraper = OpenRentScraper()
        with patch.object(scraper, 'fetch_html', return_value=html):
            props = scraper.fetch(max_rent=2000)
        self.assertEqual(len(props), 0)

    def test_multi_bed_excluded(self):
        html = self._make_html(
            ids=['505'], prices=['1800'], bedrooms=['2'],
            isstudio=['0'], isshared=['0'],
            lats=['51.51'], lngs=['-0.13'],
        )
        scraper = OpenRentScraper()
        with patch.object(scraper, 'fetch_html', return_value=html):
            props = scraper.fetch(max_rent=2000)
        self.assertEqual(len(props), 0)


class TestOnTheMarketOffline(unittest.TestCase):
    """Validates OnTheMarket __NEXT_DATA__ parser logic using mock HTML."""

    def _make_html(self, listings):
        data = {
            "props": {
                "initialReduxState": {
                    "results": {"list": listings}
                }
            }
        }
        return (
            f'<html><body>'
            f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script>'
            f'</body></html>'
        )

    def _fetch_pages(self, scraper, pages):
        call_count = [0]

        def side_effect(url):
            idx = call_count[0]
            call_count[0] += 1
            return pages[idx] if idx < len(pages) else ""

        with patch.object(scraper, 'fetch_html', side_effect=side_effect):
            return scraper.fetch(max_rent=2000)

    def test_pcm_price_parsed(self):
        listing = {
            "id": "otm-1", "bedrooms": 1,
            "property-title": "1 bed flat to rent",
            "humanised-property-type": "flat",
            "price": "£1,200 pcm",
            "location": {"lat": 51.51, "lon": -0.13},
            "address": "Marylebone, London",
            "details-url": "/to-rent/details/otm-1/",
            "features": ["Furnished"],
            "days-since-added-reduced": "Added today"
        }
        scraper = OnTheMarketScraper()
        props = self._fetch_pages(scraper, [self._make_html([listing])])
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['price'], 1200)
        self.assertEqual(props[0]['furnished'], 'Furnished')

    def test_pw_price_converted_to_monthly(self):
        listing = {
            "id": "otm-2", "bedrooms": 0,
            "property-title": "studio flat",
            "humanised-property-type": "studio",
            "price": "£350 pw",
            "location": {"lat": 51.52, "lon": -0.14},
            "address": "Soho, London",
            "details-url": "/to-rent/details/otm-2/",
            "features": [],
            "days-since-added-reduced": "Reduced"
        }
        scraper = OnTheMarketScraper()
        props = self._fetch_pages(scraper, [self._make_html([listing])])
        self.assertEqual(len(props), 1)
        self.assertEqual(props[0]['price'], round(350 * 52 / 12))
        self.assertEqual(props[0]['property_type'], 'Studio')

    def test_bills_included_detected_from_features(self):
        listing = {
            "id": "otm-3", "bedrooms": 1,
            "property-title": "1 bed flat",
            "humanised-property-type": "flat",
            "price": "£1,100 pcm",
            "location": {"lat": 51.51, "lon": -0.13},
            "address": "Islington, London",
            "details-url": "/to-rent/details/otm-3/",
            "features": ["Furnished", "All bills included"],
            "days-since-added-reduced": "Active"
        }
        scraper = OnTheMarketScraper()
        props = self._fetch_pages(scraper, [self._make_html([listing])])
        self.assertEqual(len(props), 1)
        self.assertTrue(props[0]['bills_included'])

    def test_no_price_match_excluded(self):
        listing = {
            "id": "otm-4", "bedrooms": 1,
            "property-title": "1 bed flat",
            "humanised-property-type": "flat",
            "price": "Price on application",
            "location": {"lat": 51.51, "lon": -0.13},
            "address": "Chelsea, London",
            "details-url": "/to-rent/details/otm-4/",
            "features": [], "days-since-added-reduced": "Active"
        }
        scraper = OnTheMarketScraper()
        props = self._fetch_pages(scraper, [self._make_html([listing])])
        self.assertEqual(len(props), 0)


class TestZooplaOffline(unittest.TestCase):
    """Offline tests for the Zoopla scraper (pre-existing, expanded)."""

    def test_zoopla_parser_offline(self):
        mock_data = {
            "props": {
                "pageProps": {
                    "data": {
                        "propertiesSearch": {
                            "listings": [
                                {
                                    "listingId": "111111",
                                    "price": 1300,
                                    "bedrooms": 1,
                                    "title": "Stunning 1 bed flat to rent",
                                    "description": "A beautiful modern flat.",
                                    "propertyType": "flat",
                                    "coordinates": {"lat": 51.5074, "lon": -0.1278},
                                    "address": "Baker Street, London",
                                    "features": ["Furnished", "All bills included"],
                                    "url": "/to-rent/details/111111/",
                                    "addedOrReduced": "Added today"
                                },
                                {
                                    "listingId": "222222",
                                    "price": {"monthlyRent": 950},
                                    "bedrooms": 0,
                                    "title": "Cozy Studio Flat",
                                    "description": "Compact studio.",
                                    "propertyType": "studio",
                                    "coordinates": {"lat": 51.5152, "lon": -0.1419},
                                    "address": "Oxford Street, London",
                                    "features": ["Unfurnished"],
                                    "url": "/to-rent/details/222222/",
                                    "addedOrReduced": "2 days ago"
                                }
                            ]
                        }
                    }
                }
            }
        }
        mock_html = (
            f'<html><body>'
            f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(mock_data)}</script>'
            f'</body></html>'
        )
        scraper = ZooplaScraper()

        def fetch_side_effect(url):
            return mock_html if "pn=1" in url else ""

        with patch.object(scraper, 'fetch_html', side_effect=fetch_side_effect):
            with patch('scrapers.zoopla.os.path.exists', return_value=False):
                props = scraper.fetch(max_rent=1500)

        self.assertEqual(len(props), 2)
        p1 = props[0]
        self.assertEqual(p1['id'], 'zoopla-111111')
        self.assertEqual(p1['price'], 1300)
        self.assertEqual(p1['property_type'], '1 Bed Flat')
        self.assertEqual(p1['furnished'], 'Furnished')
        self.assertTrue(p1['bills_included'])

        p2 = props[1]
        self.assertEqual(p2['id'], 'zoopla-222222')
        self.assertEqual(p2['price'], 950)
        self.assertEqual(p2['property_type'], 'Studio')
        self.assertEqual(p2['furnished'], 'Unfurnished')
        self.assertFalse(p2['bills_included'])


# ---------------------------------------------------------------------------
# Pipeline function tests  (#13)
# ---------------------------------------------------------------------------

class TestDeduplicateProperties(unittest.TestCase):
    """Unit tests for the deduplicate_properties function."""

    def test_same_location_same_price_merged(self):
        p1 = make_property(id="openrent-1",  source="OpenRent",  lat=51.5100, lng=-0.1300, price=1200,
                           sources=[{"source": "OpenRent",  "url": "https://openrent.co.uk/1"}])
        p2 = make_property(id="rightmove-1", source="Rightmove", lat=51.5100, lng=-0.1300, price=1205,
                           sources=[{"source": "Rightmove", "url": "https://rightmove.co.uk/1"}])
        result = deduplicate_properties([p1, p2])
        self.assertEqual(len(result), 1)
        sources = {s['source'] for s in result[0]['sources']}
        self.assertIn("OpenRent", sources)
        self.assertIn("Rightmove", sources)

    def test_source_priority_openrent_wins(self):
        """When two listings are the same property, OpenRent's data takes precedence."""
        p_rm  = make_property(id="rightmove-2", source="Rightmove", lat=51.51, lng=-0.13, price=1300,
                              sources=[{"source": "Rightmove", "url": "r"}])
        p_or  = make_property(id="openrent-2",  source="OpenRent",  lat=51.51, lng=-0.13, price=1300,
                              sources=[{"source": "OpenRent",  "url": "o"}])
        result = deduplicate_properties([p_rm, p_or])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['source'], 'OpenRent')

    def test_different_location_both_kept(self):
        p1 = make_property(id="openrent-3", lat=51.5000, lng=-0.1000, price=1200,
                           sources=[{"source": "OpenRent", "url": "a"}])
        p2 = make_property(id="openrent-4", lat=51.5500, lng=-0.1500, price=1200,
                           sources=[{"source": "OpenRent", "url": "b"}])
        result = deduplicate_properties([p1, p2])
        self.assertEqual(len(result), 2)

    def test_same_location_big_price_diff_both_kept(self):
        p1 = make_property(id="openrent-5", lat=51.51, lng=-0.13, price=1000,
                           sources=[{"source": "OpenRent", "url": "c"}])
        p2 = make_property(id="openrent-6", lat=51.51, lng=-0.13, price=1500,
                           sources=[{"source": "OpenRent", "url": "d"}])
        result = deduplicate_properties([p1, p2])
        self.assertEqual(len(result), 2)

    def test_sources_list_populated_on_new_property(self):
        """A property without a pre-built sources list gets one added automatically."""
        p = make_property(id="openrent-7", source="OpenRent", url="https://x.com")
        del p['sources']
        result = deduplicate_properties([p])
        self.assertEqual(len(result), 1)
        self.assertIn('sources', result[0])
        self.assertEqual(result[0]['sources'][0]['source'], 'OpenRent')


class TestLoadTflCache(unittest.TestCase):
    """Unit tests for load_tfl_cache."""

    def test_returns_empty_dict_when_file_missing(self):
        cache = load_tfl_cache("/nonexistent/path/properties.json")
        self.assertEqual(cache, {})

    def test_loads_valid_entries(self):
        data = [
            {
                "lat": 51.51, "lng": -0.13,
                "commute_time": 15, "station_walk_time": 5, "is_walk_only": False,
                "tfl_cached_on": date.today().isoformat()
            },
            {
                "lat": 51.52, "lng": -0.14,
                "commute_time": None  # should be excluded
            }
        ]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            fname = f.name
        try:
            cache = load_tfl_cache(fname)
            self.assertEqual(len(cache), 1)
            key = (round(51.51, 4), round(-0.13, 4))
            self.assertIn(key, cache)
            self.assertEqual(cache[key]['commute_time'], 15)
        finally:
            os.unlink(fname)

    def test_expired_entries_excluded(self):
        """Entries older than TFL_CACHE_TTL_DAYS should not be loaded into the cache."""
        old_date = (date.today() - timedelta(days=35)).isoformat()
        data = [{
            "lat": 51.51, "lng": -0.13,
            "commute_time": 20, "station_walk_time": 3, "is_walk_only": False,
            "tfl_cached_on": old_date
        }]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            fname = f.name
        try:
            cache = load_tfl_cache(fname)
            self.assertEqual(len(cache), 0)
        finally:
            os.unlink(fname)

    def test_entry_without_cached_on_excluded(self):
        """Entries with no tfl_cached_on date are treated as having unknown age — excluded."""
        data = [{
            "lat": 51.51, "lng": -0.13,
            "commute_time": 10, "station_walk_time": 2, "is_walk_only": False,
            # deliberately no "tfl_cached_on"
        }]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(data, f)
            fname = f.name
        try:
            cache = load_tfl_cache(fname)
            self.assertEqual(len(cache), 0)
        finally:
            os.unlink(fname)

    def test_returns_empty_on_malformed_json(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{{")
            fname = f.name
        try:
            cache = load_tfl_cache(fname)
            self.assertEqual(cache, {})
        finally:
            os.unlink(fname)


class TestApplyTflCache(unittest.TestCase):
    """Unit tests for apply_tfl_cache."""

    def test_cache_hit_applies_data(self):
        today = date.today().isoformat()
        cache = {
            (51.51, -0.13): {
                "commute_time": 12, "station_walk_time": 4,
                "is_walk_only": False, "tfl_cached_on": today,
            }
        }
        props = [make_property(lat=51.51, lng=-0.13)]
        result, misses, hits = apply_tfl_cache(props, cache)
        self.assertEqual(hits, 1)
        self.assertEqual(len(misses), 0)
        self.assertEqual(result[0]['commute_time'], 12)

    def test_cache_miss_added_to_misses(self):
        cache = {}
        props = [make_property(lat=99.0, lng=99.0)]
        result, misses, hits = apply_tfl_cache(props, cache)
        self.assertEqual(hits, 0)
        self.assertEqual(len(misses), 1)
        self.assertIsNone(result[0]['commute_time'])


# ---------------------------------------------------------------------------
# Live integration tests (not run in CI)
# ---------------------------------------------------------------------------

class TestScrapersLive(unittest.TestCase):
    """Live integration tests that hit real websites.
    Slow, non-deterministic — do NOT use to gate CI.
    Run manually: python -m unittest tests.test_scrapers.TestScrapersLive
    """

    def setUp(self):
        self.max_rent = 1500

    def _check_format(self, prop, source_name):
        self.assertIn('id', prop)
        self.assertIn('price', prop)
        self.assertIn('lat', prop)
        self.assertIn('lng', prop)
        self.assertEqual(prop['source'], source_name)
        self.assertIsInstance(prop['price'], int)
        self.assertIsInstance(prop['lat'], float)
        self.assertIsInstance(prop['lng'], float)

    def test_openrent_scraper(self):
        props = OpenRentScraper().fetch(max_rent=self.max_rent)
        self.assertGreater(len(props), 500)
        for p in props[:10]:
            self._check_format(p, "OpenRent")

    def test_rightmove_scraper(self):
        props = RightmoveScraper().fetch(max_rent=self.max_rent)
        self.assertGreater(len(props), 20)
        for p in props[:10]:
            self._check_format(p, "Rightmove")

    def test_onthemarket_scraper(self):
        props = OnTheMarketScraper().fetch(max_rent=self.max_rent)
        self.assertGreater(len(props), 20)
        for p in props[:10]:
            self._check_format(p, "OnTheMarket")

    def test_zoopla_scraper(self):
        props = ZooplaScraper().fetch(max_rent=self.max_rent)
        if len(props) == 0:
            print("⚠️ Zoopla returned 0 properties — likely Cloudflare block.")
        else:
            self.assertGreater(len(props), 10)
            for p in props[:10]:
                self._check_format(p, "Zoopla")


if __name__ == '__main__':
    unittest.main()
