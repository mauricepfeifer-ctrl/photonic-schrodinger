package main

import (
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/http"
	"os"
	"path/filepath"
	"sort"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// ──────────────────────────────────────────────────────────
// SWARM ENGINE – Reusable Infrastructure for Agent Armies
// ──────────────────────────────────────────────────────────

// Niche represents a content niche with associated keywords.
type Niche struct {
	Name     string
	Keywords []string
}

// SwarmConfig holds all tunable parameters for a swarm run.
type SwarmConfig struct {
	NumAgents      int
	MaxConcurrent  int     // Limit goroutines to prevent system freeze
	ViralThreshold float64 // 0.0–1.0, higher = stricter filter
	OutputDir      string
	EnableAPI      bool
	APIPort        int
}

// DefaultConfig returns a safe, optimized config that won't crash the system.
func DefaultConfig() SwarmConfig {
	return SwarmConfig{
		NumAgents:      10000,
		MaxConcurrent:  500, // Safe limit for M3 chip
		ViralThreshold: 0.995,
		OutputDir:      "swarm_output/candidate_ideas",
		EnableAPI:      false,
		APIPort:        8337,
	}
}

// ──── Agent Strategies ────

// StrategyType defines what kind of content an agent produces.
type StrategyType string

const (
	StrategySales     StrategyType = "sales"
	StrategyContent   StrategyType = "content"
	StrategyResearch  StrategyType = "research"
	StrategyArbitrage StrategyType = "arbitrage"
	StrategyTikTok    StrategyType = "tiktok"
)

// Strategy defines how an agent generates and scores ideas.
type Strategy struct {
	Type       StrategyType
	Niches     []Niche
	Templates  []string
	ScoreBoost float64 // Extra score multiplier for this strategy
}

// BuiltinStrategies returns the full arsenal of content strategies.
func BuiltinStrategies() map[StrategyType]Strategy {
	return map[StrategyType]Strategy{
		StrategySales: {
			Type: StrategySales,
			Niches: []Niche{
				{"B2B SaaS", []string{"AI Automation", "Workflow Optimization", "Cost Reduction", "Scale Operations", "Eliminate Manual Work"}},
				{"Freelance", []string{"AI Consulting", "Chatbot Development", "Data Pipeline", "Content Automation", "Lead Generation"}},
			},
			Templates: []string{
				"How %s Saved Company X $50K/Month",
				"Why Every Business Needs %s in 2025",
				"The ROI of %s: A Case Study",
				"%s: From 0 to $10K MRR in 30 Days",
			},
			ScoreBoost: 1.2,
		},
		StrategyContent: {
			Type: StrategyContent,
			Niches: []Niche{
				{"Money/Success", []string{"Passive Income", "Dropshipping", "Crypto", "Mindset", "Millionaire Habits"}},
				{"AI/Future", []string{"ChatGPT Hacks", "New AI Tools", "Robots", "Automation", "Future Tech"}},
				{"Psychology", []string{"Dark Psychology", "Manipulation", "Body Language", "Attraction", "Influence"}},
			},
			Templates: []string{
				"Why %s is the Key to Freedom",
				"The Dark Truth about %s",
				"I Tried %s for 30 Days – Here's What Happened",
				"%s: What They Don't Want You to Know",
				"Top 5 %s Secrets Nobody Talks About",
			},
			ScoreBoost: 1.0,
		},
		StrategyResearch: {
			Type: StrategyResearch,
			Niches: []Niche{
				{"Market Trends", []string{"AI Market Size", "SaaS Growth", "Remote Work", "Creator Economy", "Web3 Revival"}},
				{"Tech Analysis", []string{"LLM Benchmarks", "Open Source AI", "Edge Computing", "Quantum Computing", "Biotech"}},
			},
			Templates: []string{
				"Deep Dive: The %s Opportunity in 2025",
				"%s Market Analysis: Where's the Money?",
				"Why %s Will Dominate the Next Decade",
			},
			ScoreBoost: 0.8,
		},
		StrategyArbitrage: {
			Type: StrategyArbitrage,
			Niches: []Niche{
				{"Cross-Platform", []string{"TikTok to YouTube", "Reddit to Twitter", "LinkedIn to Newsletter", "Podcast to Shorts", "Blog to Thread"}},
			},
			Templates: []string{
				"Repackage: %s for Maximum Reach",
				"Content Arbitrage: %s Across All Platforms",
				"How to Turn One %s Idea into 10 Pieces of Content",
			},
			ScoreBoost: 1.5,
		},
		StrategyTikTok: {
			Type: StrategyTikTok,
			Niches: []Niche{
				{"Viral Hooks", []string{"Storytime", "POV", "Did You Know", "Life Hack", "Duet This"}},
				{"Trending Audio", []string{"AI Voice", "Original Sound", "Remix", "Voiceover", "ASMR"}},
			},
			Templates: []string{
				"🎬 HOOK: %s (60s Script)",
				"POV: You discovered %s",
				"Wait for it... %s",
				"Nobody talks about %s",
			},
			ScoreBoost: 1.3,
		},
	}
}

// ──── Enhanced Idea with Strategy ────

// SwarmIdea is a richer version of IdeaCandidate with strategy metadata.
type SwarmIdea struct {
	Topic       string       `json:"topic"`
	Niche       string       `json:"niche"`
	Strategy    StrategyType `json:"strategy"`
	ViralScore  float64      `json:"viral_score"`
	Revenue     float64      `json:"estimated_revenue_eur"`
	GeneratedAt time.Time    `json:"generated_at"`
}

// ──── Swarm Metrics ────

// SwarmMetrics tracks live performance counters.
type SwarmMetrics struct {
	TotalAgents    int64
	ActiveAgents   int64
	CompletedTasks int64
	ViralHits      int64
	StartTime      time.Time
	mu             sync.RWMutex
	TopIdeas       []SwarmIdea
}

func NewMetrics() *SwarmMetrics {
	return &SwarmMetrics{
		StartTime: time.Now(),
		TopIdeas:  make([]SwarmIdea, 0, 100),
	}
}

func (m *SwarmMetrics) RecordHit(idea SwarmIdea) {
	atomic.AddInt64(&m.ViralHits, 1)
	m.mu.Lock()
	m.TopIdeas = append(m.TopIdeas, idea)
	m.mu.Unlock()
}

func (m *SwarmMetrics) Snapshot() map[string]interface{} {
	m.mu.RLock()
	defer m.mu.RUnlock()
	elapsed := time.Since(m.StartTime)
	return map[string]interface{}{
		"total_agents":     atomic.LoadInt64(&m.TotalAgents),
		"active_agents":    atomic.LoadInt64(&m.ActiveAgents),
		"completed_tasks":  atomic.LoadInt64(&m.CompletedTasks),
		"viral_hits":       atomic.LoadInt64(&m.ViralHits),
		"elapsed_ms":       elapsed.Milliseconds(),
		"throughput_per_s": float64(atomic.LoadInt64(&m.CompletedTasks)) / math.Max(elapsed.Seconds(), 0.001),
		"top_ideas_count":  len(m.TopIdeas),
	}
}

// ──── Swarm Engine ────

// SwarmEngine orchestrates agents with concurrency limits and metrics.
type SwarmEngine struct {
	Config     SwarmConfig
	Strategies map[StrategyType]Strategy
	Metrics    *SwarmMetrics
	results    chan SwarmIdea
	sem        chan struct{} // Semaphore for concurrency control
}

// NewSwarmEngine creates a ready-to-run engine.
func NewSwarmEngine(cfg SwarmConfig) *SwarmEngine {
	return &SwarmEngine{
		Config:     cfg,
		Strategies: BuiltinStrategies(),
		Metrics:    NewMetrics(),
		results:    make(chan SwarmIdea, cfg.NumAgents),
		sem:        make(chan struct{}, cfg.MaxConcurrent),
	}
}

// Run executes the full swarm and returns top ideas.
func (e *SwarmEngine) Run() []SwarmIdea {
	atomic.StoreInt64(&e.Metrics.TotalAgents, int64(e.Config.NumAgents))
	os.MkdirAll(e.Config.OutputDir, 0755)

	// Optional: Start HTTP API
	if e.Config.EnableAPI {
		go e.startAPI()
	}

	fmt.Println("╔══════════════════════════════════════════════════════════════╗")
	fmt.Println("║  🐝  SWARM ENGINE v2.0 – MAURICE'S AI EMPIRE              ║")
	fmt.Printf("║  📊  Agents: %d | Concurrency: %d                    ║\n", e.Config.NumAgents, e.Config.MaxConcurrent)
	fmt.Printf("║  🎯  Filter: Top %.1f%% | Strategies: %d                    ║\n", (1.0-e.Config.ViralThreshold)*100, len(e.Strategies))
	fmt.Println("╚══════════════════════════════════════════════════════════════╝")

	start := time.Now()
	var wg sync.WaitGroup

	// Distribute agents across strategies
	strategyKeys := make([]StrategyType, 0, len(e.Strategies))
	for k := range e.Strategies {
		strategyKeys = append(strategyKeys, k)
	}

	for i := 0; i < e.Config.NumAgents; i++ {
		wg.Add(1)
		strategy := e.Strategies[strategyKeys[i%len(strategyKeys)]]

		go func(id int, strat Strategy) {
			defer wg.Done()
			e.sem <- struct{}{}        // Acquire slot
			defer func() { <-e.sem }() // Release slot

			atomic.AddInt64(&e.Metrics.ActiveAgents, 1)
			defer atomic.AddInt64(&e.Metrics.ActiveAgents, -1)

			e.runAgent(id, strat)
			atomic.AddInt64(&e.Metrics.CompletedTasks, 1)
		}(i, strategy)
	}

	// Closer
	go func() {
		wg.Wait()
		close(e.results)
	}()

	// Collect results
	var candidates []SwarmIdea
	for idea := range e.results {
		candidates = append(candidates, idea)
	}

	elapsed := time.Since(start)

	// Sort by viral score (descending)
	sort.Slice(candidates, func(i, j int) bool {
		return candidates[i].ViralScore > candidates[j].ViralScore
	})

	// Save batch
	e.saveBatch(candidates)

	// Print results
	fmt.Println("\n╔══════════════════════════════════════════════════════════════╗")
	fmt.Println("║  ✅  SWARM COMPLETE                                        ║")
	fmt.Printf("║  ⏱   Time: %s                                       ║\n", elapsed.Round(time.Millisecond))
	fmt.Printf("║  💎  Viral Hits: %d / %d agents                          ║\n", len(candidates), e.Config.NumAgents)
	fmt.Printf("║  🚀  Throughput: %.0f agents/sec                           ║\n", float64(e.Config.NumAgents)/math.Max(elapsed.Seconds(), 0.001))
	fmt.Println("╚══════════════════════════════════════════════════════════════╝")

	// Print top 10
	if len(candidates) > 0 {
		fmt.Println("\n🏆 TOP IDEAS:")
		limit := 10
		if len(candidates) < limit {
			limit = len(candidates)
		}
		for i := 0; i < limit; i++ {
			c := candidates[i]
			fmt.Printf("  %2d. [%.4f] [%s] %s\n", i+1, c.ViralScore, c.Strategy, c.Topic)
		}
	}

	return candidates
}

// runAgent simulates a single agent's deep search and scoring.
func (e *SwarmEngine) runAgent(id int, strat Strategy) {
	// Simulate processing time (variable based on strategy complexity)
	jitter := time.Duration(rand.Intn(300)+100) * time.Millisecond
	time.Sleep(jitter)

	// Pick random niche and keyword
	niche := strat.Niches[rand.Intn(len(strat.Niches))]
	keyword := niche.Keywords[rand.Intn(len(niche.Keywords))]

	// Generate viral score with strategy boost
	score := rand.NormFloat64()*0.1 + 0.5
	score *= strat.ScoreBoost

	// Trend spikes (5% chance)
	if rand.Float64() < 0.05 {
		score += 0.4
	}

	// Cross-pollination bonus (agents near each other boost scores)
	if id > 0 && id%100 == 0 {
		score += 0.05
	}

	if score > e.Config.ViralThreshold {
		template := strat.Templates[rand.Intn(len(strat.Templates))]
		topic := fmt.Sprintf(template, keyword)

		// Estimate revenue potential
		revenue := score * 97.0 * strat.ScoreBoost

		idea := SwarmIdea{
			Topic:       topic,
			Niche:       niche.Name,
			Strategy:    strat.Type,
			ViralScore:  score,
			Revenue:     revenue,
			GeneratedAt: time.Now(),
		}

		e.results <- idea
		e.Metrics.RecordHit(idea)
	}
}

// saveBatch writes results to a timestamped JSON file.
func (e *SwarmEngine) saveBatch(candidates []SwarmIdea) {
	batchID := time.Now().Format("20060102_150405")
	filename := filepath.Join(e.Config.OutputDir, fmt.Sprintf("swarm_v2_batch_%s.json", batchID))

	output := map[string]interface{}{
		"batch_id":   batchID,
		"config":     e.Config,
		"metrics":    e.Metrics.Snapshot(),
		"candidates": candidates,
	}

	file, err := os.Create(filename)
	if err != nil {
		fmt.Printf("❌ Failed to save batch: %v\n", err)
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	encoder.Encode(output)
	fmt.Printf("💾 Saved to: %s\n", filename)
}

// ──── HTTP API (Optional Live Dashboard) ────

func (e *SwarmEngine) startAPI() {
	mux := http.NewServeMux()

	// GET /metrics – Live swarm metrics
	mux.HandleFunc("/metrics", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		json.NewEncoder(w).Encode(e.Metrics.Snapshot())
	})

	// GET /top – Top viral ideas
	mux.HandleFunc("/top", func(w http.ResponseWriter, r *http.Request) {
		e.Metrics.mu.RLock()
		defer e.Metrics.mu.RUnlock()
		w.Header().Set("Content-Type", "application/json")

		ideas := e.Metrics.TopIdeas
		sort.Slice(ideas, func(i, j int) bool {
			return ideas[i].ViralScore > ideas[j].ViralScore
		})
		limit := 50
		if len(ideas) < limit {
			limit = len(ideas)
		}
		json.NewEncoder(w).Encode(ideas[:limit])
	})

	// GET /health – Health check
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Write([]byte(`{"status":"ok","engine":"swarm_v2"}`))
	})

	addr := fmt.Sprintf(":%d", e.Config.APIPort)
	fmt.Printf("🌐 Swarm API live at http://localhost%s\n", addr)
	http.ListenAndServe(addr, mux)
}

// ──── CLI Runner ────
// This is NOT main() – it's called from production_swarm_main.go or standalone.
// To use standalone, rename RunSwarmCLI to main and remove production_swarm_main.go.

// RunSwarmCLI parses basic flags and runs the swarm.
func RunSwarmCLI() {
	cfg := DefaultConfig()

	// Simple env-based config
	if v := os.Getenv("SWARM_AGENTS"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.NumAgents)
	}
	if v := os.Getenv("SWARM_CONCURRENT"); v != "" {
		fmt.Sscanf(v, "%d", &cfg.MaxConcurrent)
	}
	if strings.ToLower(os.Getenv("SWARM_API")) == "true" {
		cfg.EnableAPI = true
	}

	engine := NewSwarmEngine(cfg)
	engine.Run()
}
