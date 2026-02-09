---
description: Generate and deploy a new landing page from blueprint
---

## Generate & Deploy Landing Page

// turbo-all

1. Copy an existing config as template:
```bash
cp blueprints/configs/bma_consulting.json blueprints/configs/NEW_PRODUCT.json
```

2. Edit the JSON config with product-specific content (title, pricing, colors, FAQ, etc.)

3. Generate the landing page:
```bash
python3 blueprints/generate_landing.py blueprints/configs/NEW_PRODUCT.json --output NEW_PRODUCT/
```

4. Preview locally:
```bash
open NEW_PRODUCT/index.html
```

5. Commit and push to GitHub Pages:
```bash
git add NEW_PRODUCT/ blueprints/configs/NEW_PRODUCT.json
git commit -m "🚀 Add NEW_PRODUCT landing page"
git push origin main
```

6. Verify live (wait ~60s for GitHub Pages deploy):
```bash
curl -s -o /dev/null -w "%{http_code}" https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/NEW_PRODUCT/
```

Live URL: `https://mauricepfeifer-ctrl.github.io/photonic-schrodinger/NEW_PRODUCT/`
