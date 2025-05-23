import statistics
import numpy as np
from datetime import datetime

class MLAnalyzer:
    """Enhanced ML analysis for actor careers using online data"""
    
    def analyze_career(self, actor):
        """Comprehensive analysis of actor's career"""
        if not actor or not actor.get('movies'):
            return {'error': 'Insufficient data for analysis'}
        
        movies = actor['movies']
        career_years = 2024 - actor.get('career_start', 2000)
        
        # Basic statistics
        ratings = [movie['rating'] for movie in movies if movie['rating'] > 0]
        box_office = [movie['box_office'] for movie in movies if movie['box_office'] > 0]
        years = [movie['year'] for movie in movies if movie['year']]
        
        if not ratings:
            return {'error': 'No rating data available'}
        
        analysis = {
            'career_length': career_years,
            'total_movies': len(movies),
            'avg_rating': round(statistics.mean(ratings), 2),
            'rating_std': round(statistics.stdev(ratings) if len(ratings) > 1 else 0, 2),
            'total_box_office': sum(box_office),
            'avg_box_office': round(statistics.mean(box_office), 1) if box_office else 0,
            'best_movie': max(movies, key=lambda x: x['rating']) if movies else None,
            'highest_grossing': max(movies, key=lambda x: x['box_office']) if box_office else None,
            'career_score': self._calculate_career_score(actor),
            'performance_trend': self._analyze_trend(movies),
            'productivity': self._calculate_productivity(actor),
            'consistency': self._calculate_consistency(ratings),
            'commercial_success': self._calculate_commercial_success(box_office),
            'peak_years': self._find_peak_years(movies),
            'recommendations': self._generate_recommendations(actor)
        }
        
        return analysis
    
    def _calculate_career_score(self, actor):
        """Enhanced career score calculation (0-100)"""
        movies = actor['movies']
        if not movies:
            return 0
        
        # Rating component (40%)
        ratings = [m['rating'] for m in movies if m['rating'] > 0]
        rating_score = (statistics.mean(ratings) / 10 * 100) if ratings else 0
        
        # Box office component (30%)
        box_office = [m['box_office'] for m in movies if m['box_office'] > 0]
        box_office_score = min(sum(box_office) / 50, 100) if box_office else 0
        
        # Longevity component (15%)
        career_years = 2024 - actor.get('career_start', 2000)
        longevity_score = min(career_years * 3, 100)
        
        # Productivity component (10%)
        productivity_score = min(len(movies) * 2, 100)
        
        # Awards component (5%)
        awards_score = min(actor.get('awards', 0) * 10, 100)
        
        # Weighted calculation
        total_score = (
            rating_score * 0.4 +
            box_office_score * 0.3 +
            longevity_score * 0.15 +
            productivity_score * 0.1 +
            awards_score * 0.05
        )
        
        return min(round(total_score, 1), 100)
    
    def _analyze_trend(self, movies):
        """Analyze career trajectory"""
        if len(movies) < 4:
            return "Insufficient data"
        
        # Sort by year and get ratings
        sorted_movies = sorted([m for m in movies if m['year'] and m['rating']], 
                              key=lambda x: x['year'])
        
        if len(sorted_movies) < 4:
            return "Insufficient data"
        
        # Compare recent vs earlier performance
        mid_point = len(sorted_movies) // 2
        recent_ratings = [m['rating'] for m in sorted_movies[mid_point:]]
        earlier_ratings = [m['rating'] for m in sorted_movies[:mid_point]]
        
        recent_avg = statistics.mean(recent_ratings)
        earlier_avg = statistics.mean(earlier_ratings)
        
        # Calculate trend strength
        trend_strength = abs(recent_avg - earlier_avg)
        
        if recent_avg > earlier_avg + 0.4:
            return f"Strongly Trending Up (+{trend_strength:.1f})"
        elif recent_avg > earlier_avg + 0.2:
            return f"Trending Up (+{trend_strength:.1f})"
        elif recent_avg < earlier_avg - 0.4:
            return f"Strongly Trending Down (-{trend_strength:.1f})"
        elif recent_avg < earlier_avg - 0.2:
            return f"Trending Down (-{trend_strength:.1f})"
        else:
            return "Stable Performance"
    
    def _calculate_productivity(self, actor):
        """Calculate actor's productivity rate"""
        career_years = 2024 - actor.get('career_start', 2000)
        total_movies = len(actor.get('movies', []))
        
        if career_years <= 0:
            return 0
        
        movies_per_year = total_movies / career_years
        
        if movies_per_year > 2:
            return "Very High"
        elif movies_per_year > 1.5:
            return "High"
        elif movies_per_year > 1:
            return "Moderate"
        elif movies_per_year > 0.5:
            return "Low"
        else:
            return "Very Low"
    
    def _calculate_consistency(self, ratings):
        """Calculate performance consistency"""
        if len(ratings) < 3:
            return "Insufficient data"
        
        std_dev = statistics.stdev(ratings)
        
        if std_dev < 0.5:
            return "Very Consistent"
        elif std_dev < 1.0:
            return "Consistent"
        elif std_dev < 1.5:
            return "Moderately Consistent"
        else:
            return "Inconsistent"
    
    def _calculate_commercial_success(self, box_office):
        """Analyze commercial success level"""
        if not box_office:
            return "No data available"
        
        total_box_office = sum(box_office)
        avg_box_office = statistics.mean(box_office)
        
        if avg_box_office > 500:
            return "Blockbuster Star"
        elif avg_box_office > 200:
            return "Commercially Successful"
        elif avg_box_office > 100:
            return "Moderate Success"
        elif avg_box_office > 50:
            return "Limited Commercial Appeal"
        else:
            return "Independent/Art House"
    
    def _find_peak_years(self, movies):
        """Identify peak performance years"""
        if not movies:
            return []
        
        # Group movies by year and calculate average rating
        year_ratings = {}
        for movie in movies:
            if movie['year'] and movie['rating']:
                year = movie['year']
                if year not in year_ratings:
                    year_ratings[year] = []
                year_ratings[year].append(movie['rating'])
        
        # Calculate average rating per year
        year_averages = {year: statistics.mean(ratings) 
                        for year, ratings in year_ratings.items()}
        
        # Find top 3 years
        sorted_years = sorted(year_averages.items(), 
                            key=lambda x: x[1], reverse=True)
        
        return [year for year, rating in sorted_years[:3]]
    
    def _generate_recommendations(self, actor):
        """Generate AI-powered recommendations"""
        recommendations = []
        movies = actor.get('movies', [])
        
        if not movies:
            return ["Insufficient data for recommendations"]
        
        ratings = [m['rating'] for m in movies if m['rating'] > 0]
        box_office = [m['box_office'] for m in movies if m['box_office'] > 0]
        
        # Rating-based recommendations
        if ratings:
            avg_rating = statistics.mean(ratings)
            if avg_rating < 7.0:
                recommendations.append("Focus on script quality and work with acclaimed directors")
            elif avg_rating > 8.5:
                recommendations.append("Maintain high standards while exploring diverse roles")
        
        # Commercial performance recommendations
        if box_office:
            avg_box_office = statistics.mean(box_office)
            if avg_box_office < 100:
                recommendations.append("Consider larger budget productions for broader appeal")
            elif avg_box_office > 500:
                recommendations.append("Balance blockbusters with challenging independent films")
        
        # Career stage recommendations
        career_years = 2024 - actor.get('career_start', 2000)
        if career_years < 10:
            recommendations.append("Build diverse portfolio across different genres")
        elif career_years > 25:
            recommendations.append("Consider mentoring roles and producing opportunities")
        
        # Genre diversity
        genres = actor.get('genres', [])
        if len(genres) < 3:
            recommendations.append("Explore different genres to showcase versatility")
        
        return recommendations[:4]  # Limit to top 4 recommendations
    
    def compare_actors(self, actors_data):
        """Compare multiple actors"""
        if len(actors_data) < 2:
            return {'error': 'Need at least 2 actors to compare'}
        
        comparison = {
            'actors': [],
            'metrics_comparison': {},
            'winner_categories': {}
        }
        
        # Analyze each actor
        for actor in actors_data:
            analysis = self.analyze_career(actor)
            comparison['actors'].append({
                'name': actor['name'],
                'analysis': analysis
            })
        
        # Compare key metrics
        metrics = ['career_score', 'avg_rating', 'total_box_office', 'career_length']
        
        for metric in metrics:
            values = []
            for actor in actors_data:
                analysis = self.analyze_career(actor)
                if metric in analysis and isinstance(analysis[metric], (int, float)):
                    values.append({
                        'name': actor['name'],
                        'value': analysis[metric]
                    })
            
            if values:
                # Sort by value
                sorted_values = sorted(values, key=lambda x: x['value'], reverse=True)
                comparison['metrics_comparison'][metric] = sorted_values
                comparison['winner_categories'][metric] = sorted_values[0]['name']
        
        return comparison
    
    def prepare_charts_data(self, actors):
        """Prepare data for visualizations"""
        if not actors:
            return {}
        
        charts_data = {}
        
        # Career progression chart
        for actor in actors:
            movies = actor.get('movies', [])
            if movies:
                # Sort movies by year
                sorted_movies = sorted([m for m in movies if m['year'] and m['rating']], 
                                     key=lambda x: x['year'])
                
                career_progression = []
                for movie in sorted_movies:
                    career_progression.append({
                        'year': movie['year'],
                        'rating': movie['rating'],
                        'title': movie['title'],
                        'box_office': movie.get('box_office', 0)
                    })
                
                charts_data[f"{actor['name']}_progression"] = career_progression
        
        # Box office comparison
        box_office_comparison = []
        for actor in actors:
            movies = actor.get('movies', [])
            total_box_office = sum(m['box_office'] for m in movies if m['box_office'])
            box_office_comparison.append({
                'name': actor['name'],
                'total_box_office': total_box_office,
                'avg_box_office': total_box_office / len(movies) if movies else 0
            })
        
        charts_data['box_office_comparison'] = box_office_comparison
        
        # Rating distribution
        rating_distribution = []
        for actor in actors:
            movies = actor.get('movies', [])
            for movie in movies:
                if movie['rating'] > 0:
                    rating_distribution.append({
                        'actor': actor['name'],
                        'movie': movie['title'],
                        'rating': movie['rating'],
                        'year': movie['year']
                    })
        
        charts_data['rating_distribution'] = rating_distribution
        
        # Career metrics radar chart
        career_metrics = []
        for actor in actors:
            analysis = self.analyze_career(actor)
            if 'error' not in analysis:
                career_metrics.append({
                    'name': actor['name'],
                    'career_score': analysis.get('career_score', 0),
                    'avg_rating': analysis.get('avg_rating', 0) * 10,  # Scale to 0-100
                    'commercial_success': min(analysis.get('total_box_office', 0) / 50, 100),
                    'productivity': self._productivity_to_score(analysis.get('productivity', 'Low')),
                    'consistency': self._consistency_to_score(analysis.get('consistency', 'Inconsistent'))
                })
        
        charts_data['career_metrics'] = career_metrics
        
        return charts_data
    
    def _productivity_to_score(self, productivity_level):
        """Convert productivity level to numerical score"""
        scores = {
            'Very High': 100,
            'High': 80,
            'Moderate': 60,
            'Low': 40,
            'Very Low': 20
        }
        return scores.get(productivity_level, 30)
    
    def _consistency_to_score(self, consistency_level):
        """Convert consistency level to numerical score"""
        scores = {
            'Very Consistent': 100,
            'Consistent': 80,
            'Moderately Consistent': 60,
            'Inconsistent': 30
        }
        return scores.get(consistency_level, 30)
    
    def get_industry_insights(self, actors):
        """Generate industry insights from actor data"""
        if not actors:
            return {}
        
        all_movies = []
        all_ratings = []
        all_box_office = []
        career_lengths = []
        
        for actor in actors:
            movies = actor.get('movies', [])
            all_movies.extend(movies)
            
            ratings = [m['rating'] for m in movies if m['rating'] > 0]
            all_ratings.extend(ratings)
            
            box_office = [m['box_office'] for m in movies if m['box_office'] > 0]
            all_box_office.extend(box_office)
            
            career_length = 2024 - actor.get('career_start', 2000)
            career_lengths.append(career_length)
        
        insights = {}
        
        if all_ratings:
            insights['industry_avg_rating'] = round(statistics.mean(all_ratings), 2)
            insights['rating_benchmark'] = {
                'excellent': 8.5,
                'good': 7.5,
                'average': 6.5,
                'poor': 5.5
            }
        
        if all_box_office:
            insights['industry_avg_box_office'] = round(statistics.mean(all_box_office), 1)
            insights['box_office_benchmarks'] = {
                'blockbuster': 500,
                'successful': 200,
                'moderate': 100,
                'limited': 50
            }
        
        if career_lengths:
            insights['avg_career_length'] = round(statistics.mean(career_lengths), 1)
        
        return insights