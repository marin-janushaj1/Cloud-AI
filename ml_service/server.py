"""
ML Prediction Service - Flask API Server
Exposes ML predictions via HTTP endpoints
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
from predict import get_predictor
from typing import Dict, Any

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize predictor
predictor = get_predictor()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        health_status = predictor.health_check()
        return jsonify({
            "status": "ok",
            "service": "ML Prediction Service",
            **health_status
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route('/predict-housing', methods=['POST'])
def predict_housing():
    """
    Predict UK housing price

    Expected JSON body:
    {
        "property_type": "T",  // D, S, T, F, O
        "is_new": "N",        // Y or N
        "duration": "F",      // F, L, U
        "county": "GREATER LONDON",
        "year": 2016,
        "month": 6
    }
    """
    try:
        # Get request data
        data = request.get_json()

        # Validate required fields
        required_fields = ['property_type', 'is_new', 'duration', 'county', 'year', 'month']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields
            }), 400

        # Validate property_type
        valid_types = ['D', 'S', 'T', 'F', 'O']
        if data['property_type'] not in valid_types:
            return jsonify({
                "error": f"Invalid property_type. Must be one of: {', '.join(valid_types)}"
            }), 400

        # Validate is_new
        if data['is_new'] not in ['Y', 'N']:
            return jsonify({
                "error": "Invalid is_new. Must be 'Y' or 'N'"
            }), 400

        # Validate duration
        valid_durations = ['F', 'L', 'U']
        if data['duration'] not in valid_durations:
            return jsonify({
                "error": f"Invalid duration. Must be one of: {', '.join(valid_durations)}"
            }), 400

        # Validate year range
        if not (1995 <= data['year'] <= 2025):
            return jsonify({
                "error": "Year must be between 1995 and 2025"
            }), 400

        # Validate month
        if not (1 <= data['month'] <= 12):
            return jsonify({
                "error": "Month must be between 1 and 12"
            }), 400

        # Make prediction
        result = predictor.predict_housing(
            property_type=data['property_type'],
            is_new=data['is_new'],
            duration=data['duration'],
            county=data['county'],
            year=data['year'],
            month=data['month']
        )

        logger.info(f"Housing prediction: £{result['price']:,.0f}")
        return jsonify(result), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route('/predict-electricity', methods=['POST'])
def predict_electricity():
    """
    Predict UK electricity demand

    Expected JSON body:
    {
        "year": 2025,
        "month": 1,
        "day": 15,
        "hour": 12  // optional, defaults to 12
    }
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['year', 'month', 'day']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields
            }), 400

        # Optional hour field
        hour = data.get('hour', 12)

        # Validate ranges
        if not (2020 <= data['year'] <= 2030):
            return jsonify({"error": "Year must be between 2020 and 2030"}), 400

        if not (1 <= data['month'] <= 12):
            return jsonify({"error": "Month must be between 1 and 12"}), 400

        if not (1 <= data['day'] <= 31):
            return jsonify({"error": "Day must be between 1 and 31"}), 400

        if not (0 <= hour <= 23):
            return jsonify({"error": "Hour must be between 0 and 23"}), 400

        # Make prediction
        result = predictor.predict_electricity(
            year=data['year'],
            month=data['month'],
            day=data['day'],
            hour=hour
        )

        logger.info(f"Electricity prediction: {result['demand_mw']} MW at {result['datetime']}")
        return jsonify(result), 200

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        return jsonify({
            "error": "Prediction failed",
            "details": str(e)
        }), 500


@app.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    health_status = predictor.health_check()
    return jsonify({
        "available_models": {
            "housing": {
                "status": "available" if health_status['housing_model_loaded'] else "unavailable",
                "endpoint": "/predict-housing",
                "model_type": health_status['housing_model_type']
            },
            "electricity": {
                "status": "available" if health_status['electricity_model_loaded'] else "unavailable",
                "endpoint": "/predict-electricity"
            }
        }
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": [
            "/health",
            "/predict-housing",
            "/predict-electricity",
            "/models"
        ]
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == '__main__':
    # Development server
    import os
    port = int(os.getenv('PORT', '5000'))

    print("\n" + "="*80)
    print("ML PREDICTION SERVICE STARTING")
    print("="*80)
    print(f"\nListening on http://0.0.0.0:{port}")
    print("\nEndpoints:")
    print("  GET  /health              - Health check")
    print("  POST /predict-housing     - Predict UK housing price")
    print("  POST /predict-electricity - Predict UK electricity demand")
    print("  GET  /models              - List available models")
    print("\n" + "="*80 + "\n")

    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
