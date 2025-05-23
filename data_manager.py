from api_client import APIClient
import re
from datetime import datetime

class DataManager:
    """Manages actor data from online APIs"""
    
    def __init__(self):
        self.api_client = APIClient()
        self.cache = {}  # Simple in-memory cache
    
    def search_actors(self, query):
        """Search for actors online"""
        cache_key = f"search_{query.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Search using TMDB API
        search_results = self.api_client.search_person_tmdb(query)
        
        # Process and clean results
        actors = []
        if 'results' in search_results:
            for person in search_results['results'][:10]:  # Limit to top 10
                actors.append({
                    'id': person.get('id'),
                    'name': person.get('name'),
                    'profile_image': person.get('profile_path'),
                    'popularity': person.get('popularity', 0)
                })
        
        self.cache[cache_key] = actors
        return actors
    
    def get_actor_data(self, actor_name):
        """Get comprehensive actor data from APIs"""
        cache_key = f"actor_{actor_name.lower()}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # First search for the actor
        search_results = self.search_actors(actor_name)
        if not search_results:
            return None
        
        # Get the first matching actor
        actor_info = search_results[0]
        person_id = actor_info['id']
        
        # Get detailed person info from TMDB
        person_details = self.api_client.get_person_details_tmdb(person_id)
        if not person_details:
            return None
        
        # Process the data
        actor_data = self._process_actor_data(person_details)
        
        self.cache[cache_key] = actor_data
        return actor_data
    
    def _process_actor_data(self, person_details):
        """Process raw API data into structured format"""
        # Basic info
        birth_year = None
        if person_details.get('birthday'):
            birth_year = int(person_details['birthday'][:4])
        
        # Process movies
        movies = []
        movie_credits = person_details.get('movie_credits', {}).get('cast', [])
        
        for movie in movie_credits[:15]:  # Limit to recent 15 movies
            if movie.get('title') and movie.get('release_date'):
                # Get additional movie details from OMDB
                year = int(movie['release_date'][:4]) if movie['release_date'] else None
                movie_details = self.api_client.get_movie_details_omdb(movie['title'], year)
                
                # Extract box office (convert to millions)
                box_office = self._extract_box_office(movie_details.get('BoxOffice', 'N/A'))
                
                movies.append({
                    'title': movie['title'],
                    'year': year,
                    'rating': movie.get('vote_average', 0),
                    'box_office': box_office
                })
        
        # Calculate career metrics
        career_start = min([m['year'] for m in movies if m['year']]) if movies else birth_year + 18
        genres = self._extract_genres(movies)
        
        return {
            'id': person_details.get('id'),
            'name': person_details.get('name'),
            'birth_year': birth_year,
            'career_start': career_start,
            'total_movies': len(movies),
            'movies': sorted(movies, key=lambda x: x['year'] or 0, reverse=True),
            'awards': self._estimate_awards(movies),  # Estimated based on ratings
            'genres': genres,
            'biography': person_details.get('biography', ''),
            'place_of_birth': person_details.get('place_of_birth', ''),
            'profile_image': person_details.get('profile_path')
        }
    
    def _extract_box_office(self, box_office_str):
        """Extract box office numbers and convert to millions"""
        if not box_office_str or box_office_str == 'N/A':
            return 0
        
        # Remove currency symbols and commas
        numbers = re.findall(r'[\d,]+', box_office_str)
        if numbers:
            # Convert to integer and then to millions
            amount = int(numbers[0].replace(',', ''))
            return round(amount / 1_000_000, 1)  # Convert to millions
        return 0
    
    def _extract_genres(self, movies):
        """Estimate genres based on movie titles and patterns"""
        # This is a simplified genre extraction
        # In a real app, you'd get this from the API
        common_genres = ['Drama', 'Action', 'Comedy', 'Thriller', 'Romance']
        return common_genres[:3]  # Return first 3 as placeholder
    
    def _estimate_awards(self, movies):
        """Estimate number of awards based on movie ratings"""
        high_rated_movies = [m for m in movies if m['rating'] > 8.0]
        return min(len(high_rated_movies), 5)  # Estimate max 5 major awards
    
    def get_popular_actors(self):
        """Get list of popular actors"""
        cache_key = "popular_actors"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        popular_data = self.api_client.get_popular_actors_tmdb()
        
        actors = []
        if 'results' in popular_data:
            for person in popular_data['results'][:20]:  # Top 20
                actors.append({
                    'id': person.get('id'),
                    'name': person.get('name'),
                    'popularity': person.get('popularity', 0),
                    'profile_image': person.get('profile_path')
                })
        
        self.cache[cache_key] = actors
        return actors
    
    def get_trending_actors(self):
        """Get trending actors (simplified version)"""
        # For demo, return subset of popular actors
        popular = self.get_popular_actors()
        return popular[:10]
    
    def clear_cache(self):
        """Clear the data cache"""
        self.cache.clear()