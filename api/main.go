package main

import (
	"fmt"
	"log"
	"os"

	"github.com/gin-gonic/gin"
	"cloud-ai-api/handlers"
	"cloud-ai-api/middleware"
)

func main() {
	// Get port from environment or use default
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	// Get ML service URL from environment or use default
	mlServiceURL := os.Getenv("ML_SERVICE_URL")
	if mlServiceURL != "" {
		handlers.MLServiceURL = mlServiceURL
	}

	// Set Gin mode (release for production)
	if os.Getenv("GIN_MODE") == "" {
		gin.SetMode(gin.ReleaseMode)
	}

	// Create router
	router := gin.Default()

	// Add middleware
	router.Use(middleware.CORSMiddleware())

	// Print banner
	printBanner(port)

	// Register routes
	v1 := router.Group("/api/v1")
	{
		v1.GET("/health", handlers.HealthCheckHandler)
		v1.POST("/predict/housing", handlers.HousingPredictionHandler)
		v1.POST("/predict/electricity", handlers.ElectricityPredictionHandler)
	}

	// Root route
	router.GET("/", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"service": "Cloud AI API Gateway",
			"version": "1.0.0",
			"endpoints": []string{
				"GET  /api/v1/health",
				"POST /api/v1/predict/housing",
				"POST /api/v1/predict/electricity",
			},
		})
	})

	// Start server
	log.Printf("Server starting on :%s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}

func printBanner(port string) {
	banner := `
================================================================================
  Cloud AI API Gateway - Team Yunus
================================================================================

Service:      API Gateway (Go)
Version:      1.0.0
Port:         %s
ML Service:   %s

Endpoints:
  GET  /                        - Service info
  GET  /api/v1/health           - Health check
  POST /api/v1/predict/housing  - Predict UK housing price
  POST /api/v1/predict/electricity - Predict UK electricity demand

Documentation:
  http://localhost:%s/

================================================================================
`
	fmt.Printf(banner, port, handlers.MLServiceURL, port)
}
