# 🔥 Kimi Mega Swarm -> n8n Integration Guide

You have activated **Maximale Kimi Power** by enabling real-time result streaming to n8n.
Every task completed by the Kimi Swarm is now beamed to your n8n instance immediately.

## 📡 Webhook Configuration

**Method:** `POST`
**URL:** `https://ai1337empire.app.n8n.cloud/webhook/empire-swarm/task_completed`

*(Note: The `task_completed` part is appended to your base `N8N_WEBHOOK_URL`)*

## 📦 Payload Schema

The Kimi Swarm sends the following JSON payload for every completed task:

```json
{
  "event": "task_completed",
  "task_id": 1234,
  "department": "sales",
  "type": "cold_email",
  "prompt": "Schreibe eine Cold Email für...",
  "result": "Subject: Skalieren Sie Ihr Business...\n\nHallo Herr Müller...",
  "revenue_eur": 2.50,
  "cost_usd": 0.00015,
  "timestamp": "2026-02-10T00:15:00.123456"
}
```

## ⚡ Power Workflows to Build

Now that you have this stream, you can build these "Maximum Power" workflows in n8n:

### 1. 📢 Auto-Posting Machine

- **Trigger:** Webhook (`type` == `x_thread` OR `department` == `marketing`)
- **Action:** Parse JSON `result`
- **Action:** Post to **Twitter/X** or **LinkedIn**
- **Result:** Fully autonomous social media scaling.

### 2. 📧 Sales Outreach Bot

- **Trigger:** Webhook (`type` == `cold_email` OR `type` == `proposal`)
- **Action:** Create Draft in **Gmail** / **Outlook** (or send directly via SMTP)
- **Action:** Log to **Google Sheets** / **HubSpot** / **Pipedrive**
- **Result:** Thousands of outreach emails generated and staged automatically.

### 3. 🎓 Course Creator

- **Trigger:** Webhook (`type` == `course_module`)
- **Action:** Save content to **Google Docs** or **Notion**
- **Action:** Create slide deck via **Google Slides** API
- **Result:** Entire courses built in minutes.

### 4. 🧠 Knowledge Base Builder

- **Trigger:** Webhook (`department` == `research` OR `troubleshooting`)
- **Action:** Upsert into **Vector Database** (Pinecone/Supabase)
- **Action:** Update **Notion Wiki**
- **Result:** Your AI Empire gets smarter with every task.

## 🚀 How to Run with Max Power

Run the swarm as usual. The streaming is **ENABLED** by default now.

```bash
# Run 1000 agents, streaming results to n8n
python kimi_mega_swarm.py --agents 1000

# Run only Sales department
python kimi_mega_swarm.py --department sales
```

To disable streaming (why would you?):

```bash
python kimi_mega_swarm.py --no-stream
```
