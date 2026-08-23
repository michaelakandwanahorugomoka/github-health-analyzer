import re
from datetime import datetime, timezone
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(
    page_title="Dynamic GitHub Repo Health Analyzer",
    page_icon="⚡",
    layout="wide",
)


def parse_github_url(url: str):
    pattern = r"github\.com/([^/]+)/([^/]+)"
    match = re.search(pattern, url.strip().strip("/"))
    if match:
        return match.group(1), match.group(2).replace(".git", "")
    return None, None


def fetch_repo_tree(owner: str, repo: str, token: str = None):
    """Fetches recursive tree data to inspect nested files/folders."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    base_url = f"https://api.github.com/repos/{owner}/{repo}"

    # Metadata
    r_meta = requests.get(base_url, headers=headers)
    if r_meta.status_code != 200:
        return (
            None,
            f"Error fetching repo metadata (Status Code: {r_meta.status_code})",
        )
    meta = r_meta.json()

    # Recursive Tree
    default_branch = meta.get("default_branch", "main")
    r_tree = requests.get(
        f"{base_url}/git/trees/{default_branch}?recursive=1", headers=headers
    )

    paths = []
    if r_tree.status_code == 200:
        tree_data = r_tree.json()
        paths = [item["path"].lower() for item in tree_data.get("tree", [])]

    # Latest Commit
    r_commits = requests.get(
        f"{base_url}/commits?per_page=1", headers=headers
    )
    commits = r_commits.json() if r_commits.status_code == 200 else []

    return {"meta": meta, "paths": paths, "commits": commits}, None


def evaluate_health_dynamic(data: dict):
    meta = data["meta"]
    paths = data["paths"]
    commits = data["commits"]

    primary_lang = (meta.get("language") or "Unknown").lower()
    total_files = len(paths)
    is_small_project = total_files < 15

    checks = []
    recs = []
    scores = {}

    # --- 1. DOCUMENTATION & USABILITY ---
    doc_score = 0

    has_readme = any("readme" in p for p in paths)
    if has_readme:
        doc_score += 40
        checks.append(("🟢", "Documentation: README file detected"))
    else:
        recs.append(
            "Add a `README.md` to guide project visitors and reviewers."
        )
        checks.append(("🔴", "Documentation: No README found"))

    if meta.get("description"):
        doc_score += 20
        checks.append(("🟢", "Metadata: GitHub repository description set"))
    else:
        recs.append("Set a brief project description in your repository header.")
        checks.append(("🟡", "Metadata: Repository description missing"))

    if any("license" in p for p in paths):
        doc_score += 20
        checks.append(("🟢", "Legal: Open-source LICENSE present"))
    else:
        checks.append(("⚪", "Legal: No explicit LICENSE specified"))

    if any(p.startswith("docs/") or "wiki" in p or "contributing" in p for p in paths):
        doc_score += 20
        checks.append(("🟢", "Extended Docs: Found `/docs` or contribution guidelines"))
    else:
        doc_score += 10

    scores["Documentation"] = min(doc_score, 100)

    # --- 2. ADAPTIVE STRUCTURE & CI AUDIT ---
    struct_score = 0

    if any(".gitignore" in p for p in paths):
        struct_score += 25
        checks.append(("🟢", "Hygiene: `.gitignore` file configured"))
    else:
        recs.append("Add a `.gitignore` file tailored to your stack.")
        checks.append(("🔴", "Hygiene: `.gitignore` missing"))

    lang_deps = {
        "python": [
            "requirements.txt",
            "pyproject.toml",
            "pipfile",
            "environment.yml",
            "setup.py",
        ],
        "javascript": ["package.json"],
        "typescript": ["package.json", "tsconfig.json"],
        "go": ["go.mod"],
        "rust": ["cargo.toml"],
        "java": ["pom.xml", "build.gradle"],
    }

    target_deps = lang_deps.get(
        primary_lang,
        ["requirements.txt", "package.json", "pom.xml", "go.mod", "cargo.toml"],
    )
    has_dep_file = any(
        any(dep in p for dep in target_deps) for p in paths
    )

    if has_dep_file:
        struct_score += 35
        checks.append((
            "🟢",
            f"Dependencies: Standard manifest found for {primary_lang.capitalize()}",
        ))
    else:
        recs.append(f"Add a dependency management file for {primary_lang.capitalize()}.")
        checks.append(("🟡", "Dependencies: No standard manifest found"))

    has_tests = any(
        "test" in p or "spec" in p or p.endswith("_test.go") for p in paths
    )
    if has_tests:
        struct_score += 25
        checks.append(("🟢", "Quality Assurance: Test scripts or suite detected"))
    elif is_small_project:
        struct_score += 15
        checks.append((
            "⚪",
            "Quality Assurance: Small codebase — explicit test suite optional",
        ))
    else:
        recs.append("Add unit or integration tests under a `/tests` directory.")
        checks.append(("🟡", "Quality Assurance: No test directory detected"))

    has_ci = any(".github/workflows" in p or ".gitlab-ci" in p for p in paths)
    if has_ci:
        struct_score += 15
        checks.append(("🟢", "Automation: CI/CD workflow configured"))
    else:
        checks.append(("⚪", "Automation: No automated CI/CD pipeline set"))

    scores["Architecture"] = min(struct_score, 100)

    # --- 3. REPOSITORY ACTIVITY & MAINTAINABILITY ---
    activity_score = 40

    if commits and isinstance(commits, list) and len(commits) > 0:
        c_date = commits[0]["commit"]["committer"]["date"]
        # ISO-8601 parsing handles variable timestamps correctly
        last_commit = datetime.fromisoformat(c_date.replace("Z", "+00:00"))
        days = (datetime.now(timezone.utc) - last_commit).days

        if days <= 45:
            activity_score += 40
            checks.append(("🟢", f"Activity: High (Last commit {days} days ago)"))
        elif days <= 180:
            activity_score += 25
            checks.append(("🟡", f"Activity: Moderate (Last commit {days} days ago)"))
        else:
            activity_score += 10
            recs.append("Repository has been inactive for over 6 months.")
            checks.append(("🔴", f"Activity: Inactive (Last commit {days} days ago)"))

    if meta.get("stargazers_count", 0) > 0 or meta.get("forks_count", 0) > 0:
        activity_score += 20
        checks.append(("🟢", "Community: Project has earned stars or forks"))

    scores["Maintenance"] = min(activity_score, 100)

    overall_score = round(
        (scores["Documentation"] * 0.35)
        + (scores["Architecture"] * 0.45)
        + (scores["Maintenance"] * 0.20)
    )

    return overall_score, scores, checks, recs, primary_lang.capitalize()


# --- STREAMLIT FRONTEND ---
st.title("⚡ Dynamic GitHub Repository Analyzer")
st.markdown("Context-aware health and readiness auditing for public & private GitHub repositories.")

with st.sidebar:
    st.header("⚙️ Configuration")
    github_token = st.text_input(
        "GitHub Personal Access Token (Optional):",
        type="password",
        help="Increases API rate limits and allows scanning of private repositories.",
    )

url_input = st.text_input(
    "Target Repository URL:",
    value="https://github.com/michaelakandwanahorugomoka/usip-uganda",
)

if st.button("Run Adaptive Audit", type="primary"):
    owner, repo = parse_github_url(url_input)

    if not owner or not repo:
        st.error("Please enter a valid GitHub URL format (e.g., https://github.com/owner/repo)")
    else:
        with st.spinner(f"Analyzing structure of `{owner}/{repo}`..."):
            data, error = fetch_repo_tree(owner, repo, github_token)

        if error:
            st.error(error)
        else:
            overall_score, category_scores, checks, recs, lang = evaluate_health_dynamic(data)
            meta = data["meta"]

            st.divider()

            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("Overall Readiness", f"{overall_score}%")
            c2.metric("Primary Language", lang)
            c3.metric("Stars", meta.get("stargazers_count", 0))
            c4.metric("Forks", meta.get("forks_count", 0))
            c5.metric("Open Issues", meta.get("open_issues_count", 0))

            left, right = st.columns([1, 1])

            with left:
                st.markdown("### Category Audit Radar")
                df_scores = pd.DataFrame(
                    dict(r=list(category_scores.values()), theta=list(category_scores.keys()))
                )
                fig = px.line_polar(df_scores, r="r", theta="theta", line_close=True, range_r=[0, 100])
                fig.update_traces(fill="toself", line_color="#00CC96")
                st.plotly_chart(fig, use_container_width=True)

            with right:
                st.markdown("### Contextual Checks")
                for icon, msg in checks:
                    st.write(f"{icon} {msg}")

            st.divider()
            st.markdown("### 💡 Recommended Enhancements")
            if recs:
                for r in recs:
                    st.warning(r)
            else:
                st.success("🎉 Outstanding repository setup! No immediate issues detected.")