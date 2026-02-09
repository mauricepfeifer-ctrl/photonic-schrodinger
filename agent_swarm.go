package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// Configuration
const NUM_AGENTS = 10000
const VIRAL_PROBABILITY = 0.005 // 0.5% chance to find a viral hit

type Agent struct {
	ID int
}

// Agent worker function
func (a *Agent) Run(wg *sync.WaitGroup, results chan<- string) {
	defer wg.Done()

	// Simulate "work" (e.g. scanning TikTok API, analyzing trends)
	// Random latency between 10ms and 100ms
	latency := time.Duration(10+rand.Intn(90)) * time.Millisecond
	time.Sleep(latency)

	// Simulate finding a viral video
	if rand.Float64() < VIRAL_PROBABILITY {
		results <- fmt.Sprintf("Agent %d found a VIRAL GEM! 💎", a.ID)
	}
}

func main() {
	// Seed random number generator
	rand.Seed(time.Now().UnixNano())

	fmt.Println("========================================")
	fmt.Printf("🚀 LAUNCHING %d AGENT SWARM\n", NUM_AGENTS)
	fmt.Println("========================================")
	fmt.Println("Goal: Find viral content candidates...")
	fmt.Println("Status: Spawning goroutines...")
	
	start := time.Now()

	var wg sync.WaitGroup
	results := make(chan string, NUM_AGENTS)

	// Spawn Agents
	for i := 0; i < NUM_AGENTS; i++ {
		wg.Add(1)
		agent := Agent{ID: i + 1}
		go agent.Run(&wg, results)
	}

	// Background monitor to close channel when done
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect Results
	viralCount := 0
	for msg := range results {
		viralCount++
		// Print only first 5 to avoid spam
		if viralCount <= 5 {
			fmt.Println(msg)
		}
	}

	elapsed := time.Since(start)

	fmt.Println("========================================")
	fmt.Printf("✅ MISSION COMPLETE\n")
	fmt.Printf("⏱  Time Elapsed: %s\n", elapsed)
	fmt.Printf("💎 Viral Hits Found: %d\n", viralCount)
	fmt.Printf("⚡️ Speed: %.0f agents/second\n", float64(NUM_AGENTS)/elapsed.Seconds())
	fmt.Println("========================================")
}
