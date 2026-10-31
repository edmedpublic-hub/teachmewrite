# TeachMeWrite System Architecture Map
This file is the single source of truth for all file locations and infrastructure.
Last Updated: Day 100 (Phase 2 Start)




teachmewrite/
├── .github/
│   └── workflows/
│       └── deploy.yml                 # CI/CD pipeline (build, push, gate, deploy)
├── ai-service/                        # The FastAPI Backend
│   ├── main.py                        # The live AI service (auth, routes, logic)
│   ├── requirements.txt               # Python dependencies for production
│   ├── requirements-gate.txt          # Python dependencies for CI gate
│   ├── Dockerfile                     # Container definition
│   ├── run_gate.py                    # Golden-set evaluation script
│   ├── golden_set.jsonl               # 20-case test dataset
│   └── docs/
│       ├── evaluation.md              # Day 90 quality report
│       ├── runbook.md                 # [DAY 100] Incident response guide
│       └── grafana_dashboard.json     # [DAY 100] Dashboard as Code
├── frontend/                          # [PHASE 2] React application (to be created)
│   ├── src/                           # React components
│   └── package.json
├── notebooks/                         # Colab notebooks (Days 85-100)
│   ├── artifacts/                     # Saved JSON results (redteam, eval, etc.)
│   ├── day85_redteam.ipynb
│   └── ...
├── book/                              # [NEW] Daily chapters for the book
│   ├── day_100.md                     # Today's chapter
│   ├── day_101.md                     # Tomorrow's chapter
│   └── assets/                        # Images, diagrams for the book
├── ARCHITECTURE.md                    # [NEW] This exact map
└── README.md                          # Project overview



teachmewrite-ai/
├── batch_eval_day88.json              # Historical eval results
├── redteam_results_day86.json         # Historical security results
├── student_notes.json                 # Agent memory (from Day 93)
└── [Future models/datasets]           # For Phase 3 (Fine-tuning data)

GCP Project: teachmewrite-prod (asia-south1)
├── Cloud Run: teachmewrite-ai         # The live backend service
├── Artifact Registry: teachmewrite-ai # Docker images
├── Secret Manager: anthropic-api-key  # API key for Claude
├── Cloud Build                        # Used by GitHub Actions to build images
└── Monitoring                         # Alert Policy: "5xx Error Detected"
