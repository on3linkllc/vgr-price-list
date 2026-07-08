# VGR America — Wholesale Price List

Live at https://whp.vgramerica.com (Cloudflare Pages, auto-deploys from `main`).

- `template.html` — page template (logo, styles, cart; placeholders: DATA_JSON, ISSUED_DATE, VALID_DATE)
- `generate.py` — builds `index.html` from the Google Sheet markdown export; rounds every price UP to the next X.99 (charm pricing); sets validity to build date + 30 days
- `data.json` — parsed product data from the last build (used for change detection)
- Updated automatically by a daily Claude scheduled task
