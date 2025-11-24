package handlers

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"cloud-ai-api/models"
)

// MLServiceURL is the URL of the Python ML service
var MLServiceURL = "http://ml-service:5000"

// HousingPredictionHandler handles housing price prediction requests
func HousingPredictionHandler(c *gin.Context) {
	startTime := time.Now()

	// Parse request
	var req models.HousingPredictionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid request format",
			Details: err.Error(),
		})
		return
	}

	// Validate property type
	validTypes := map[string]bool{"D": true, "S": true, "T": true, "F": true, "O": true}
	if !validTypes[req.PropertyType] {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid property type",
			Details: "Must be one of: D, S, T, F, O",
		})
		return
	}

	// Validate is_new
	if req.IsNew != "Y" && req.IsNew != "N" {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid is_new value",
			Details: "Must be 'Y' or 'N'",
		})
		return
	}

	// Validate duration
	validDurations := map[string]bool{"F": true, "L": true, "U": true}
	if !validDurations[req.Duration] {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid duration",
			Details: "Must be one of: F, L, U",
		})
		return
	}

	// Validate year
	if req.Year < 1995 || req.Year > 2025 {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid year",
			Details: "Must be between 1995 and 2025",
		})
		return
	}

	// Validate month
	if req.Month < 1 || req.Month > 12 {
		c.JSON(http.StatusBadRequest, models.ErrorResponse{
			Error:   "Invalid month",
			Details: "Must be between 1 and 12",
		})
		return
	}

	// Forward request to ML service
	mlResp, err := callMLService(req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, models.ErrorResponse{
			Error:   "ML service error",
			Details: err.Error(),
		})
		return
	}

	// Add processing time
	mlResp.ProcessingTimeMs = float64(time.Since(startTime).Milliseconds())
	mlResp.PredictionTime = time.Now().Format(time.RFC3339)

	c.JSON(http.StatusOK, mlResp)
}

// callMLService makes HTTP request to Python ML service
func callMLService(req models.HousingPredictionRequest) (*models.HousingPredictionResponse, error) {
	// Prepare request body
	reqBody, err := json.Marshal(req)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	// Make HTTP request
	resp, err := http.Post(
		fmt.Sprintf("%s/predict-housing", MLServiceURL),
		"application/json",
		bytes.NewBuffer(reqBody),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to call ML service: %w", err)
	}
	defer resp.Body.Close()

	// Read response body
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	// Check status code
	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("ML service returned status %d: %s", resp.StatusCode, string(body))
	}

	// Parse response
	var mlResp models.HousingPredictionResponse
	if err := json.Unmarshal(body, &mlResp); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &mlResp, nil
}

// ElectricityPredictionHandler handles electricity demand prediction requests
func ElectricityPredictionHandler(c *gin.Context) {
	c.JSON(http.StatusNotImplemented, models.ErrorResponse{
		Error: "Electricity prediction not yet implemented",
	})
}
