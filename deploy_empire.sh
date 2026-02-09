#!/bin/bash
# 🚀 DEPLOY EMPIRE — GO LIVE
# Pushes current codebase to GitHub (triggering Pages deploy)

echo "🌍 PREPARING FOR LIFTOFF..."

# 1. Add all changes
git add .

# 2. Commit with timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
git commit -m "🚀 Empire Launch $TIMESTAMP: Sales Force + Lead Magnet Live"

# 3. Push to main branch
echo "Pushing to GitHub..."
git push origin main

echo "✅ DEPLOYMENT COMPLETE."
echo "Your changes should be live on https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/ shortly."
