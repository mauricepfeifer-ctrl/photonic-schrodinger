#!/bin/bash
# 🚀 RUN EMPIRE — ONE CLICK REVENUE
# Executes Content Blitz and Sales Force

echo "💰 INITIALIZING AI EMPIRE REVENUE PROTOCOLS..."

# 1. Activate Environment
source venv/bin/activate

# 2. Generate Content Assets (Traffic)
echo "⚡ STARTING CONTENT BLITZ (Generating 5 viral assets)..."
python content_blitz.py --count 5

# 3. Run Sales Force (Leads)
echo "🕵️ STARTING SALES FORCE (Prospecting)..."
python sales_force.py --mode all

# 4. Start Server (if needed)
# echo "🌐 STARTING SERVER..."
# python empire_nucleus.py

echo "✅ MONEY PRINTER FINISHED."
echo "📂 Check 'content_output' and 'sales_output' for your assets."
