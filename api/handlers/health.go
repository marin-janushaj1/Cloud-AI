package handlers

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"cloud-ai-api/models"
)

// HealthCheckHandler handles health check requests
func HealthCheckHandler(c *gin.Context) {
	// Check ML service health
	mlHealthy, mlResponse := checkMLServiceHealth()

	status := "healthy"
	if !mlHealthy {
		status = "degraded"
	}

	c.JSON(http.StatusOK, models.HealthResponse{
		Status:            status,
		Service:           "Cloud AI API Gateway",
		Version:           "1.0.0",
		MLServiceHealthy:  mlHealthy,
		MLServiceResponse: mlResponse,
	})
}

// checkMLServiceHealth checks if ML service is responsive
func checkMLServiceHealth() (bool, string) {
	client := http.Client{
		Timeout: 3 * time.Second,
	}

	resp, err := client.Get(fmt.Sprintf("%s/health", MLServiceURL))
	if err != nil {
		return false, fmt.Sprintf("Failed to connect: %s", err.Error())
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return false, fmt.Sprintf("Unhealthy status: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return false, "Failed to read response"
	}

	var healthResp map[string]interface{}
	if err := json.Unmarshal(body, &healthResp); err != nil {
		return false, "Invalid response format"
	}

	return true, "OK"
}
