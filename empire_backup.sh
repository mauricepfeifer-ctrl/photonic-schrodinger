#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# 🔄 AI EMPIRE — AUTOMATED BACKUP TO iCLOUD & GOOGLE DRIVE
# ═══════════════════════════════════════════════════════════════
# Runs automatically via cron or manually
# Syncs all empire data to cloud storage
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

# ─── CONFIGURATION ────────────────────────────────────────────
EMPIRE_DIR="$HOME/.gemini/antigravity/playground/photonic-schrodinger"
EMPIRE_CORE="$HOME/AIEmpire-Core"

# Cloud destinations
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/AI-Empire-Backup"
GDRIVE_DIR="$HOME/Library/CloudStorage/GoogleDrive-*/My Drive/AI-Empire-Backup"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$EMPIRE_DIR/backup.log"

# ─── COLORS ───────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}[$(date '+%H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}[$(date '+%H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"; }

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  🔄 AI EMPIRE — AUTOMATED BACKUP"
echo "  📅 $(date '+%Y-%m-%d %H:%M:%S')"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# ─── iCLOUD BACKUP ────────────────────────────────────────────
log "📱 Starting iCloud backup..."

# Create iCloud backup directory structure
mkdir -p "$ICLOUD_DIR/code"
mkdir -p "$ICLOUD_DIR/products"
mkdir -p "$ICLOUD_DIR/swarm-output"
mkdir -p "$ICLOUD_DIR/data"
mkdir -p "$ICLOUD_DIR/landing-pages"
mkdir -p "$ICLOUD_DIR/courses"
mkdir -p "$ICLOUD_DIR/configs"
mkdir -p "$ICLOUD_DIR/snapshots"

# 1. Sync all Python scripts & Go files
log "  📂 Syncing code files..."
rsync -av --update \
  --include="*.py" \
  --include="*.go" \
  --include="*.sh" \
  --include="*.json" \
  --include="*.md" \
  --include="*.html" \
  --include="*.css" \
  --include="*.js" \
  --exclude="venv/" \
  --exclude="__pycache__/" \
  --exclude=".git/" \
  --exclude="mega_swarm_output/" \
  --exclude="node_modules/" \
  "$EMPIRE_DIR/" "$ICLOUD_DIR/code/" 2>/dev/null || warn "Code sync had issues"

# 2. Sync products (BMA Checklisten etc.)
if [ -d "$EMPIRE_CORE/products" ]; then
  log "  📦 Syncing products..."
  rsync -av --update "$EMPIRE_CORE/products/" "$ICLOUD_DIR/products/" 2>/dev/null || warn "Products sync had issues"
fi

# 3. Sync swarm outputs (latest only — keep last 5 runs)
if [ -d "$EMPIRE_DIR/mega_swarm_output" ]; then
  log "  🐝 Syncing swarm output..."
  # Get latest 5 run directories
  for dir in $(ls -dt "$EMPIRE_DIR/mega_swarm_output/run_"* 2>/dev/null | head -5); do
    rsync -av --update "$dir/" "$ICLOUD_DIR/swarm-output/$(basename $dir)/" 2>/dev/null || true
  done
fi

# 4. Sync critical data files
log "  💰 Syncing data files..."
for f in revenue_log.json agent_rankings.json mega_swarm.log; do
  if [ -f "$EMPIRE_DIR/$f" ]; then
    cp -f "$EMPIRE_DIR/$f" "$ICLOUD_DIR/data/$f"
  fi
done

# 5. Sync landing pages
if [ -d "$EMPIRE_DIR/landing-pages" ]; then
  log "  🏠 Syncing landing pages..."
  rsync -av --update "$EMPIRE_DIR/landing-pages/" "$ICLOUD_DIR/landing-pages/" 2>/dev/null || true
fi

# 6. Sync courses
if [ -d "$EMPIRE_DIR/courses" ]; then
  log "  📚 Syncing courses..."
  rsync -av --update "$EMPIRE_DIR/courses/" "$ICLOUD_DIR/courses/" 2>/dev/null || true
fi

# 7. Create snapshot tarball (weekly)
DOW=$(date +%u) # 1=Monday
if [ "$DOW" -eq 1 ] || [ "${FORCE_SNAPSHOT:-}" = "true" ]; then
  log "  📸 Creating weekly snapshot..."
  SNAP_FILE="$ICLOUD_DIR/snapshots/empire_snapshot_${TIMESTAMP}.tar.gz"
  tar -czf "$SNAP_FILE" \
    -C "$EMPIRE_DIR" \
    --exclude="venv" \
    --exclude=".git" \
    --exclude="__pycache__" \
    --exclude="mega_swarm_output" \
    --exclude="node_modules" \
    . 2>/dev/null || warn "Snapshot creation had issues"
  
  # Keep only last 4 snapshots
  ls -t "$ICLOUD_DIR/snapshots/"*.tar.gz 2>/dev/null | tail -n +5 | xargs rm -f 2>/dev/null || true
  log "  📸 Snapshot saved: $(basename $SNAP_FILE)"
fi

# 8. Sync configs
log "  ⚙️  Syncing configs..."
for f in .env .env.example pyrightconfig.json .pyre_configuration requirements.txt; do
  if [ -f "$EMPIRE_DIR/$f" ]; then
    cp -f "$EMPIRE_DIR/$f" "$ICLOUD_DIR/configs/$f"
  fi
done

# ─── GOOGLE DRIVE BACKUP (if available) ───────────────────────
GDRIVE_ACTUAL=$(ls -d $HOME/Library/CloudStorage/GoogleDrive-*/My\ Drive 2>/dev/null | head -1)

if [ -n "${GDRIVE_ACTUAL:-}" ] && [ -d "${GDRIVE_ACTUAL}" ]; then
  log "📁 Google Drive detected! Syncing..."
  GDRIVE_BACKUP="${GDRIVE_ACTUAL}/AI-Empire-Backup"
  mkdir -p "$GDRIVE_BACKUP"
  
  rsync -av --update "$ICLOUD_DIR/" "$GDRIVE_BACKUP/" 2>/dev/null || warn "Google Drive sync had issues"
  log "  ✅ Google Drive backup complete"
else
  warn "Google Drive not mounted — skipping (iCloud only)"
fi

# ─── SUMMARY ─────────────────────────────────────────────────
TOTAL_SIZE=$(du -sh "$ICLOUD_DIR" 2>/dev/null | cut -f1)
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ BACKUP COMPLETE"
echo "  📱 iCloud:       $ICLOUD_DIR"
echo "  💾 Total Size:   ${TOTAL_SIZE:-unknown}"
echo "  📅 Timestamp:    $TIMESTAMP"
if [ -n "${GDRIVE_ACTUAL:-}" ]; then
  echo "  📁 Google Drive: ✅ Synced"
else
  echo "  📁 Google Drive: ❌ Not available"
fi
echo "═══════════════════════════════════════════════════════════════"
echo ""

log "✅ Backup complete at $(date)"
