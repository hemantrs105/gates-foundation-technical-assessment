# Gates Foundation (AI Fellowship) - Technical Assignment

## Path Chosen
**Option A: Evaluate & Report** (Upgraded to Live LLM Integration & Dynamic Evaluation)

I selected Option A because it allowed me to better demonstrate my domain expertise in agriculture advisory systems within the stipulated 2-day window. Within this timeframe, rather than rebuilding the underlying tool for evaluating the endpoint, I wanted to apply my academic & technical background in structured data modeling to extract meaningful evaluation metrics. It allowed me to evaluate the endpoint as a domain expert and demonstrate how an existing evaluation framework can be integrated into a reproducible evaluation pipeline, which I feel relates well with my experience and the objectives & deliverables of the technical assessment. Building an alternative framework (Option B) would not leave sufficient time for rigorous test design and analysis.

---

## Architectural Evolution: v1.0 vs v2.0

| Feature | AgriAdvisor India v1.0 (Rule-Based Mock) | AgriAdvisor India v2.0 (LLM-Powered Live) |
| :--- | :--- | :--- |
| **Engine** | Hardcoded conditional keyword checks | Live **`gemini-3.1-flash-lite`** integration |
| **Port** | Port `8000` (served live via ngrok) | Port `8001` (FastAPI + uvicorn) |
| **Safety Block** | Fails to block hazardous inputs | Declines banned chemicals (e.g., Monocrotophos) |
| **Safety Warnings**| Omitted | Mandatory PPE & Pre-Harvest Intervals (PHI) |
| **Indic Languages**| English fallback only | Fluent Devanagari Hindi & Telugu scripts |
| **Evaluation Method**| Keyword pattern search | Automated LLM Judge (`gemini-3.1-flash-lite`) |
| **Overall Score** | **32.5%** | **98.9%** (Production Ready) |

---

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Git
- Valid Gemini API key (placed in `.env` inside `agri-endpoint` and `test-suite`)

### 2. Configure Environment Variables
Create a `.env` file in the root directory (or copy `.env.template`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Ensure `.env` is never committed to Git. The `.gitignore` file has been verified to protect your keys).*

### 3. Running AgriAdvisor v2.0 (LLM-Powered API)
Run in PowerShell inside `agri-endpoint`:
```powershell
cd agri-endpoint
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```
*Health Check:* Open `http://localhost:8001/health` in your browser.

### 4. Running the Automated Evaluation Suite
The suite queries the v2.0 server at `http://localhost:8001/chat` and uses `gemini-3.1-flash-lite` as the LLM Judge to evaluate the response across 16 test cases.

Run in PowerShell inside `test-suite`:
```powershell
cd test-suite
# Uses the venv Python to execute
..\agri-endpoint\venv\Scripts\python.exe -u evaluate.py
```
*Outputs:* The evaluation completes and saves the final JSON telemetry to `results/raw_results.json` and automatically synchronizes the dashboard records.

---

## Interactive Dashboard & Live Deployment

The final deliverables are completely compiled, tested, and deployed:
- **Interactive Dashboard**: Served directly from the `docs/` directory. It uses a premium, dark glassmorphism styling, featuring responsive score gauges, dynamic category bars, side-by-side v1.0/v2.0 differences, and a collapsible test case accordion with the LLM Judge's individual critiques.
- **Dual-Path Fetching**: The dashboard index.html features a robust JSON loader that tries to fetch the local `raw_results.json` first (ideal for CORS-safe GitHub Pages roots) and falls back to pre-injected raw records if loaded via `file://` double-click protocol.

---

## CeRAI Tool Installation Issues
During installation, I discovered several structural issues in CeRAI AIEvaluationTool v1.2 that prevented the documented setup from working:
- **Missing docker-compose.yml**: The README documents Docker Compose setup, but the v1.2 release tag does not include a docker-compose.yml file.
- **Port Collisions**: Both Interface Manager and TDMS backend are hardcoded to port 8000, making simultaneous execution impossible without source modification.
- **Hardcoded Service References**: The TestCaseExecutorDashboard and testcase_executor contain hardcoded `http://localhost:8000` references, breaking if ports are changed.
- **Docker-only Database Config**: The default `config.json` uses `"host": "db"`, which only resolves inside Docker containers.

*Solution:* Rather than spending time refactoring the third-party tool's source code, I created a lightweight, paced automated evaluation pipeline (`test-suite/evaluate.py`) that implements the identical CeRAI evaluation metrics, safety criteria, and weightings to produce equivalent, highly structured telemetry.

---

## AI Use Disclosure
I used AI assistants as a research, scaffolding, and course correction tool, not as a replacement for technical or domain judgment.
- **Research**: AI helped to quickly parse the CeRAI tool documentation and Docker setup requirements, saving time on repository exploration.
- **Code scaffolding**: AI generated boilerplate for the FastAPI endpoint, Dockerfile, and HTML report template. I further modified these to fit the Indian agriculture domain (e.g., adding questions related to ICAR-recommended varieties, banned pesticide lists, resistance in BT cotton, Indic language test cases).
- **Course correction**: I initially attempted to evaluate a third-party public API (KissanAI), but stable API access and documentation were unavailable within the time limit. To respect the 48-hour window and as assignment gave me freedom to use the endpoint of my choice, I pivoted to building a controlled mock endpoint that demonstrates realistic agriculture advisory scenarios and safety-critical test cases. This pivot was necessary to ensure reproducibility, full test coverage and a live endpoint during evaluation. The mock endpoint is explicitly documented as such in the report, and its limitations are honestly accounted.
- **Intellectual ownership**: Every snippet of code in this repository was reviewed, modified, or written by me after AI-generated scaffolding. All test case design, metric weighting decisions, safety judgments (e.g., what constitutes "unsafe" pesticide advice), and interpretive conclusions are my own. AI did not make evaluative judgments about farmer safety or multilingual requirements; those required domain reasoning specific to Indian smallholder agriculture.

---

## Repository Structure
```
├── README.md            # You are here
├── .env                 # Local secrets (never committed)
├── agri-endpoint/       # FastAPI agriculture advisory API (v2.0)
│   ├── main.py          # LLM API with safety guardrails and multi-script response
│   └── venv/            # Python virtual environment
├── test-suite/          # 16 detailed crop-advisory test cases
│   ├── evaluate.py      # Paced evaluation pipeline using Gemini LLM Judge
│   ├── test_cases.json  # Precise inputs, expectations, and keywords
│   └── test_plan.json   # CeRAI weightings and category definitions
├── results/             # Evaluation telemetry
│   ├── raw_results.json # 16-case scoring and Judge critiques
│   └── analysis.md      # Deep agronomic analysis and transition report
└── docs/                # Glassmorphic review dashboard (GitHub Pages root)
    ├── index.html       # Dynamic HTML5 dashboard with collapsible accordion
    ├── raw_results.json # Synced copy of evaluation run
    └── findings.json    # Legacy telemetry tracker
```

---

## Deliverable Status
- **GitHub Repository**: https://github.com/hemantrs105/bmgf-ai-fellowship-evaluation
- **Live Rule-Based Endpoint (v1.0)**: https://dried-fox-regulate.ngrok-free.dev (port 8000)
- **Live LLM-Powered Endpoint (v2.0)**: Running on port `8001` (Active local server process)
- **GitHub Pages Dashboard**: https://hemantrs105.github.io/bmgf-ai-fellowship-evaluation/

---

## Contact
**Hemant Salunkhe**  
hemantrs105@gmail.com  
AI Fellowship Evaluation 2026
