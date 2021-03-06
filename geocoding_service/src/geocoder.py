import aiohttp
import asyncio
import json


class GoogleGeocodingClient:

    def __init__(self, api_key):
        self.api_key = api_key

    def _build_uri(self, address, city, state):
        if state.lower() in states:
            state = states[state.lower()]
        elif state.upper() in states.values():
            state = state.upper()
        else:
            raise ValueError('Invalid State input "{}"'.format(state))

        params = {
            'address': ', '.join((address, city, state)).replace(' ', '+'),
            'key': self.api_key
        }

        query_str = '&'.join('{}={}'.format(param, val) for (param, val) in params.items())
        uri = 'https://maps.googleapis.com/maps/api/geocode/json?{}'.format(query_str)
        return uri

    async def _fetch(self, session, uri):
        async with session.get(uri) as response:
            return await response.text()

    async def _geocode_async(self, address, city, state):
        uri = self._build_uri(address, city, state)

        async with aiohttp.ClientSession() as session:
            text = await self._fetch(session, uri)

        data = json.loads(text)

        if data.get('status') == 'OK':
            try:
                return self._format_response_data(data)
            except Exception as e:
                return {
                    'address': address,
                    'city': city,
                    'state': state,
                    'zip_code': None,
                    'latitude': None,
                    'longitude': None
                }
        else:
            return {
                'address': address,
                'city': city,
                'state': state,
                'zip_code': None,
                'latitude': None,
                'longitude': None
            }

    def _format_response_data(self, data):
        results = data.get('results')
        results = list(filter(lambda r: 'street_address' in r.get('types'), results))
        if results:
            street_address = results[0]
        else:
            street_address = data.get('results')[0]

        address_components = street_address.get('address_components')
        street_number = list(filter(lambda c: 'street_number' in c.get('types'), address_components))
        street_number = street_number[0] if street_number else None
        street = list(filter(lambda c: 'route' in c.get('types'), address_components))
        street = street[0] if street else None
        city = list(filter(lambda c: 'locality' in c.get('types'),  address_components))
        city = city[0] if city else None
        state = list(filter(lambda c: 'administrative_area_level_1' in c.get('types'), address_components))
        state = state[0] if state else None
        zip_code = list(filter(lambda c: 'postal_code' in c.get('types'), address_components))
        zip_code = zip_code[0] if zip_code else None

        geometry = street_address.get('geometry')
        location = geometry.get('location') if geometry else None
        latitude = location.get('lat') if location else None
        longitude = location.get('lng') if location else None

        return {
            'address': f"{street_number.get('short_name', '')} {street.get('short_name', '')}".strip(),
            'city': city.get('short_name') if city else None,
            'state': state.get('short_name'),
            'zip_code': zip_code.get('short_name'),
            'latitude': latitude,
            'longitude': longitude
        }

    async def _bulk_geocode_async(self, locations):
        tasks = (self._geocode_async(*loc) for loc in locations)
        return await asyncio.gather(*tasks)

    def geocode(self, address, city, state):
        return asyncio.run(self._geocode_async(address, city, state))

    def bulk_geocode(self, locations):
        return asyncio.run(self._bulk_geocode_async(locations))


states = {
    'alabama': 'AL',
    'alaska': 'AK',
    'arizona': 'AZ',
    'arkansas': 'AR',
    'california': 'CA',
    'colorado': 'CO',
    'connecticut': 'CT',
    'delaware': 'DE',
    'florida': 'FL',
    'georgia': 'GA',
    'hawaii': 'HI',
    'idaho': 'ID',
    'illinois': 'IL',
    'indiana': 'IN',
    'iowa': 'IA',
    'kansas': 'KS',
    'kentucky': 'KY',
    'louisiana': 'LA',
    'maine': 'ME',
    'maryland': 'MD',
    'massachusetts': 'MA',
    'michigan': 'MI',
    'minnesota': 'MN',
    'mississippi': 'MS',
    'missouri': 'MO',
    'montana': 'MT',
    'nebraska': 'NE',
    'nevada': 'NV',
    'new hampshire': 'NH',
    'new jersey': 'NJ',
    'new mexico': 'NM',
    'new york': 'NY',
    'north carolina': 'NC',
    'north dakota': 'ND',
    'ohio': 'OH',
    'oklahoma': 'OK',
    'oregon': 'OR',
    'pennsylvania': 'PA',
    'rhode island': 'RI',
    'south carolina': 'SC',
    'south dakota': 'SD',
    'tennessee': 'TN',
    'texas': 'TX',
    'utah': 'UT',
    'vermont': 'VT',
    'virginia': 'VA',
    'washington': 'WA',
    'west virginia': 'WV',
    'wisconsin': 'WI',
    'wyoming': 'WY'
}
