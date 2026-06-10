from pathlib import Path
import csv

# Base folder: current folder
base = Path.cwd()

# Create folders
folders = [
    "data",
    "scripts",
    "website",
    "website/pages",
    "website/components",
    "website/styles",
]

for folder in folders:
    (base / folder).mkdir(parents=True, exist_ok=True)

# Create promises.csv
promises_path = base / "data" / "promises.csv"

promises_header = [
    "promise_id",
    "promise_text",
    "topic",
    "keywords",
    "status",
    "progress_score",
    "evidence_summary",
    "last_checked",
]

sample_promises = [
    [
        "P001",
        "Build 1.5 million new homes over the next parliament",
        "Housing supply",
        "1.5 million homes; housebuilding; new homes; housing supply; planning reform",
        "in progress",
        "50",
        "Initial evidence suggests the promise has been announced and linked to planning reform, but delivery is not yet complete.",
        "2026-06-10",
    ],
    [
        "P002",
        "Reform the planning system to speed up housebuilding",
        "Planning",
        "planning reform; National Planning Policy Framework; NPPF; housebuilding targets; grey belt",
        "in progress",
        "50",
        "Government activity on planning reform can be tracked, but full implementation depends on legislation and actual outcomes.",
        "2026-06-10",
    ],
    [
        "P003",
        "Strengthen renters' rights",
        "Renters",
        "renters rights; private rented sector; eviction; tenants; landlord",
        "not started",
        "0",
        "No confirmed implementation evidence has been added yet.",
        "2026-06-10",
    ],
]

if not promises_path.exists():
    with open(promises_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(promises_header)
        writer.writerows(sample_promises)

# Create evidence.csv
evidence_path = base / "data" / "evidence.csv"

evidence_header = [
    "evidence_id",
    "promise_id",
    "source_type",
    "title",
    "url",
    "date_published",
    "evidence_text",
    "relevance_score",
    "suggested_status",
    "checked_by_human",
]

sample_evidence = [
    [
        "E001",
        "P001",
        "GOV.UK",
        "Example policy update",
        "https://www.gov.uk/example",
        "2026-06-10",
        "This is a placeholder evidence item. Replace it with real evidence later.",
        "80",
        "in progress",
        "no",
    ]
]

if not evidence_path.exists():
    with open(evidence_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(evidence_header)
        writer.writerows(sample_evidence)

# Create collect_evidence.py
collect_script = base / "scripts" / "collect_evidence.py"

if not collect_script.exists():
    collect_script.write_text(
        '''"""
This script will later collect evidence from official sources.
For now, it only checks whether the data files exist.
"""

from pathlib import Path
import pandas as pd

base = Path(__file__).resolve().parent.parent

promises_file = base / "data" / "promises.csv"
evidence_file = base / "data" / "evidence.csv"

promises = pd.read_csv(promises_file)
evidence = pd.read_csv(evidence_file)

print("Promises loaded:", len(promises))
print("Evidence items loaded:", len(evidence))
print("\\nCurrent promises:")
print(promises[["promise_id", "topic", "status", "progress_score"]])
''',
        encoding="utf-8",
    )

# Create README.md
readme_path = base / "README.md"
# Create README.md
readme_path = base / "README.md"

if not readme_path.exists():
    readme_content = """# Promise Tracker Website

This project is a semi-automatic promise tracker website.

It tracks political promises, collects evidence from official sources, and updates the progress status of each promise.

## Project structure

promise-tracker-website/
- data/
  - promises.csv
  - evidence.csv
- scripts/
  - collect_evidence.py
- website/
  - pages/
  - components/
  - styles/
- README.md

## Current stage

Step 1: Build the data structure for the promise tracker.

## Next step

Write a Python script to collect evidence from official sources such as GOV.UK, Parliament, and ONS.
"""

    readme_path.write_text(readme_content, encoding="utf-8")

print("Project structure created successfully!")
print(f"Base folder: {base}")
print("Created folders: data, scripts, website")
print("Created files: promises.csv, evidence.csv, collect_evidence.py, README.md")