
import json

try:
    from urllib import urlencode
    from urlparse import urlunsplit, urlsplit
except ImportError:
    # Python3
    from urllib.parse import urlunsplit, urlsplit, urlencode
import requests

from starwars_api import settings
from starwars_api.exceptions import SWAPIClientError


class SWAPIClient(object):
    GET_TIMEOUT = 30

    def _call_swapi(self, method, path='', data=None,
                    timeout=None, **params):
        url_parts = urlsplit(settings.BASE_URL)
        scheme = url_parts.scheme
        netloc = url_parts.netloc
        query = urlencode(params)
        url = urlunsplit((scheme, netloc, path, query, ''))

        timeout = timeout or self.GET_TIMEOUT
        try:
            resp = requests.request(method, url, data=data, timeout=timeout)
        except requests.exceptions.ConnectionError:
            msg = 'Could not connect to the SWAPI at {}'.format(url)
            raise SWAPIClientError(msg)
        except requests.exceptions.HTTPError:
            msg = 'Could not connect to SWAPI, got HTTPError'
            raise SWAPIClientError(msg)
        except requests.exceptions.Timeout:
            msg = 'Could not connect to SWAPI, got Timeout'
            raise SWAPIClientError(msg)

        if 400 <= resp.status_code < 500:
            msg = 'Request to SWAPI "{}" failed with status "{}". Reason: {}'
            msg = msg.format(path, resp.status_code, resp.text)
            raise SWAPIClientError(msg)
        elif resp.status_code >= 500:
            msg = ('Request to SWAPI "{}" failed: '
                   '500 Internal Server Error.').format(path)
            raise SWAPIClientError(msg)

        try:
            data = json.loads(resp.content.decode('utf-8'))
        except ValueError:
            msg = ('Request to SWAPI "{}" returned JSON invalid data.'
                   '').format(path)
            raise SWAPIClientError(msg)
        return data

    def _get_swapi(self, path='', **params):
        return self._call_swapi('GET', path, **params)

    def _post_swapi(self, path='', **params):
        raise NotImplementedError()

    def get_people(self, people_id=None, **params):
        if people_id:
            return self._get_swapi('/api/people/{}'.format(people_id))
        return self._get_swapi('/api/people', **params)

    def get_films(self, film_id=None, **params):
        if film_id:
            return self._get_swapi('/api/films/{}'.format(film_id))
        return self._get_swapi('/api/films', **params)
      
    def get_page(self, current_url):
        current_url = current_url.split('http://swapi.co')[1]
        return self._get_swapi(current_url)
