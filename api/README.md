# Cloud AI API Gateway (Go)

Production-ready API gateway written in Go for serving ML predictions.

## Features

- RESTful API with JSON responses
- Forwards requests to Python ML microservice
- Input validation and error handling
- CORS enabled for web access
- Health checks
- Fast and efficient (Go)
- Docker support

## Quick Start

### 1. Install Go Dependencies

```bash
cd api
go mod tidy
go mod download
```

### 2. Run Server

```bash
# Set ML service URL (optional)
export ML_SERVICE_URL=http://localhost:5000

# Run
go run main.go
```

Server will start on `http://localhost:8080`

### 3. Test API

```bash
curl http://localhost:8080/api/v1/health
```

## API Endpoints

### Service Info
```bash
GET /
```

### Health Check
```bash
GET /api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "service": "Cloud AI API Gateway",
  "version": "1.0.0",
  "ml_service_healthy": true
}
```

### Predict Housing Price
```bash
POST /api/v1/predict/housing
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
  "features_used": 11,
  "prediction_time": "2025-11-23T22:00:00Z",
  "processing_time_ms": 45.2
}
```

## Docker

### Build Image
```bash
docker build -t api-gateway .
```

### Run Container
```bash
docker run -p 8080:8080 \
  -e ML_SERVICE_URL=http://ml-service:5000 \
  api-gateway
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | 8080 | Server port |
| `ML_SERVICE_URL` | http://ml-service:5000 | ML service URL |
| `GIN_MODE` | release | Gin framework mode (debug/release) |

## Architecture

```
┌─────────────┐      HTTP      ┌──────────────┐      HTTP      ┌─────────────┐
│   Client    │ ───────────────>│  Go API      │ ───────────────>│   Python    │
│ (Frontend)  │                 │  Gateway     │                 │ ML Service  │
└─────────────┘ <────────────── └──────────────┘ <────────────── └─────────────┘
                   JSON                               JSON
```

The Go API acts as a gateway:
1. Receives client requests
2. Validates input
3. Forwards to Python ML service
4. Returns predictions to client

## Why Go?

- **Fast**: Compiled language, low latency
- **Type-safe**: Compile-time error checking
- **Concurrent**: Handles many requests efficiently
- **Small binary**: ~10MB Docker image
- **Production-ready**: Battle-tested for APIs

## Development

### Run Tests
```bash
go test ./...
```

### Build Binary
```bash
go build -o api-gateway main.go
./api-gateway
```

### Format Code
```bash
go fmt ./...
```

## Files

- `main.go` - Entry point and server setup
- `handlers/` - HTTP request handlers
  - `housing.go` - Housing prediction handler
  - `health.go` - Health check handler
- `models/` - Data structures (request/response)
- `middleware/` - CORS and logging middleware
- `go.mod` - Go dependencies
- `Dockerfile` - Docker configuration

## Example Requests

### Using curl
```bash
# Health check
curl http://localhost:8080/api/v1/health

# Housing prediction
curl -X POST http://localhost:8080/api/v1/predict/housing \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": "F",
    "is_new": "Y",
    "duration": "L",
    "county": "GREATER LONDON",
    "year": 2020,
    "month": 3
  }'
```

### Using JavaScript (fetch)
```javascript
const response = await fetch('http://localhost:8080/api/v1/predict/housing', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    property_type: 'T',
    is_new: 'N',
    duration: 'F',
    county: 'GREATER LONDON',
    year: 2021,
    month: 6
  })
});

const prediction = await response.json();
console.log(`Predicted price: £${prediction.price.toLocaleString()}`);
```

## Notes

- Requires Python ML service to be running
- API validates all input before forwarding
- Returns detailed error messages for invalid input
- CORS enabled for all origins (configure for production)
- Health check verifies ML service connectivity
