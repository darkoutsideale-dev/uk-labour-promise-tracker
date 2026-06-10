from pathlib import Path
from datetime import date
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

PROMISES_FILE = BASE_DIR / "data" / "promises.csv"
EVIDENCE_FILE = BASE_DIR / "data" / "evidence.csv"
OUTPUT_FILE = BASE_DIR / "data" / "promise_status_suggestions.csv"


IMPLEMENTED_KEYWORDS = [
    "act",
    "enacted",
    "law",
    "legislation",
    "royal assent",
    "regulation",
    "statutory instrument",
    "came into force",
    "implemented",
]

IN_PROGRESS_KEYWORDS = [
    "bill",
    "consultation",
    "proposal",
    "plan",
    "strategy",
    "review",
    "funding",
    "announced",
    "introduced",
    "published",
    "reform",
]

LOW_RELEVANCE_WORDS = [
    "speech",
    "statement",
    "debate",
]


def classify_evidence(evidence_texts):
    combined_text = " ".join(evidence_texts).lower()

    implemented_hits = sum(1 for word in IMPLEMENTED_KEYWORDS if word in combined_text)
    in_progress_hits = sum(1 for word in IN_PROGRESS_KEYWORDS if word in combined_text)

    if implemented_hits >= 4:
        return "implemented", 100, "A law or policy has been passed that directly delivers this promise."
    elif implemented_hits >= 2:
        return "partly implemented", 75, "Some steps have been taken but the promise is not fully delivered yet."
    elif in_progress_hits >= 1:
        return "in progress", 50, "Work is underway on this promise but no final law or policy has been passed yet."
    else:
        return "needs review", 25, "Some evidence was found but it is not clear enough to classify automatically."

def main():
    promises = pd.read_csv(PROMISES_FILE)

    if not EVIDENCE_FILE.exists():
        print("No evidence.csv found. Run collect_evidence.py first.")
        return

    evidence = pd.read_csv(EVIDENCE_FILE)

    suggestions = []

    for _, promise in promises.iterrows():
        promise_id = promise["promise_id"]
        current_status = promise["status"]
        current_score = promise["progress_score"]

        related_evidence = evidence[evidence["promise_id"] == promise_id]

        if len(related_evidence) == 0:
            suggested_status = "not started"
            suggested_score = 0
            auto_summary = "No collected evidence was found for this promise."
        else:
            texts = []

            for _, row in related_evidence.iterrows():
                title = str(row.get("title", ""))
                evidence_text = str(row.get("evidence_text", ""))
                texts.append(title + " " + evidence_text)

            suggested_status, suggested_score, auto_summary = classify_evidence(texts)

        suggestions.append(
            {
                "promise_id": promise_id,
                "promise_text": promise["promise_text"],
                "current_status": current_status,
                "current_progress_score": current_score,
                "suggested_status": suggested_status,
                "suggested_progress_score": suggested_score,
                "evidence_count": len(related_evidence),
                "auto_summary": auto_summary,
                "last_auto_checked": str(date.today()),
            }
        )

    output = pd.DataFrame(suggestions)
    output.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Status suggestions created: {OUTPUT_FILE}")
    print(output[["promise_id", "current_status", "suggested_status", "evidence_count"]])


if __name__ == "__main__":
    main()