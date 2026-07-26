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

def main():
    if len(sys.argv) < 2:
        print("  Usage:")
        print("    python track.py add <company> <title> [jd_file]")
        print("    python track.py analyze <company> <title> [jd_file]")
        print("    python track.py list")
        print("\n  Or paste JD interactively:")
        print('    echo "your JD text" | python track.py add Company Title')
        return

    cmd = sys.argv[1]

    if cmd == "list":
        list_jobs()
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
