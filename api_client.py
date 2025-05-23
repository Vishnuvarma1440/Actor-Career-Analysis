import requests
import time
import logging
from config import Config
from functools import lru_cache
from typing import Optional, Dict, Any
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class APIClient:
    """Client for external movie/actor APIs"""

    def __init__(self):
        self.tmdb_api_key = Config.TMDB_API_KEY
        self.omdb_api_key = Config.OMDB_API_KEY
        self.tmdb_base_url = Config.TMDB_BASE_URL
        self.omdb_base_url = Config.OMDB_BASE_URL
        self.last_request_time = 0

    def _rate_limit(self):
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        min_interval = 1.0 / Config.REQUESTS_PER_SECOND
        if time_since_last_request < min_interval:
            time.sleep(min_interval - time_since_last_request)
        self.last_request_time = time.time()

    @lru_cache(maxsize=100)
    def search_person_tmdb(self, name: str) -> Dict[str, Any]:
        if Config.USE_DEMO_DATA or not self.tmdb_api_key:
            return self._get_demo_search_results(name)

        self._rate_limit()
        url = f"{self.tmdb_base_url}/search/person"
        params = {'api_key': self.tmdb_api_key, 'query': name}
        return self._safe_request(url, params, self._get_demo_search_results, name)

    @lru_cache(maxsize=100)
    def get_person_details_tmdb(self, person_id: int) -> Dict[str, Any]:
        if Config.USE_DEMO_DATA or not self.tmdb_api_key:
            return self._get_demo_person_details(person_id)

        self._rate_limit()
        url = f"{self.tmdb_base_url}/person/{person_id}"
        params = {'api_key': self.tmdb_api_key, 'append_to_response': 'movie_credits'}
        return self._safe_request(url, params, self._get_demo_person_details, person_id)

    @lru_cache(maxsize=100)
    def get_movie_details_omdb(self, movie_title: str, year: Optional[int] = None) -> Dict[str, Any]:
        if Config.USE_DEMO_DATA or not self.omdb_api_key:
            return self._get_demo_movie_details(movie_title)

        self._rate_limit()
        params = {'apikey': self.omdb_api_key, 't': movie_title}
        if year:
            params['y'] = year
        return self._safe_request(self.omdb_base_url, params, self._get_demo_movie_details, movie_title)

    def get_popular_actors_tmdb(self, page: int = 1) -> Dict[str, Any]:
        if Config.USE_DEMO_DATA or not self.tmdb_api_key:
            return self._get_demo_popular_actors()

        self._rate_limit()
        url = f"{self.tmdb_base_url}/person/popular"
        params = {'api_key': self.tmdb_api_key, 'page': page}
        return self._safe_request(url, params, self._get_demo_popular_actors)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(requests.RequestException)
    )
    def _safe_request(self, url: str, params: Dict[str, Any], fallback_func, fallback_arg=None) -> Dict[str, Any]:
        print(url)
        print("--------------------------------------------")
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            print("--------------------------------------------------------")
            print(response.json())
            return response.json()
        except requests.HTTPError as http_err:
            logger.error(f"HTTP error: {http_err} | Status Code: {response.status_code}")
        except requests.RequestException as req_err:
            logger.error(f"Request error: {req_err}")
        except Exception as ex:
            logger.exception(f"Unexpected error occurred: {ex}")
        return fallback_func(fallback_arg) if fallback_arg is not None else fallback_func()

    # ---------- Demo Data Methods ----------

    def _get_demo_search_results(self, name: str) -> Dict[str, Any]:
        demo_actors = {
            'leonardo dicaprio': {'id': 1, 'name': 'Leonardo DiCaprio', 'profile_path': None},
            'emma stone': {'id': 2, 'name': 'Emma Stone', 'profile_path': None},
            'ryan gosling': {'id': 3, 'name': 'Ryan Gosling', 'profile_path': None},
            'scarlett johansson': {'id': 4, 'name': 'Scarlett Johansson', 'profile_path': None}
        }
        results = [actor for key, actor in demo_actors.items() if name.lower() in key]
        return {'results': results}

    def _get_demo_person_details(self, person_id: int) -> Dict[str, Any]:
        demo_data = {
            1: {
                'id': 1,
                'name': 'Leonardo DiCaprio',
                'birthday': '1974-11-11',
                'place_of_birth': 'Los Angeles, California, USA',
                'movie_credits': {
                    'cast': [
                        {'title': 'Titanic', 'release_date': '1997-12-19', 'vote_average': 7.9},
                        {'title': 'Inception', 'release_date': '2010-07-16', 'vote_average': 8.8},
                        {'title': 'The Revenant', 'release_date': '2015-12-25', 'vote_average': 8.0},
                        {'title': 'The Wolf of Wall Street', 'release_date': '2013-12-25', 'vote_average': 8.2}
                    ]
                }
            },
            2: {
                'id': 2,
                'name': 'Emma Stone',
                'birthday': '1988-11-06',
                'place_of_birth': 'Scottsdale, Arizona, USA',
                'movie_credits': {
                    'cast': [
                        {'title': 'La La Land', 'release_date': '2016-12-09', 'vote_average': 8.0},
                        {'title': 'Easy A', 'release_date': '2010-09-17', 'vote_average': 7.0},
                        {'title': 'The Help', 'release_date': '2011-08-10', 'vote_average': 8.1},
                        {'title': 'Birdman', 'release_date': '2014-10-17', 'vote_average': 7.7}
                    ]
                }
            }
        }
        return demo_data.get(person_id, {})

    def _get_demo_movie_details(self, title: str) -> Dict[str, Any]:
        demo_movies = {
            'Titanic': {'BoxOffice': '$2,187,463,944', 'imdbRating': '7.9'},
            'Inception': {'BoxOffice': '$829,895,144', 'imdbRating': '8.8'},
            'La La Land': {'BoxOffice': '$448,966,635', 'imdbRating': '8.0'},
            'Easy A': {'BoxOffice': '$75,046,427', 'imdbRating': '7.0'}
        }
        return demo_movies.get(title, {'BoxOffice': 'N/A', 'imdbRating': 'N/A'})

    def _get_demo_popular_actors(self) -> Dict[str, Any]:
        return {
            'results': [
                {'id': 1, 'name': 'Leonardo DiCaprio', 'profile_path': None},
                {'id': 2, 'name': 'Emma Stone', 'profile_path': None},
                {'id': 3, 'name': 'Ryan Gosling', 'profile_path': None},
                {'id': 4, 'name': 'Scarlett Johansson', 'profile_path': None}
            ]
        }
