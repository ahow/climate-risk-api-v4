"""
Climate Risk API V4 - Standalone Deployment
Flask API using calibrated climate risk processor with 100% real data
No system library dependencies (uses h5netcdf instead of netCDF4)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from climate_risk_processor_v4_cloud import ClimateRiskProcessorV4

app = Flask(__name__)
CORS(app)

# Initialize processor (singleton)
processor = None

def get_processor():
    global processor
    if processor is None:
        data_dir = os.path.join(os.path.dirname(__file__), 'climate_data')
        processor = ClimateRiskProcessorV4(data_dir=data_dir)
    return processor

@app.route('/', methods=['GET'])
def home():
    """API root - provides information about the API"""
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
        'risk_types': [
            'hurricane',
            'flood',
            'heat_stress',
            'drought',
            'extreme_precipitation'
        ],
        'endpoints': {
            '/': 'GET - API information',
            '/health': 'GET - Health check',
            '/assess': 'POST - Comprehensive climate risk assessment',
            '/assess/<risk_type>': 'POST - Specific risk type assessment'
        },
        'example_request': {
            'url': '/assess',
            'method': 'POST',
            'headers': {'Content-Type': 'application/json'},
            'body': {
                'latitude': 25.76,
                'longitude': -80.19,
                'asset_value': 1000000,
                'building_type': 'wood_frame'
            }
        },
        'example_response': {
            'expected_annual_loss': 13511.37,
            'expected_annual_loss_pct': 1.35,
            'present_value_30yr': 154387.27,
            'present_value_30yr_pct': 15.44
        }
    })

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        proc = get_processor()
        return jsonify({
            'status': 'healthy',
            'version': '4.0.0',
            'data_loaded': {
                'hadex3_indices': len(proc.hadex3_data),
                'flood_lookup_points': len(proc.flood_lookup),
                'hurricane_data_available': proc.hurricane_data is not None
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/assess', methods=['POST'])
def assess_risk():
    """Comprehensive climate risk assessment"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
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
        if building_type not in ['wood_frame', 'concrete', 'residential', 'commercial', 'industrial']:
            return jsonify({'error': f'Invalid building_type: {building_type}'}), 400
        
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Internal error: {str(e)}'}), 500

@app.route('/assess/<risk_type>', methods=['POST'])
def assess_specific_risk(risk_type):
    """Assess a specific risk type"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body must be JSON'}), 400
        
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
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

