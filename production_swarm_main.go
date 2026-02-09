package main

import (
	"fmt"
	"os"
)

// production_swarm_main.go – Entry point for the Swarm Engine v2.0
//
// Usage:
//   go run *.go                           # Default: 10K agents, 500 concurrent
//   SWARM_AGENTS=50000 go run *.go        # 50K agents
//   SWARM_API=true go run *.go            # Enable live HTTP API on :8337
//   SWARM_CONCURRENT=200 go run *.go      # Limit to 200 goroutines

func main() {
	fmt.Println("========================================")
	fmt.Println("🏰 MAURICE'S AI EMPIRE – SWARM ENGINE")
	fmt.Println("========================================")

	// Use the Swarm Engine v2.0 from agent_swarm.go
	cfg := DefaultConfig()

	// Override from env
	if v := os.Getenv("SWARM_AGENTS"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.NumAgents)
	}
	if v := os.Getenv("SWARM_CONCURRENT"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.MaxConcurrent)
	}
	if os.Getenv("SWARM_API") == "true" {
		cfg.EnableAPI = true
	}

	engine := NewSwarmEngine(cfg)
	candidates := engine.Run()

	// Summary
	totalRevenue := 0.0
	for _, c := range candidates {
		totalRevenue += c.Revenue
	}

	fmt.Printf("\n💰 Total Estimated Revenue Potential: EUR %.2f\n", totalRevenue)
	fmt.Println("========================================")
}
