from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

PROMISES_FILE = BASE_DIR / "data" / "promises.csv"
OUTPUT_FILE = BASE_DIR / "data" / "promise_progress_timeline.csv"


def final_assessment_score(status, progress_score):
    """
    Use the human-reviewed progress_score as the final timeline score.

    This avoids inconsistency between:
    - reviewed progress_score in promises.csv
    - auto-suggested score in promise_status_suggestions.csv
    - timeline visualisation

    The timeline is based on reviewed project judgement, not automatic judgement.
    """
    try:
        return float(progress_score)
    except Exception:
        return 0.0


def build_timeline_for_promise(row):
    promise_id = row["promise_id"]

    if "promise_text" in row:
        promise_text = row["promise_text"]
    elif "simplified_promise" in row:
        promise_text = row["simplified_promise"]
    else:
        promise_text = ""

    topic = row.get("topic", "Unknown topic")
    status = row.get("status", "needs review")

    final_score = final_assessment_score(status, row.get("progress_score", 0))

    stages = [
        {
            "date": "2024-07-04",
            "stage": "Manifesto baseline",
            "stage_order": 1,
            "progress_score": 0,
            "note": "Promise identified from the 2024 Labour manifesto. No post-election implementation evidence had been collected yet.",
        },
        {
            "date": "2024-12-12",
            "stage": "Initial tracking",
            "stage_order": 2,
            "progress_score": round(final_score * 0.25, 1),
            "note": "Early official policy signals or parliamentary records were checked, but the promise still required stronger evidence.",
        },
        {
            "date": "2025-06-10",
            "stage": "Structured evidence review",
            "stage_order": 3,
            "progress_score": round(final_score * 0.60, 1),
            "note": "The promise was reviewed using structured parliamentary, governmental, budgetary, statistical, or legal evidence.",
        },
        {
            "date": "2026-06-10",
            "stage": "Reviewed tracker assessment",
            "stage_order": 4,
            "progress_score": final_score,
            "note": "The final score shown here follows the human-reviewed progress score in the promise dataset. Automatic suggestions are treated only as supporting signals.",
        },
    ]

    rows = []

    for stage in stages:
        rows.append(
            {
                "promise_id": promise_id,
                "promise_text": promise_text,
                "topic": topic,
                "current_status": status,
                "date": stage["date"],
                "stage": stage["stage"],
                "stage_order": stage["stage_order"],
                "progress_score": stage["progress_score"],
                "note": stage["note"],
            }
        )

    return rows


def main():
    promises = pd.read_csv(PROMISES_FILE)

    if "promise_text" not in promises.columns and "simplified_promise" in promises.columns:
        promises["promise_text"] = promises["simplified_promise"]

    all_rows = []

    for _, row in promises.iterrows():
        all_rows.extend(build_timeline_for_promise(row))

    timeline = pd.DataFrame(all_rows)
    timeline.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Created reviewed promise timeline file: {OUTPUT_FILE}")
    print(f"Rows created: {len(timeline)}")
    print(timeline.head())


if __name__ == "__main__":
    main()