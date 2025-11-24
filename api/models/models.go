package models

// HousingPredictionRequest represents the request for housing price prediction
type HousingPredictionRequest struct {
	PropertyType string `json:"property_type" binding:"required"`
	IsNew        string `json:"is_new" binding:"required"`
	Duration     string `json:"duration" binding:"required"`
	County       string `json:"county" binding:"required"`
	Year         int    `json:"year" binding:"required"`
	Month        int    `json:"month" binding:"required"`
}

// HousingPredictionResponse represents the response from housing price prediction
type HousingPredictionResponse struct {
	Price             float64 `json:"price"`
	PriceLog          float64 `json:"price_log"`
	ConfidenceLower   float64 `json:"confidence_lower"`
	ConfidenceUpper   float64 `json:"confidence_upper"`
	Model             string  `json:"model"`
	FeaturesUsed      int     `json:"features_used"`
	PredictionTime    string  `json:"prediction_time,omitempty"`
	ProcessingTimeMs  float64 `json:"processing_time_ms,omitempty"`
}

// ErrorResponse represents an error response
type ErrorResponse struct {
	Error   string   `json:"error"`
	Details string   `json:"details,omitempty"`
	Fields  []string `json:"fields,omitempty"`
}

// HealthResponse represents the health check response
type HealthResponse struct {
	Status            string `json:"status"`
	Service           string `json:"service"`
	Version           string `json:"version"`
	MLServiceHealthy  bool   `json:"ml_service_healthy"`
	MLServiceResponse string `json:"ml_service_response,omitempty"`
}

// ElectricityPredictionRequest represents the request for electricity demand prediction
type ElectricityPredictionRequest struct {
	// TODO: Add fields based on electricity model requirements
	Timestamp string  `json:"timestamp"`
	Features  map[string]interface{} `json:"features"`
}

// ElectricityPredictionResponse represents the response from electricity prediction
type ElectricityPredictionResponse struct {
	Demand           float64 `json:"demand"`
	PredictionTime   string  `json:"prediction_time"`
	ProcessingTimeMs float64 `json:"processing_time_ms"`
}
