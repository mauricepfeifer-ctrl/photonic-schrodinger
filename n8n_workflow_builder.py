#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🔥 N8N WORKFLOW BUILDER — ALL EMPIRE PROCESSES VISUALIZED 🔥     ║
║                                                                      ║
║   Creates ALL n8n workflows for every AI Empire process:             ║
║     1. 🎯 Kimi Swarm Pipeline                                       ║
║     2. 💰 Revenue Tracker                                            ║
║     3. 📢 Content Blitz → Auto-Post                                 ║
║     4. 🕵️ Sales Force Outreach                                      ║
║     5. 👻 Ghost Squadron Ops                                         ║
║     6. 📈 Empire Nucleus Heartbeat                                   ║
║     7. 🧠 Brain Decision Logger                                     ║
║     8. 💳 Stripe Webhook Processor                                   ║
║     9. 📹 YouTube Automation                                         ║
║    10. 🐦 X Monster Auto-Post                                       ║
║                                                                      ║
║   Uses n8n REST API to create workflows programmatically.            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import json
import os
import sys
from datetime import datetime

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# ═══════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════
N8N_BASE_URL = os.getenv("N8N_API_URL", "https://ai1337empire.app.n8n.cloud/api/v1")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    "X-N8N-API-KEY": N8N_API_KEY,
}


def create_workflow(name: str, nodes: list, connections: dict, active: bool = False) -> dict:
    """Create a single n8n workflow via API."""
    payload = {
        "name": name,
        "nodes": nodes,
        "connections": connections,
        "active": active,
        "settings": {
            "executionOrder": "v1"
        }
    }
    return payload


# ═══════════════════════════════════════════════════════
# WORKFLOW 1: KIMI SWARM RECEIVER
# Catches all task results from the Mega Swarm
# ═══════════════════════════════════════════════════════
def wf_kimi_swarm_receiver():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "empire-swarm/task_completed",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-swarm",
            "name": "🔥 Swarm Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {
                        "caseSensitive": True,
                        "leftValue": "",
                        "typeValidation": "strict"
                    },
                    "conditions": [
                        {
                            "id": "cond-sales",
                            "leftValue": "={{ $json.department }}",
                            "rightValue": "sales",
                            "operator": {
                                "type": "string",
                                "operation": "equals"
                            }
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "switch-dept",
            "name": "🏢 Route by Dept",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [500, 300]
        },
        {
            "parameters": {
                "jsCode": """// Categorize & Enrich
const item = $input.first().json;

const enriched = {
  ...item,
  processed_at: new Date().toISOString(),
  category: item.department || 'unknown',
  revenue_formatted: `€${(item.revenue_eur || 0).toFixed(2)}`,
  is_high_value: (item.revenue_eur || 0) > 5,
  summary: `[${(item.department || 'UNK').toUpperCase()}] ${item.type}: €${(item.revenue_eur || 0).toFixed(2)}`
};

return [{json: enriched}];"""
            },
            "id": "code-enrich",
            "name": "🧠 Enrich Data",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 520]
        },
        {
            "parameters": {
                "operation": "appendOrUpdate",
                "documentId": { "__rl": True, "value": "", "mode": "list" },
                "sheetName": { "__rl": True, "value": "", "mode": "list" },
                "columns": {
                    "mappingMode": "autoMapInputData",
                    "value": {}
                },
                "options": {}
            },
            "id": "sheets-log",
            "name": "📊 Log to Sheets",
            "type": "n8n-nodes-base.googleSheets",
            "typeVersion": 4.5,
            "position": [750, 520]
        }
    ]
    
    connections = {
        "🔥 Swarm Webhook": {
            "main": [[
                {"node": "🏢 Route by Dept", "type": "main", "index": 0},
                {"node": "🧠 Enrich Data", "type": "main", "index": 0}
            ]]
        },
        "🧠 Enrich Data": {
            "main": [[
                {"node": "📊 Log to Sheets", "type": "main", "index": 0}
            ]]
        }
    }
    
    return create_workflow("🔥 Kimi Swarm Receiver", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 2: REVENUE DASHBOARD
# Periodically checks Stripe + Empire revenue
# ═══════════════════════════════════════════════════════
def wf_revenue_dashboard():
    nodes = [
        {
            "parameters": {
                "rule": {
                    "interval": [{"field": "hours", "hoursInterval": 1}]
                }
            },
            "id": "schedule-rev",
            "name": "⏰ Every Hour",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// Read revenue state
const now = new Date();
const stats = {
  timestamp: now.toISOString(),
  hour: now.getHours(),
  day: now.toISOString().split('T')[0],
  
  // These will be enriched by downstream nodes
  total_revenue_eur: 0,
  transactions_today: 0,
  top_product: 'unknown',
  
  // Empire status
  empire_status: 'ACTIVE',
  agents_running: 0,
  content_generated: 0,
};

return [{json: stats}];"""
            },
            "id": "code-rev-stats",
            "name": "📊 Compile Stats",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-revenue-check",
                            "leftValue": "={{ $json.total_revenue_eur }}",
                            "rightValue": "100",
                            "operator": {"type": "number", "operation": "gte"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-milestone",
            "name": "💎 Milestone?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [750, 300]
        },
        {
            "parameters": {
                "jsCode": """// Format revenue report
const stats = $input.first().json;
const report = {
  text: `💰 EMPIRE REVENUE REPORT\\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━\\n` +
        `📅 ${stats.day}\\n` +
        `💶 Total: €${stats.total_revenue_eur}\\n` +
        `📦 Transactions: ${stats.transactions_today}\\n` +
        `🏆 Top Product: ${stats.top_product}\\n` +
        `🤖 Agents: ${stats.agents_running}\\n` +
        `📝 Content: ${stats.content_generated}\\n` +
        `━━━━━━━━━━━━━━━━━━━━━━━━\\n` +
        `Status: ${stats.empire_status}`,
  channel: '#revenue'
};

return [{json: report}];"""
            },
            "id": "code-format-report",
            "name": "📝 Format Report",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 520]
        }
    ]
    
    connections = {
        "⏰ Every Hour": {
            "main": [[{"node": "📊 Compile Stats", "type": "main", "index": 0}]]
        },
        "📊 Compile Stats": {
            "main": [[
                {"node": "💎 Milestone?", "type": "main", "index": 0},
                {"node": "📝 Format Report", "type": "main", "index": 0}
            ]]
        }
    }
    
    return create_workflow("💰 Revenue Dashboard", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 3: CONTENT BLITZ AUTO-POST
# Receives generated content and auto-posts
# ═══════════════════════════════════════════════════════
def wf_content_blitz():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "empire-swarm/content-created",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-content",
            "name": "📝 Content Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-tiktok",
                            "leftValue": "={{ $json.type }}",
                            "rightValue": "tiktok_script",
                            "operator": {"type": "string", "operation": "equals"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "switch-platform",
            "name": "📱 Platform Router",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 3,
            "position": [500, 300]
        },
        {
            "parameters": {
                "jsCode": """// Format for X/Twitter
const item = $input.first().json;

const tweets = item.result ? item.result.split('\\n\\n').filter(t => t.trim()) : ['No content'];

const formatted = {
  platform: 'twitter',
  content: tweets[0] || item.result,
  thread: tweets,
  hashtags: ['#AI', '#Automation', '#AIEmpire'],
  scheduled_for: new Date(Date.now() + 3600000).toISOString(),
  original_type: item.type,
  department: item.department
};

return [{json: formatted}];"""
            },
            "id": "code-format-x",
            "name": "🐦 Format for X",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [750, 200]
        },
        {
            "parameters": {
                "jsCode": """// Format TikTok Script
const item = $input.first().json;

const formatted = {
  platform: 'tiktok',
  script: item.result,
  hook: item.result ? item.result.split('.')[0] : 'Hook missing',
  duration_estimate: '60s',
  visual_style: 'talking_head',
  music_suggestion: 'trending_beat',
  original_type: item.type,
  department: item.department
};

return [{json: formatted}];"""
            },
            "id": "code-format-tiktok",
            "name": "🎬 Format TikTok",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [750, 400]
        },
        {
            "parameters": {
                "jsCode": """// Format YouTube Script
const item = $input.first().json;

const formatted = {
  platform: 'youtube',
  title: item.result ? item.result.split('\\n')[0] : 'Video Title',
  script: item.result,
  estimated_length: '8-12 min',
  thumbnail_ideas: ['Bold text overlay', 'Shocked face', 'Before/After'],
  tags: ['AI', 'automation', 'business', 'tech'],
  original_type: item.type,
  department: item.department
};

return [{json: formatted}];"""
            },
            "id": "code-format-yt",
            "name": "📹 Format YouTube",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [750, 600]
        },
        {
            "parameters": {
                "jsCode": """// Save all content to master queue
const item = $input.first().json;

const queueEntry = {
  id: Date.now().toString(36),
  ...item,
  status: 'queued',
  created_at: new Date().toISOString(),
  priority: item.is_high_value ? 'high' : 'normal'
};

return [{json: queueEntry}];"""
            },
            "id": "code-queue",
            "name": "📋 Content Queue",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1000, 400]
        }
    ]
    
    connections = {
        "📝 Content Webhook": {
            "main": [[{"node": "📱 Platform Router", "type": "main", "index": 0}]]
        },
        "📱 Platform Router": {
            "main": [
                [{"node": "🐦 Format for X", "type": "main", "index": 0}],
                [{"node": "🎬 Format TikTok", "type": "main", "index": 0}],
                [{"node": "📹 Format YouTube", "type": "main", "index": 0}]
            ]
        },
        "🐦 Format for X": {
            "main": [[{"node": "📋 Content Queue", "type": "main", "index": 0}]]
        },
        "🎬 Format TikTok": {
            "main": [[{"node": "📋 Content Queue", "type": "main", "index": 0}]]
        },
        "📹 Format YouTube": {
            "main": [[{"node": "📋 Content Queue", "type": "main", "index": 0}]]
        }
    }
    
    return create_workflow("📢 Content Blitz Auto-Router", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 4: SALES FORCE PIPELINE
# Manages sales outreach and CRM
# ═══════════════════════════════════════════════════════
def wf_sales_force():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "empire-swarm/sales-action",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-sales",
            "name": "🎯 Sales Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// Sales Pipeline Stage Router
const item = $input.first().json;

const stage = {
  type: item.type || 'unknown',
  department: item.department,
  
  // Determine pipeline stage
  pipeline_stage: 'unknown',
  next_action: 'review',
  urgency: 'normal'
};

if (item.type === 'cold_email') {
  stage.pipeline_stage = 'OUTREACH';
  stage.next_action = 'send_email';
  stage.urgency = 'high';
} else if (item.type === 'proposal') {
  stage.pipeline_stage = 'PROPOSAL';
  stage.next_action = 'customize_and_send';
  stage.urgency = 'critical';
} else if (item.type === 'objection_handling') {
  stage.pipeline_stage = 'NEGOTIATION';
  stage.next_action = 'follow_up';
  stage.urgency = 'medium';
}

return [{json: {...item, ...stage}}];"""
            },
            "id": "code-sales-route",
            "name": "🔀 Pipeline Router",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "jsCode": """// Score lead quality
const item = $input.first().json;

let score = 50; // base score
if (item.revenue_eur > 5) score += 20;
if (item.type === 'proposal') score += 15;
if (item.urgency === 'critical') score += 10;

const scored = {
  ...item,
  lead_score: score,
  lead_grade: score >= 80 ? 'A' : score >= 60 ? 'B' : 'C',
  action_required: score >= 70,
  auto_send: score >= 85
};

return [{json: scored}];"""
            },
            "id": "code-lead-score",
            "name": "⭐ Lead Scoring",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [750, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-auto-send",
                            "leftValue": "={{ $json.auto_send }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "true"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-auto-send",
            "name": "🚀 Auto-Send?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [1000, 300]
        }
    ]
    
    connections = {
        "🎯 Sales Webhook": {
            "main": [[{"node": "🔀 Pipeline Router", "type": "main", "index": 0}]]
        },
        "🔀 Pipeline Router": {
            "main": [[{"node": "⭐ Lead Scoring", "type": "main", "index": 0}]]
        },
        "⭐ Lead Scoring": {
            "main": [[{"node": "🚀 Auto-Send?", "type": "main", "index": 0}]]
        }
    }
    
    return create_workflow("🎯 Sales Force Pipeline", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 5: GHOST SQUADRON OPS
# Tracks all ghost squadron missions
# ═══════════════════════════════════════════════════════
def wf_ghost_squadron():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "empire-swarm/ghost-mission",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-ghost",
            "name": "👻 Ghost Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// Ghost Squadron Mission Tracker
const item = $input.first().json;

const units = {
  'sniper': '🎯 SNIPER',
  'demo': '💥 DEMO',
  'shield': '🛡️ SHIELD',
  'recon': '🔍 RECON',
  'striker': '⚡ STRIKER',
  'command': '🧠 COMMAND',
  'forge': '🔧 FORGE',
  'signal': '📡 SIGNAL'
};

const mission = {
  unit_name: units[item.unit] || '❓ UNKNOWN',
  unit_code: item.unit,
  mission_type: item.mission_type || item.type,
  priority: item.priority || 'medium',
  status: item.status || 'active',
  result_preview: item.result ? item.result.substring(0, 200) : 'Pending...',
  revenue_potential: item.revenue_potential || 0,
  revenue_actual: item.revenue_actual || item.revenue_eur || 0,
  timestamp: new Date().toISOString()
};

return [{json: mission}];"""
            },
            "id": "code-ghost-track",
            "name": "📋 Mission Tracker",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-critical",
                            "leftValue": "={{ $json.priority }}",
                            "rightValue": "critical",
                            "operator": {"type": "string", "operation": "equals"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-critical",
            "name": "🚨 Critical?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [750, 300]
        },
        {
            "parameters": {
                "jsCode": """// Summary report for all missions
const item = $input.first().json;
const report = {
  alert: `🚨 CRITICAL MISSION: ${item.unit_name}`,
  details: item.mission_type,
  revenue: item.revenue_potential,
  action: 'IMMEDIATE REVIEW REQUIRED'
};
return [{json: report}];"""
            },
            "id": "code-alert",
            "name": "🔔 Alert",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1000, 200]
        }
    ]
    
    connections = {
        "👻 Ghost Webhook": {
            "main": [[{"node": "📋 Mission Tracker", "type": "main", "index": 0}]]
        },
        "📋 Mission Tracker": {
            "main": [[{"node": "🚨 Critical?", "type": "main", "index": 0}]]
        },
        "🚨 Critical?": {
            "main": [
                [{"node": "🔔 Alert", "type": "main", "index": 0}],
                []
            ]
        }
    }
    
    return create_workflow("👻 Ghost Squadron Ops", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 6: EMPIRE HEARTBEAT
# Monitors the entire empire health
# ═══════════════════════════════════════════════════════
def wf_empire_heartbeat():
    nodes = [
        {
            "parameters": {
                "rule": {
                    "interval": [{"field": "minutes", "minutesInterval": 5}]
                }
            },
            "id": "schedule-heartbeat",
            "name": "💓 Every 5 Min",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// Empire Health Check
const now = new Date();

const health = {
  timestamp: now.toISOString(),
  
  // Services
  services: {
    nucleus: { status: 'checking', url: 'localhost:8080' },
    ollama: { status: 'checking', url: 'localhost:11434' },
    stripe: { status: 'checking', url: 'api.stripe.com' },
    n8n: { status: 'active', url: 'ai1337empire.app.n8n.cloud' },
  },
  
  // Metrics
  metrics: {
    uptime_hours: Math.floor((now - new Date('2026-02-09')) / 3600000),
    agents_deployed: 10000,
    revenue_today: 0,
    content_pieces: 0,
    errors_last_hour: 0
  },
  
  // Health score
  overall_health: 100,
  status: 'OPERATIONAL'
};

return [{json: health}];"""
            },
            "id": "code-health",
            "name": "🏥 Health Check",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-unhealthy",
                            "leftValue": "={{ $json.overall_health }}",
                            "rightValue": "50",
                            "operator": {"type": "number", "operation": "lt"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-unhealthy",
            "name": "🚨 Unhealthy?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [750, 300]
        },
        {
            "parameters": {
                "jsCode": """// Generate health report
const h = $input.first().json;

const report = {
  title: '💓 EMPIRE HEARTBEAT',
  status: h.status,
  health_score: h.overall_health + '%',
  uptime: h.metrics.uptime_hours + ' hours',
  agents: h.metrics.agents_deployed,
  revenue: '€' + h.metrics.revenue_today,
  services: Object.entries(h.services).map(([k,v]) => 
    (v.status === 'active' ? '✅' : '❓') + ' ' + k
  ).join('\\n'),
  generated_at: new Date().toISOString()
};

return [{json: report}];"""
            },
            "id": "code-report",
            "name": "📋 Health Report",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 520]
        }
    ]
    
    connections = {
        "💓 Every 5 Min": {
            "main": [[{"node": "🏥 Health Check", "type": "main", "index": 0}]]
        },
        "🏥 Health Check": {
            "main": [[
                {"node": "🚨 Unhealthy?", "type": "main", "index": 0},
                {"node": "📋 Health Report", "type": "main", "index": 0}
            ]]
        }
    }
    
    return create_workflow("💓 Empire Heartbeat Monitor", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 7: BRAIN DECISION LOGGER
# ═══════════════════════════════════════════════════════
def wf_brain_logger():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "empire-swarm/brain-decision",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-brain",
            "name": "🧠 Brain Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// Analyze Brain Decision
const item = $input.first().json;

const cells = item.cells || {};
const decision = {
  timestamp: new Date().toISOString(),
  directive: item.directive || 'HOLD',
  confidence: item.confidence || 0,
  
  // 8 Brain Cells
  revenue_score: cells.revenue || 0,
  agent_score: cells.agents || 0,
  risk_score: cells.risk || 0,
  timing_score: cells.timing || 0,
  resource_score: cells.resources || 0,
  content_score: cells.content || 0,
  pipeline_score: cells.pipeline || 0,
  competitive_score: cells.competitive || 0,
  
  // Weighted average
  weighted_avg: item.weighted_score || 0,
  
  // Action
  action: item.action || 'none',
  details: JSON.stringify(item.details || {})
};

return [{json: decision}];"""
            },
            "id": "code-brain-analyze",
            "name": "📊 Analyze Decision",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-directive",
                            "leftValue": "={{ $json.directive }}",
                            "rightValue": "SCALE_UP",
                            "operator": {"type": "string", "operation": "equals"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-scale",
            "name": "📈 Scale Up?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [750, 300]
        }
    ]
    
    connections = {
        "🧠 Brain Webhook": {
            "main": [[{"node": "📊 Analyze Decision", "type": "main", "index": 0}]]
        },
        "📊 Analyze Decision": {
            "main": [[{"node": "📈 Scale Up?", "type": "main", "index": 0}]]
        }
    }
    
    return create_workflow("🧠 Brain Decision Logger", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 8: STRIPE PAYMENT PROCESSOR
# ═══════════════════════════════════════════════════════
def wf_stripe_processor():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "stripe/webhook",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-stripe",
            "name": "💳 Stripe Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// Process Stripe Event
const item = $input.first().json;
const event_type = item.type || 'unknown';

const processed = {
  event_type: event_type,
  timestamp: new Date().toISOString(),
  is_payment: event_type.includes('payment') || event_type.includes('checkout'),
  is_refund: event_type.includes('refund'),
  
  // Extract amount
  amount_cents: item.data?.object?.amount_total || item.data?.object?.amount || 0,
  amount_eur: ((item.data?.object?.amount_total || item.data?.object?.amount || 0) / 100).toFixed(2),
  currency: item.data?.object?.currency || 'eur',
  
  // Customer
  customer_email: item.data?.object?.customer_email || item.data?.object?.customer_details?.email || 'unknown',
  
  // Product
  product_name: 'AI Empire Product',
  
  // Status
  status: item.data?.object?.status || item.data?.object?.payment_status || 'unknown'
};

return [{json: processed}];"""
            },
            "id": "code-stripe-process",
            "name": "🔄 Process Event",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-is-payment",
                            "leftValue": "={{ $json.is_payment }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "true"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-payment",
            "name": "💰 Payment?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [750, 300]
        },
        {
            "parameters": {
                "jsCode": """// Celebrate sale!
const item = $input.first().json;

const celebration = {
  message: '🎉 KA-CHING! New Sale!',
  amount: '€' + item.amount_eur,
  customer: item.customer_email,
  product: item.product_name,
  timestamp: new Date().toISOString(),
  
  // Notification
  notification_text: '💰 €' + item.amount_eur + ' von ' + item.customer_email + '! 🚀'
};

return [{json: celebration}];"""
            },
            "id": "code-celebrate",
            "name": "🎉 Celebrate!",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1000, 200]
        }
    ]
    
    connections = {
        "💳 Stripe Webhook": {
            "main": [[{"node": "🔄 Process Event", "type": "main", "index": 0}]]
        },
        "🔄 Process Event": {
            "main": [[{"node": "💰 Payment?", "type": "main", "index": 0}]]
        },
        "💰 Payment?": {
            "main": [
                [{"node": "🎉 Celebrate!", "type": "main", "index": 0}],
                []
            ]
        }
    }
    
    return create_workflow("💳 Stripe Payment Processor", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 9: YOUTUBE AUTOMATION
# ═══════════════════════════════════════════════════════
def wf_youtube_automation():
    nodes = [
        {
            "parameters": {
                "rule": {
                    "interval": [{"field": "hours", "hoursInterval": 6}]
                }
            },
            "id": "schedule-yt",
            "name": "⏰ Every 6 Hours",
            "type": "n8n-nodes-base.scheduleTrigger",
            "typeVersion": 1.2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// YouTube Content Pipeline
const niches = ['ai_news', 'finance', 'tech_reviews', 'motivation', 'open_source'];
const niche = niches[Math.floor(Math.random() * niches.length)];

const pipeline = {
  niche: niche,
  stage: 'SCRIPT_GENERATION',
  target_length_min: 10,
  estimated_cpm: 15,
  
  // Revenue estimate
  target_views: 50000,
  estimated_revenue: (50000 / 1000 * 15).toFixed(2),
  
  // Metadata
  upload_time: '15:00 UTC',
  publish_day: new Date().toLocaleDateString('en', {weekday: 'long'}),
  
  timestamp: new Date().toISOString()
};

return [{json: pipeline}];"""
            },
            "id": "code-yt-pipeline",
            "name": "🎬 Video Pipeline",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "jsCode": """// Generate SEO Metadata
const item = $input.first().json;

const seo = {
  ...item,
  title_options: [
    'How AI is Changing Everything in 2026',
    'I Built a $10K/Month AI Business (Full Tutorial)',
    'The AI Tool That Replaced My Entire Team'
  ],
  description_template: 'In this video, I show you how to leverage AI to...',
  tags: ['AI', 'artificial intelligence', 'automation', 'business', 'money', 'tech'],
  thumbnail_style: 'bold_text_reaction'
};

return [{json: seo}];"""
            },
            "id": "code-yt-seo",
            "name": "🔍 SEO Optimizer",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [750, 300]
        }
    ]
    
    connections = {
        "⏰ Every 6 Hours": {
            "main": [[{"node": "🎬 Video Pipeline", "type": "main", "index": 0}]]
        },
        "🎬 Video Pipeline": {
            "main": [[{"node": "🔍 SEO Optimizer", "type": "main", "index": 0}]]
        }
    }
    
    return create_workflow("📹 YouTube Automation Pipeline", nodes, connections)


# ═══════════════════════════════════════════════════════
# WORKFLOW 10: X MONSTER AUTO-POST
# ═══════════════════════════════════════════════════════
def wf_x_monster():
    nodes = [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "empire-swarm/x-content",
                "responseMode": "onReceived",
                "options": {}
            },
            "id": "webhook-x",
            "name": "🐦 X Content Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 2,
            "position": [250, 300]
        },
        {
            "parameters": {
                "jsCode": """// X Monster Content Processor
const item = $input.first().json;

const tweets = item.tweets || (item.result ? item.result.split('\\n\\n') : ['No content']);

const processed = {
  mode: item.mode || 'viral',
  topic: item.topic || 'AI',
  tweet_count: tweets.length,
  tweets: tweets.map((t, i) => ({
    index: i + 1,
    text: t.trim(),
    chars: t.trim().length,
    is_valid: t.trim().length <= 280
  })),
  first_tweet: tweets[0] || '',
  is_thread: tweets.length > 1,
  engagement_estimate: tweets.length > 3 ? 'HIGH' : 'MEDIUM',
  
  // Schedule
  post_at: new Date(Date.now() + Math.random() * 3600000).toISOString(),
  generated_at: new Date().toISOString()
};

return [{json: processed}];"""
            },
            "id": "code-x-process",
            "name": "🔄 Process Content",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [500, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                    "conditions": [
                        {
                            "id": "cond-thread",
                            "leftValue": "={{ $json.is_thread }}",
                            "rightValue": True,
                            "operator": {"type": "boolean", "operation": "true"}
                        }
                    ],
                    "combinator": "and"
                },
                "options": {}
            },
            "id": "if-thread",
            "name": "🧵 Thread?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 2,
            "position": [750, 300]
        },
        {
            "parameters": {
                "jsCode": """// Format as thread
const item = $input.first().json;
const formatted = {
  post_type: 'thread',
  thread_tweets: item.tweets,
  schedule: item.post_at,
  status: 'ready_to_post'
};
return [{json: formatted}];"""
            },
            "id": "code-thread",
            "name": "🧵 Thread Builder",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1000, 200]
        },
        {
            "parameters": {
                "jsCode": """// Format as single tweet
const item = $input.first().json;
const formatted = {
  post_type: 'single',
  tweet: item.first_tweet,
  schedule: item.post_at,
  status: 'ready_to_post'
};
return [{json: formatted}];"""
            },
            "id": "code-single",
            "name": "📝 Single Tweet",
            "type": "n8n-nodes-base.code",
            "typeVersion": 2,
            "position": [1000, 400]
        }
    ]
    
    connections = {
        "🐦 X Content Webhook": {
            "main": [[{"node": "🔄 Process Content", "type": "main", "index": 0}]]
        },
        "🔄 Process Content": {
            "main": [[{"node": "🧵 Thread?", "type": "main", "index": 0}]]
        },
        "🧵 Thread?": {
            "main": [
                [{"node": "🧵 Thread Builder", "type": "main", "index": 0}],
                [{"node": "📝 Single Tweet", "type": "main", "index": 0}]
            ]
        }
    }
    
    return create_workflow("🐦 X Monster Auto-Post", nodes, connections)


# ═══════════════════════════════════════════════════════
# MAIN — Export all workflows as JSON
# ═══════════════════════════════════════════════════════

ALL_WORKFLOWS = {
    "1_kimi_swarm": wf_kimi_swarm_receiver,
    "2_revenue_dashboard": wf_revenue_dashboard,
    "3_content_blitz": wf_content_blitz,
    "4_sales_force": wf_sales_force,
    "5_ghost_squadron": wf_ghost_squadron,
    "6_empire_heartbeat": wf_empire_heartbeat,
    "7_brain_logger": wf_brain_logger,
    "8_stripe_processor": wf_stripe_processor,
    "9_youtube_automation": wf_youtube_automation,
    "10_x_monster": wf_x_monster,
}


def export_all():
    """Export all workflows as JSON files for manual import."""
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "n8n_workflows")
    os.makedirs(out_dir, exist_ok=True)
    
    print("\n" + "═" * 60)
    print("🔥  N8N WORKFLOW BUILDER — EXPORTING ALL WORKFLOWS")
    print("═" * 60)
    
    for name, builder_fn in ALL_WORKFLOWS.items():
        workflow = builder_fn()
        filepath = os.path.join(out_dir, f"{name}.json")
        with open(filepath, "w") as f:
            json.dump(workflow, f, indent=2, ensure_ascii=False)
        print(f"  ✅ {workflow['name']} → {filepath}")
    
    print("─" * 60)
    print(f"  📁 All {len(ALL_WORKFLOWS)} workflows exported to: {out_dir}")
    print(f"  📋 Import them in n8n: Settings → Import from File")
    print("═" * 60 + "\n")
    
    return out_dir


def push_to_n8n():
    """Push all workflows to n8n via REST API."""
    if not HAS_REQUESTS:
        print("❌ 'requests' library not installed. Run: pip install requests")
        print("   Falling back to JSON export mode.")
        return export_all()
    if not N8N_API_KEY:
        print("❌ N8N_API_KEY not set. Falling back to export mode.")
        return export_all()

    print("\n" + "═" * 60)
    print("🚀  PUSHING WORKFLOWS TO N8N CLOUD")
    print("═" * 60)
    
    for name, builder_fn in ALL_WORKFLOWS.items():
        workflow = builder_fn()
        try:
            resp = requests.post(
                f"{N8N_BASE_URL}/workflows",
                headers=HEADERS,
                json=workflow,
                timeout=15
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                print(f"  ✅ Created: {workflow['name']} (ID: {data.get('id', '?')})")
            else:
                print(f"  ❌ Failed: {workflow['name']} — {resp.status_code}: {resp.text[:100]}")
        except Exception as e:
            print(f"  ❌ Error: {workflow['name']} — {e}")
    
    print("═" * 60 + "\n")


if __name__ == "__main__":
    if "--push" in sys.argv:
        push_to_n8n()
    else:
        export_all()
