from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

PROMISES_FILE = BASE_DIR / "data" / "promises.csv"
OUTPUT_FILE = BASE_DIR / "data" / "promise_progress_timeline.csv"


def final_assessment_score(status, progress_score):
    """
    This is not a direct completion percentage.
    It is a cautious evidence-based assessment score for visual timeline purposes.
    """
    status = str(status).lower().strip()

    if status == "implemented":
        return 80
    if status == "partly implemented":
        return 65
    if status == "in progress":
        return 45
    if status == "needs review":
        return 25
    if status == "not started":
        return 10

    try:
        return min(float(progress_score), 80)
    except Exception:
        return 0


def build_timeline_for_promise(row):
    promise_id = row["promise_id"]
    promise_text = row["promise_text"]
    topic = row["topic"]
    status = row["status"]

    final_score = final_assessment_score(status, row["progress_score"])

    stages = [
        {
            "date": "2024-07-04",
            "stage": "Manifesto baseline",
            "stage_order": 1,
            "progress_score": 0,
            "note": "Promise identified from the manifesto. No post-election implementation evidence had been collected yet.",
        },
        {
            "date": "2024-12-12",
            "stage": "Initial policy signals",
            "stage_order": 2,
            "progress_score": round(final_score * 0.25, 1),
            "note": "Early policy signals or related documents may appear, but the promise still requires stronger evidence.",
        },
        {
            "date": "2025-06-10",
            "stage": "Structured evidence review",
            "stage_order": 3,
            "progress_score": round(final_score * 0.60, 1),
            "note": "The promise is reviewed using structured parliamentary, governmental, or official evidence.",
        },
        {
            "date": "2026-06-10",
            "stage": "Semi-automatic tracker prototype",
            "stage_order": 4,
            "progress_score": final_score,
            "note": "The tracker combines collected evidence and automatic status suggestions. Final judgement still requires human review.",
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

    all_rows = []

    for _, row in promises.iterrows():
        all_rows.extend(build_timeline_for_promise(row))

    timeline = pd.DataFrame(all_rows)
    timeline.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")

    print(f"Created per-promise timeline file: {OUTPUT_FILE}")
    print(f"Rows created: {len(timeline)}")
    print(timeline.head())


if __name__ == "__main__":
    main()