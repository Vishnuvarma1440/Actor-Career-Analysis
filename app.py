from flask import Flask, render_template, jsonify, request
from data_manager import DataManager
from ml_analyzer import MLAnalyzer
import asyncio

app = Flask(__name__)

# Initialize our components
data_manager = DataManager()
ml_analyzer = MLAnalyzer()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/search-actor')
def search_actor():
    """Search for actors online"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'No search query provided'}), 400
    
    try:
        # Search for actors using the query
        results = data_manager.search_actors(query)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/actor/<actor_name>')
def get_actor_details(actor_name):
    """Get detailed info for specific actor from online sources"""
    try:
        # Fetch actor data from online APIs
        actor_data = data_manager.get_actor_data(actor_name)
        if actor_data:
            # Add ML analysis
            analysis = ml_analyzer.analyze_career(actor_data)
            actor_data['analysis'] = analysis
            return jsonify(actor_data)
        return jsonify({'error': 'Actor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/popular-actors')
def get_popular_actors():
    """Get popular actors from online sources"""
    try:
        popular_actors = data_manager.get_popular_actors()
        return jsonify(popular_actors)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts-data/<actor_name>')
def get_charts_data(actor_name):
    """Get data for charts and visualizations for specific actor"""
    try:
        actor_data = data_manager.get_actor_data(actor_name)
        if actor_data:
            charts_data = ml_analyzer.prepare_charts_data([actor_data])
            return jsonify(charts_data)
        return jsonify({'error': 'Actor not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/compare-actors')
def compare_actors():
    """Compare multiple actors"""
    actor_names = request.args.getlist('actors')
    if len(actor_names) < 2:
        return jsonify({'error': 'Need at least 2 actors to compare'}), 400
    
    try:
        actors_data = []
        for name in actor_names:
            actor_data = data_manager.get_actor_data(name)
            if actor_data:
                actors_data.append(actor_data)
        
        if len(actors_data) < 2:
            return jsonify({'error': 'Could not find enough actors'}), 404
        
        comparison = ml_analyzer.compare_actors(actors_data)
        return jsonify(comparison)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)