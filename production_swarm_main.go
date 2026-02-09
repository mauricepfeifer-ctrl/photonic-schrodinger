package main

import (
	"encoding/json"
	"fmt"
	"math/rand"
	"os"
	"path/filepath"
	"sync"
	"time"
)

// Configuration
const (
	NUM_AGENTS        = 10000
	VIRAL_THRESHOLD   = 0.999 // Only top 0.1% accepted
	OUTPUT_DIR        = "swarm_output/candidate_ideas"
)

// Data Models
type Niche struct {
	Name     string
	Keywords []string
}

type IdeaCandidate struct {
	Topic       string
	Niche       string
	ViralScore  float64
	GeneratedAt time.Time
}

// Knowledge Base (Built-in for speed)
var Niches = []Niche{
	{"Money/Success", []string{"Passive Income", "Dropshipping", "Crypto", "Mindset", "Millionaire Habits"}},
	{"AI/Future", []string{"ChatGPT Hacks", "New AI Tools", "Robots", "Automation", "Future Tech"}},
	{"Psychology", []string{"Dark Psychology", "Manipulation", "Body Language", "Attraction", "Influence"}},
	{"Health/Biohacking", []string{"Sleep Optimization", "Testosterone", "Focus Hacks", "Dopamine Detox", "Workout"}},
	{"History/Facts", []string{"Crazy Facts", "Ancient Mysteries", "War Stories", "Hidden History", "Conspiracies"}},
}

// Agent Worker
func agentWorker(id int, wg *sync.WaitGroup, results chan<- IdeaCandidate) {
	defer wg.Done()

	// Simulate "Deep Search" time
	time.Sleep(time.Duration(rand.Intn(500)) * time.Millisecond)

	// Pick a random niche and keyword
	niche := Niches[rand.Intn(len(Niches))]
	keyword := niche.Keywords[rand.Intn(len(niche.Keywords))]

	// Generate a random viral score (simulating market demand)
	// Using a normal distribution to make high scores rare
	score := rand.NormFloat64()*0.1 + 0.5 // Mean 0.5, SD 0.1
	// Boost score randomly to simulate "Trends"
	if rand.Float64() < 0.05 {
		score += 0.4 // Viral spike
	}

	// Filter: Only send back if it's a "Viral Hit"
	if score > VIRAL_THRESHOLD {
		topic := fmt.Sprintf("Why %s is the Key to %s", keyword, "Freedom") // Simple template for now
		if rand.Float64() > 0.5 {
			topic = fmt.Sprintf("The Dark Truth about %s", keyword)
		}

		results <- IdeaCandidate{
			Topic:       topic,
			Niche:       niche.Name,
			ViralScore:  score,
			GeneratedAt: time.Now(),
		}
	}
}

func main() {
	rand.Seed(time.Now().UnixNano())
	
	// Create output directory
	os.MkdirAll(OUTPUT_DIR, 0755)

	fmt.Println("========================================")
	fmt.Printf("🐝 10K AGENT SWARM: PRODUCTION MODE\n")
	fmt.Println("========================================")
	fmt.Println("Objective: Mining High-Value Viral Concepts")
	fmt.Printf("Agents: %d\n", NUM_AGENTS)
	fmt.Printf("Filter Strictness: Top %.1f%%\n", (1.0-VIRAL_THRESHOLD)*100)
	fmt.Println("----------------------------------------")

	start := time.Now()
	var wg sync.WaitGroup
	results := make(chan IdeaCandidate, NUM_AGENTS) // Buffer large enough

	// Launch Swarm
	fmt.Println("🚀 Swarm Launching...")
	for i := 0; i < NUM_AGENTS; i++ {
		wg.Add(1)
		go agentWorker(i, &wg, results)
	}

	// Closer routine
	go func() {
		wg.Wait()
		close(results)
	}()

	// Collect Candidates
	var candidates []IdeaCandidate
	for idea := range results {
		candidates = append(candidates, idea)
		// fmt.Printf("💎 Agent found: %s (Score: %.4f)\n", idea.Topic, idea.ViralScore)
	}

	elapsed := time.Since(start)

	// Save Batch
	batchID := time.Now().Format("20060102_150405")
	filename := filepath.Join(OUTPUT_DIR, fmt.Sprintf("batch_%s.json", batchID))
	
	file, _ := os.Create(filename)
	defer file.Close()
	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	encoder.Encode(candidates)

	fmt.Println("----------------------------------------")
	fmt.Printf("✅ BATCH COMPLETE\n")
	fmt.Printf("⏱  Time: %s\n", elapsed)
	fmt.Printf("💎 High-Value Candidates: %d\n", len(candidates))
	fmt.Printf("💾 Saved to: %s\n", filename)
	fmt.Println("========================================")
}
