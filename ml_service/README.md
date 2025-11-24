# ML Prediction Service

Python microservice for serving ML predictions via HTTP API.

## Features

- Housing price predictions (LightGBM model)
- Electricity demand predictions (coming soon)
- RESTful API with JSON responses
- Input validation and error handling
- Health checks
- CORS enabled

## Quick Start

### 1. Install Dependencies

```bash
cd ml_service
pip install -r requirements.txt
```

### 2. Run Server

```bash
python server.py
```

Server will start on `http://localhost:5000`

### 3. Test Service

```bash
# In another terminal
python test_service.py
```

## API Endpoints

### Health Check
```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "ML Prediction Service",
  "housing_model_loaded": true,
  "housing_model_type": "LGBMRegressor"
}
```

### Predict Housing Price
```bash
POST /predict-housing
Content-Type: application/json

{
  "property_type": "T",
  "is_new": "N",
  "duration": "F",
  "county": "GREATER LONDON",
  "year": 2016,
  "month": 6
}
```

Response:
```json
{
  "price": 469050.23,
  "price_log": 13.0587,
  "confidence_lower": 224344.23,
  "confidence_upper": 713756.23,
  "model": "LightGBM",
  "features_used": 11
}
```

### Parameter Reference

| Parameter | Values | Description |
|-----------|--------|-------------|
| `property_type` | D, S, T, F, O | Detached, Semi, Terraced, Flat, Other |
| `is_new` | Y, N | New build or established |
| `duration` | F, L, U | Freehold, Leasehold, Unknown |
| `county` | String | UK county name (uppercase) |
| `year` | 1995-2025 | Year of transfer |
| `month` | 1-12 | Month of transfer |

## Docker

### Build Image
```bash
docker build -t ml-service .
```

### Run Container
```bash
docker run -p 5000:5000 ml-service
```

## Testing

```bash
# Run tests
python test_service.py

# Test with curl
curl -X POST http://localhost:5000/predict-housing \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": "T",
    "is_new": "N",
    "duration": "F",
    "county": "GREATER LONDON",
    "year": 2016,
    "month": 6
  }'
```

## Files

- `predict.py` - Core prediction logic
- `server.py` - Flask API server
- `test_service.py` - Test suite
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration

## Notes

- Model file must be at `../data/clean/best_model.pkl`
- Service runs on port 5000
- Logs all requests for debugging
- Uses gunicorn in production (via Docker)
