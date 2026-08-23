# ⚡ Dynamic GitHub Repository Analyzer

A context-aware repository health and production-readiness auditor built with Python and Streamlit.

## 🌟 Key Features
- **Adaptive Auditing Engine:** Evaluates code quality based on detected stack/language (Python, JS, Go, Rust) and project scale.
- **Recursive Tree Inspection:** Uses GitHub API Git Trees to inspect deeply nested directory structures.
- **Interactive Visualizations:** Renders category radar charts and metric breakdowns using Plotly.
- **Rate-Limit Resilience:** Supports optional GitHub Personal Access Tokens for private repository access.

## 🚀 Quickstart
```powershell
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
streamlit run app.py
```
