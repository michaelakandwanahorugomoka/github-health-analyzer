# ⚡ Dynamic GitHub Repository Health Analyzer

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit)
![Plotly](https://img.shields.io/badge/Plotly-Interactive-3F4F75?style=for-the-badge&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

A context-aware repository health and production-readiness auditor built with Python and Streamlit. It dynamically inspects public and private GitHub repositories to evaluate code quality, project architecture, and maintainability.

---

## 🌟 Key Features

- **Context-Aware Auditing Engine:** Automatically adapts evaluation criteria based on project size and primary language (Python, JavaScript/TypeScript, Go, Rust, Java).
- **Deep Directory Inspection:** Uses GitHub`s recursive Git Trees API (`/git/trees/main?recursive=1`) to audit nested structures instead of just checking root files.
- **Interactive Radar Charts:** Visualizes breakdown scores across Documentation, Architecture, and Maintenance using Plotly.
- **Report Generation:** Export comprehensive audit summaries as `.md` report files with a single click.
- **Rate-Limit Management:** Supports optional Personal Access Token (PAT) authentication for higher API limits and private repository support.

---

## 🏗️ System Architecture & Workflow

```text
[GitHub Repo URL] ➡️ [URL Parsing] ➡️ [GitHub REST API / Git Trees]
                                                │
                                                ▼
[Exportable .md Report] ◄── [Streamlit UI] ◄── [Adaptive Scoring Engine]

🛠️ Tech Stack

    Frontend / Dashboard: Streamlit

    Data Visualization: Plotly Express

    API Integration: Python Requests (GitHub REST API v3)

    Data Handling: Pandas, Datetime (ISO 8601 parsing)

🚀 Quickstart

    Clone the repository:
    Bash

    git clone [https://github.com/michaelakandwanahorugomoka/github-health-analyzer.git](https://github.com/michaelakandwanahorugomoka/github-health-analyzer.git)
    cd github-health-analyzer

    Set up virtual environment:
    PowerShell

    python -m venv venv
    .\venv\Scripts\Activate

    Install dependencies:
    PowerShell

    pip install -r requirements.txt

    Run the Streamlit application:
    PowerShell

    streamlit run app.py

📄 License

Distributed under the MIT License. See LICENSE for more information.
