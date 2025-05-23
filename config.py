import os

# API Configuration
class Config:
    # TMDB (The Movie Database) - Free API
    TMDB_API_KEY = '961705365938a740dc424c592762ab1b'
    TMDB_BASE_URL = 'https://api.themoviedb.org/3'
    
    # OMDB API - Free tier available
    OMDB_API_KEY ='54502316'
    OMDB_BASE_URL = 'http://www.omdbapi.com'
    
    # Cache settings
    CACHE_TIMEOUT = 3600  # 1 hour in seconds
    
    # Rate limiting
    REQUESTS_PER_SECOND = 2
    
    # Default values for demo (when API keys not available)
    USE_DEMO_DATA = False  # Set to False when you have API keys

# Instructions for getting API keys:
"""
1. TMDB API Key:
   - Go to https://www.themoviedb.org/
   - Create account and request API key
   - Free and widely used

2. OMDB API Key:
   - Go to http://www.omdbapi.com/apikey.aspx
   - Get free key (1000 requests/day)

3. Set environment variables:
   export TMDB_API_KEY=your_key_here
   export OMDB_API_KEY=your_key_here
"""