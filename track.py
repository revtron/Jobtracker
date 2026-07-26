#!/usr/bin/env python3
import sys, os, re, json
from pathlib import Path
from datetime import datetime
from rapidfuzz import fuzz, process

BASE_DIR = Path(__file__).parent
RESUME_DIR = BASE_DIR / "resume"
JOBS_DIR = BASE_DIR / "jobs"

def extract_text(path):
    path = Path(path)
    if not path.exists():
        print(f"  File not found: {path}")
        return ""
    if path.suffix == ".pdf":
        import fitz
        doc = fitz.open(str(path))
        text = "".join(page.get_text() for page in doc)
        doc.close()
        return text
    elif path.suffix == ".docx":
        from docx import Document
        doc = Document(str(path))
        return "\n".join(p.text for p in doc.paragraphs)
    else:
        with open(path) as f:
            return f.read()

def extract_keywords(text):
    text_lower = text.lower()
    tech_skills = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue", "node",
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible", "jenkins",
        "git", "linux", "ci/cd", "devops", "mysql", "postgresql", "mongodb", "redis",
        "rest api", "graphql", "html", "css", "sass", "bootstrap", "flask", "django",
        "spring", "hibernate", "jira", "confluence", "agile", "scrum", "shell", "bash",
        "powershell", "networking", "ssl", "dns", "vpn", "firewall", "load balancer",
        "nginx", "apache", "tomcat", "elasticsearch", "kibana", "logstash", "grafana",
        "prometheus", "monitoring", "alerting", "splunk", "datadog", "new relic",
        "puppet", "chef", "salt", "vagrant", "packer", "vault", "consul", "nomad",
        "helm", "kustomize", "argocd", "flux", "gitops", "sonarqube", "nexus",
        "artifactory", "maven", "gradle", "npm", "yarn", "webpack", "babel",
        "microservices", "serverless", "lambda", "ec2", "s3", "rds", "dynamodb",
        "cloudfront", "route53", "iam", "vpc", "cloudformation", "cdk", "pulumi",
        "ml", "machine learning", "ai", "data science", "pandas", "numpy", "scikit",
        "tensorflow", "pytorch", "selenium", "cypress", "jest", "mocha", "chai",
        "postman", "swagger", "openapi", "oauth", "jwt", "saml", "ldap", "active directory",
        "windows", "macos", "ubuntu", "centos", "rhel", "suse", "debian", "alpine",
        "sql", "nosql", "oracle", "sqlite", "mariadb", "cassandra", "couchdb", "neo4j",
        "rabbitmq", "kafka", "activemq", "sqs", "sns", "pub/sub", "grpc", "websocket",
        "frontend", "backend", "full stack", "fullstack", "ui/ux", "responsive",
        "performance", "optimization", "security", "testing", "deployment",
        "code review", "documentation", "leadership", "mentoring", "team management",
    ]
    found = set()
    for skill in tech_skills:
        if skill in text_lower:
            found.add(skill)
    return sorted(found)

def analyze_jd(jd_text, resume_text):
    jd_lower = jd_text.lower()
    resume_lower = resume_text.lower()

    jd_keywords = extract_keywords(jd_text)
    resume_keywords = extract_keywords(resume_text)

    jd_set = set(jd_keywords)
    resume_set = set(resume_keywords)

    matched = jd_set & resume_set
    missing = jd_set - resume_set
    extra = resume_set - jd_set

    match_pct = round(len(matched) / len(jd_set) * 100) if jd_set else 0

    return {
        "match_pct": match_pct,
        "matched": sorted(matched),
        "missing": sorted(missing),
        "extra": sorted(extra),
        "jd_keywords": jd_keywords,
        "resume_keywords": resume_keywords
    }

def add_job(company, title, jd_text=None):
    safe_company = re.sub(r'[^a-zA-Z0-9]+', '_', company).strip('_').lower()
    safe_title = re.sub(r'[^a-zA-Z0-9]+', '_', title).strip('_').lower()
    folder = JOBS_DIR / f"{safe_company}_{safe_title}"
    folder.mkdir(parents=True, exist_ok=True)

    (folder / "status.md").write_text(f"""# {company} - {title}

**Applied:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** 📝 Not Applied
**Link:**
**Notes:**

## Timeline
- {datetime.now().strftime('%Y-%m-%d')}: Created entry
""")

    if jd_text:
        (folder / "job_description.md").write_text(jd_text)

    return folder

def analyze(company, title, jd_text=None):
    resume_files = list(RESUME_DIR.glob("*.pdf")) + list(RESUME_DIR.glob("*.docx")) + list(RESUME_DIR.glob("*.doc"))
    if not resume_files:
        print("  No resume found in resume/ folder")
        return

    resume_file = resume_files[0]
    print(f"\n  Using resume: {resume_file.name}")
    resume_text = extract_text(resume_file)

    if jd_text:
        folder = add_job(company, title, jd_text)
        result = analyze_jd(jd_text, resume_text)

        analysis = f"""# JD Analysis: {company} - {title}

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Match Score:** {result['match_pct']}%

---

## ✅ Matched Skills ({len(result['matched'])})
{chr(10).join(f'  - {s}' for s in result['matched']) if result['matched'] else '  None'}

## ❌ Missing Skills ({len(result['missing'])})
{chr(10).join(f'  - {s}' for s in result['missing']) if result['missing'] else '  None'}

## 📌 Skills to Highlight/Add
{chr(10).join(f'  - Consider adding: {s}' for s in result['missing'][:10]) if result['missing'] else '  All JD skills are covered!'}

---

## All JD Keywords
{', '.join(result['jd_keywords'])}

## Resume Skills Not in JD
{', '.join(result['extra'][:15]) if result['extra'] else 'None'}
"""
        (folder / "analysis.md").write_text(analysis)
        generate_workflow()
        print(f"\n  {'='*50}")
        print(f"  Match Score: {result['match_pct']}%")
        print(f"  ✅ Matched: {len(result['matched'])} skills")
        print(f"  ❌ Missing: {len(result['missing'])} skills")
        print(f"  📁 Created: {folder}")
        print(f"  {'='*50}")
    else:
        print("  No JD provided to analyze")

def list_jobs():
    jobs = sorted(JOBS_DIR.iterdir()) if JOBS_DIR.exists() else []
    if not jobs:
        print("  No job entries yet")
        return
    print(f"\n  {'Company':<30} {'Match':<8} Status")
    print(f"  {'-'*50}")
    for j in jobs:
        if j.is_dir():
            analysis_file = j / "analysis.md"
            status_file = j / "status.md"
            match = "N/A"
            if analysis_file.exists():
                for line in analysis_file.read_text().splitlines():
                    if "Match Score" in line:
                        match = line.split("**")[-1].strip() if "**" in line else line.split(":")[-1].strip()
                        break
            status = "📝 New"
            if status_file.exists():
                for line in status_file.read_text().splitlines():
                    if "**Status:**" in line:
                        status = line.split("**Status:**")[-1].strip()
                        break
            name = j.name.replace("_", " ").title()
            print(f"  {name:<30} {match:<8} {status}")

def generate_workflow():
    jobs = sorted(JOBS_DIR.iterdir()) if JOBS_DIR.exists() else []
    resume_files = list(RESUME_DIR.glob("*.pdf")) + list(RESUME_DIR.glob("*.docx"))
    resume_skills = 0
    if resume_files:
        text = extract_text(resume_files[0])
        resume_skills = len(extract_keywords(text))

    total_missing = set()
    all_missing = []
    job_cards = []
    for j in jobs:
        if not j.is_dir(): continue
        analysis_file = j / "analysis.md"
        status_file = j / "status.md"
        if not analysis_file.exists(): continue
        content = analysis_file.read_text()
        match = "N/A"
        for line in content.splitlines():
            if "Match Score" in line:
                m = re.search(r'(\d+)%', line)
                if m: match = m.group(1)
                break
        matched_section = content.split("## ✅ Matched Skills")[1].split("##")[0] if "## ✅ Matched Skills" in content else ""
        missing_section = content.split("## ❌ Missing Skills")[1].split("##")[0] if "## ❌ Missing Skills" in content else ""
        matched = [line.strip("- ").strip() for line in matched_section.splitlines() if line.strip().startswith("-")]
        missing = [line.strip("- ").strip() for line in missing_section.splitlines() if line.strip().startswith("-")]
        all_missing.extend(missing)
        for s in missing: total_missing.add(s)

        company_title = j.name.replace("_", " ").title()
        company = company_title.rsplit(" ", 1)[0] if len(company_title.rsplit(" ", 1)) > 1 else company_title
        title_part = company_title.rsplit(" ", 1)[-1] if len(company_title.rsplit(" ", 1)) > 1 else ""

        status = "Not Applied"
        if status_file.exists():
            for line in status_file.read_text().splitlines():
                if "**Status:**" in line:
                    st = line.split("**Status:**")[-1].strip()
                    if "Applied" in st: status = "Applied"
                    elif "Interview" in st: status = "Interview"
                    elif "Offer" in st: status = "Offer"
                    elif "Reject" in st: status = "Rejected"

        match_int = int(match) if match != "N/A" else 0
        match_class = "high" if match_int >= 80 else ("mid" if match_int >= 50 else "low")

        matched_tags = "".join(f'<span class="skill-tag tag-matched">{s}</span>' for s in matched)
        missing_tags = "".join(f'<span class="skill-tag tag-missing">{s}</span>' for s in missing)

        status_class = {"Applied": "status-applied", "Interview": "status-interview", "Offer": "status-offer", "Rejected": "status-rejected"}.get(status, "")

        job_cards.append(f'''    <div class="job-card">
      <div class="job-header">
        <div>
          <div class="job-title">{title_part or company}</div>
          <div class="job-company">{company} · <span class="status-badge {status_class}">{status}</span></div>
        </div>
        <div class="match-badge match-{match_class}">{match}%</div>
      </div>
      <div class="progress-bar">
        <div class="progress-fill {match_class}" style="width: {match_int}%"></div>
      </div>
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
        <div class="skills-section">
          <h3> Matched ({len(matched)})</h3>
          <div class="skill-tags">{matched_tags}</div>
        </div>
        <div class="skills-section">
          <h3> Missing ({len(missing)})</h3>
          <div class="skill-tags">{missing_tags}</div>
        </div>
      </div>
    </div>''')

    from collections import Counter
    missing_counts = Counter(all_missing)
    rec_items = []
    for skill, count in missing_counts.most_common():
        priority = "priority-high" if count >= 2 else ("priority-mid" if count == 1 else "priority-low")
        label = "High" if count >= 2 else ("Medium" if count == 1 else "Low")
        rec_items.append(f'      <div class="rec-item"><span class="{priority}">{label}</span> Add {skill} to resume (appears in {count} job{"s" if count > 1 else ""})</div>')

    if not rec_items:
        rec_items.append('      <div class="rec-item">All skills covered across all jobs!</div>')

    scores = []
    for c in job_cards:
        m = re.search(r'match-(high|mid|low)"[^>]*>(\d+)%', c)
        if m: scores.append(int(m.group(2)))
    avg_match = round(sum(scores) / len(scores)) if scores else 0

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Job Tracker - Resume Improvement Workflow</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #e2e8f0; padding: 20px; }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1 {{ font-size: 28px; margin-bottom: 8px; }}
  .subtitle {{ color: #94a3b8; margin-bottom: 24px; }}
  .stats-row {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 24px; }}
  .stat-card {{ background: #1e293b; border-radius: 12px; padding: 20px; border: 1px solid #334155; }}
  .stat-card .label {{ font-size: 13px; color: #94a3b8; margin-bottom: 4px; }}
  .stat-card .value {{ font-size: 32px; font-weight: 700; }}
  .job-card {{ background: #1e293b; border-radius: 12px; padding: 24px; margin-bottom: 20px; border: 1px solid #334155; }}
  .job-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px; flex-wrap: wrap; gap: 12px; }}
  .job-title {{ font-size: 20px; font-weight: 600; }}
  .job-company {{ color: #94a3b8; font-size: 14px; }}
  .match-badge {{ padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 18px; }}
  .match-high {{ background: #064e3b; color: #6ee7b7; }}
  .match-mid {{ background: #713f12; color: #fde68a; }}
  .match-low {{ background: #7f1d1d; color: #fca5a5; }}
  .skills-section {{ margin-top: 12px; }}
  .skills-section h3 {{ font-size: 14px; margin-bottom: 8px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
  .skill-tags {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .skill-tag {{ padding: 4px 12px; border-radius: 6px; font-size: 13px; }}
  .tag-matched {{ background: #064e3b; color: #6ee7b7; border: 1px solid #065f46; }}
  .tag-missing {{ background: #7f1d1d; color: #fca5a5; border: 1px solid #991b1b; }}
  .tag-extra {{ background: #1e3a5f; color: #93c5fd; border: 1px solid #1e40af; }}
  .progress-bar {{ height: 8px; background: #334155; border-radius: 4px; margin: 12px 0; overflow: hidden; }}
  .progress-fill {{ height: 100%; border-radius: 4px; transition: width 0.5s; }}
  .progress-fill.high {{ background: linear-gradient(90deg, #059669, #10b981); }}
  .progress-fill.mid {{ background: linear-gradient(90deg, #d97706, #f59e0b); }}
  .progress-fill.low {{ background: linear-gradient(90deg, #dc2626, #ef4444); }}
  .recommendations {{ background: #1e293b; border-radius: 12px; padding: 24px; margin-top: 24px; border: 1px solid #334155; }}
  .recommendations h2 {{ font-size: 18px; margin-bottom: 16px; }}
  .rec-item {{ padding: 8px 0; border-bottom: 1px solid #334155; display: flex; align-items: center; gap: 8px; }}
  .rec-item:last-child {{ border-bottom: none; }}
  .priority-high {{ color: #fca5a5; }}
  .priority-mid {{ color: #fde68a; }}
  .priority-low {{ color: #6ee7b7; }}
  .status-badge {{ font-size: 13px; padding: 4px 10px; border-radius: 12px; }}
  .status-applied {{ background: #1e3a5f; color: #93c5fd; }}
  .status-interview {{ background: #713f12; color: #fde68a; }}
  .status-offer {{ background: #064e3b; color: #6ee7b7; }}
  .status-rejected {{ background: #7f1d1d; color: #fca5a5; }}
  .footer {{ text-align: center; color: #475569; font-size: 13px; margin-top: 32px; padding: 20px; }}
</style>
</head>
<body>
<div class="container">
  <h1> Job Application Tracker</h1>
  <p class="subtitle">Resume gap analysis & improvement workflow · Updated {datetime.now().strftime('%b %d, %Y')}</p>

  <div class="stats-row">
    <div class="stat-card">
      <div class="label">Total Applications</div>
      <div class="value">{len(job_cards)}</div>
    </div>
    <div class="stat-card">
      <div class="label">Avg Match Score</div>
      <div class="value">{avg_match}%</div>
    </div>
    <div class="stat-card">
      <div class="label">Skills in Resume</div>
      <div class="value">{resume_skills}</div>
    </div>
    <div class="stat-card">
      <div class="label">Gaps to Fill</div>
      <div class="value">{len(total_missing)}</div>
    </div>
  </div>

  <div id="jobsContainer">
{chr(10).join(job_cards)}
  </div>

  <div class="recommendations">
    <h2> Resume Improvement Plan</h2>
{chr(10).join(rec_items)}
  </div>

  <div class="footer">Auto-generated by track.py</div>
</div>
</body>
</html>"""

    (BASE_DIR / "workflow.html").write_text(html)
    print(f"  Generated workflow.html ({len(job_cards)} jobs, {len(total_missing)} skill gaps)")

def main():
    if len(sys.argv) < 2:
        print("  Usage:")
        print("    python track.py add <company> <title> [jd_file]")
        print("    python track.py analyze <company> <title> [jd_file]")
        print("    python track.py list")
        print("    python track.py workflow")
        print("\n  Or paste JD interactively:")
        print('    echo "your JD text" | python track.py add Company Title')
        return

    cmd = sys.argv[1]

    if cmd == "list":
        list_jobs()
        return

    if cmd == "workflow":
        generate_workflow()
        return

    if cmd in ("add", "analyze"):
        if len(sys.argv) < 4:
            print("  Usage: track.py add <company> <title> [jd_file]")
            return

        company = sys.argv[2]
        title = " ".join(sys.argv[3:])

        if not sys.stdin.isatty():
            jd_text = sys.stdin.read()
        else:
            jd_text = None

        if cmd == "add":
            folder = add_job(company, title, jd_text)
            print(f"  Created job entry: {folder}")
        else:
            analyze(company, title, jd_text)

if __name__ == "__main__":
    main()
