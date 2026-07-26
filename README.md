# Job Application Tracker

Track job applications, analyze JD-resume fit, and identify skill gaps.

## Usage

```bash
# Add and analyze a new job
echo "paste JD here" | python3 track.py analyze "Company" "Job Title"

# List all tracked jobs
python3 track.py list

# Regenerate the workflow dashboard
python3 track.py workflow
```

Open `workflow.html` in a browser for a visual dashboard showing match scores, skill gaps, and a prioritized improvement plan.

## Structure

```
├── workflow.html        Visual dashboard
├── track.py             CLI tool
├── resume/              Your latest resume
└── jobs/                Per-job folders with JD, analysis, and status
```
