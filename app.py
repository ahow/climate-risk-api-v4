"""
Climate Risk API V4 - Cloud Deployment
Flask API wrapper for calibrated climate risk assessment
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from climate_risk_processor_v4_cloud import ClimateRiskProcessorV4

app = Flask(__name__)
CORS(app)

# Initialize processor (will download data on first run)
processor = None

def get_processor():
    global processor
    if processor is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'climate_data')
        processor = ClimateRiskProcessorV4(data_dir=data_dir)
    return processor

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'name': 'Climate Risk Assessment API V4',
        'version': '4.0.0',
        'description': 'Calibrated climate risk assessment using 100% real data',
        'data_sources': {
            'hurricanes': 'NOAA IBTrACS (1974-2024, 50 years)',
            'floods': 'WRI Aqueduct Floods v2.0 (100-year return period)',
            'climate_extremes': 'HadEX3 (1901-2018, 118 years)'
        },
        'calibration': 'Calibrated to NOAA historical loss data (Pielke & Landsea 1998)',
        'endpoints': {
            '/assess': 'POST - Comprehensive climate risk assessment',
            '/assess/country': 'POST - Country-level climate risk assessment',
            '/health': 'GET - API health check'
        },
        'example': {
            'endpoint': '/assess',
            'method': 'POST',
            'body': {
                'latitude': 25.76,
                'longitude': -80.19,
                'asset_value': 1000000,
                'building_type': 'wood_frame'
            }
        }
    })

@app.route('/health', methods=['GET'])
def health():
    try:
        proc = get_processor()
        return jsonify({
            'status': 'healthy',
            'hadex3_loaded': len(proc.hadex3_data),
            'flood_lookup_points': len(proc.flood_lookup),
            'hurricane_data': proc.hurricane_data is not None
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/assess', methods=['POST'])
def assess_risk():
    try:
        data = request.get_json()
        
        # Validate required parameters
        if 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'error': 'Missing required parameters: latitude and longitude'
            }), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        asset_value = float(data.get('asset_value', 1000000))
        building_type = data.get('building_type', 'wood_frame')
        
        # Validate ranges
        if not (-90 <= latitude <= 90):
            return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        if not (-180 <= longitude <= 180):
            return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        if asset_value <= 0:
            return jsonify({'error': 'Asset value must be positive'}), 400
        
        # Calculate risk
        proc = get_processor()
        result = proc.calculate_comprehensive_risk(
            latitude, 
            longitude, 
            asset_value=asset_value,
            building_type=building_type
        )
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/assess/country', methods=['POST'])
def assess_country_risk():
    """Assess climate risk for a country using population-weighted coordinates"""
    try:
        data = request.get_json()
        
        if 'country' not in data:
            return jsonify({
                'error': 'Missing required parameter: country'
            }), 400
        
        country = data['country']
        asset_value = float(data.get('asset_value', 1000000))
        building_type = data.get('building_type', 'wood_frame')
        
        # Load country lookup
        country_lookup_path = os.path.join(
            os.path.dirname(__file__), 
            'climate_data', 
            'country_lookup.json'
        )
        
        with open(country_lookup_path, 'r') as f:
            country_lookup = json.load(f)
        
        if country not in country_lookup:
            available_countries = sorted(country_lookup.keys())
            return jsonify({
                'error': f'Country not found: {country}',
                'available_countries': available_countries,
                'total_countries': len(available_countries)
            }), 404
        
        # Get population-weighted coordinates
        country_data = country_lookup[country]
        pop_weighted = country_data['population_weighted']
        
        latitude = pop_weighted['latitude']
        longitude = pop_weighted['longitude']
        location_name = pop_weighted['name']
        
        # Calculate risk for population-weighted location
        proc = get_processor()
        result = proc.calculate_comprehensive_risk(
            latitude, 
            longitude, 
            asset_value=asset_value,
            building_type=building_type
        )
        
        # Add country context to result
        result['country'] = country
        result['assessment_type'] = 'population_weighted'
        result['location'] = {
            'name': location_name,
            'latitude': latitude,
            'longitude': longitude,
            'description': f'Population-weighted center of {country}'
        }
        
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({'error': f'Invalid parameter value: {str(e)}'}), 400
    except FileNotFoundError:
        return jsonify({'error': 'Country lookup data not available'}), 500
    except Exception as e:
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/assess/<risk_type>', methods=['POST'])
def assess_specific_risk(risk_type):
    """Assess a specific risk type"""
    try:
        data = request.get_json()
        
        if 'latitude' not in data or 'longitude' not in data:
            return jsonify({
                'error': 'Missing required parameters: latitude and longitude'
            }), 400
        
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        asset_value = float(data.get('asset_value', 1000000))
        building_type = data.get('building_type', 'wood_frame')
        
        proc = get_processor()
        
        # Route to specific risk calculation
        risk_methods = {
            'hurricane': proc.calculate_hurricane_risk,
            'flood': proc.calculate_flood_risk,
            'heat': proc.calculate_heat_stress_risk,
            'drought': proc.calculate_drought_risk,
            'precipitation': proc.calculate_extreme_precipitation_risk
        }
        
        if risk_type not in risk_methods:
            return jsonify({
                'error': f'Unknown risk type: {risk_type}',
                'available': list(risk_methods.keys())
            }), 400
        
        method = risk_methods[risk_type]
        
        # Call appropriate method
        if risk_type in ['hurricane', 'flood']:
            result = method(latitude, longitude, asset_value, building_type)
        else:
            result = method(latitude, longitude, asset_value)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

