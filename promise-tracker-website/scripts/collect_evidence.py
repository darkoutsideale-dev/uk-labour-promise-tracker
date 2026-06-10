from pathlib import Path
from datetime import date
import pandas as pd
import requests
import time

base = Path(__file__).resolve().parent.parent

promises_file = base / "data" / "promises.csv"
evidence_file = base / "data" / "evidence.csv"

GOVUK_SEARCH_API = "https://www.gov.uk/api/search.json"


def search_govuk(query, count=3):
    params = {
        "q": query,
        "count": count,
        "order": "-public_timestamp",
    }

    response = requests.get(GOVUK_SEARCH_API, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def make_evidence_id(existing_count):
    return f"E{existing_count + 1:04d}"


def main():
    promises = pd.read_csv(promises_file)

    if evidence_file.exists():
        evidence = pd.read_csv(evidence_file)
    else:
        evidence = pd.DataFrame()

    print(f"Promises loaded: {len(promises)}")
    print(f"Existing evidence items loaded: {len(evidence)}")

    new_rows = []

    for _, promise in promises.iterrows():
        promise_id = promise["promise_id"]
        keywords = str(promise["keywords"])

        keyword_list = [k.strip() for k in keywords.split(";") if k.strip()]
        search_query = " ".join(keyword_list[:3])

        print(f"\nSearching GOV.UK for {promise_id}: {search_query}")

        try:
            results = search_govuk(search_query, count=3)
        except Exception as e:
            print(f"Search failed for {promise_id}: {e}")
            continue

        print(f"Found {len(results)} results for {promise_id}")

        for result in results:
            title = result.get("title", "")
            link = result.get("link", "")
            description = result.get("description", "")
            public_timestamp = result.get("public_timestamp", "")

            if link.startswith("http"):
                url = link
            else:
                url = "https://www.gov.uk" + link

            if not evidence.empty and "url" in evidence.columns:
                duplicate = evidence[
                    (evidence["promise_id"] == promise_id)
                    & (evidence["url"] == url)
                ]
                if len(duplicate) > 0:
                    continue

            evidence_id = make_evidence_id(len(evidence) + len(new_rows))

            new_rows.append(
                {
                    "evidence_id": evidence_id,
                    "promise_id": promise_id,
                    "source_type": "GOV.UK Search API",
                    "title": title,
                    "url": url,
                    "date_published": public_timestamp[:10],
                    "evidence_text": description,
                    "relevance_score": 50,
                    "suggested_status": "needs review",
                    "checked_by_human": "no",
                    "search_query": search_query,
                    "collected_at": str(date.today()),
                }
            )

        time.sleep(0.5)

    if new_rows:
        new_evidence = pd.DataFrame(new_rows)

        if evidence.empty:
            updated_evidence = new_evidence
        else:
            updated_evidence = pd.concat([evidence, new_evidence], ignore_index=True)

        updated_evidence.to_csv(evidence_file, index=False, encoding="utf-8")
        print(f"\nAdded {len(new_rows)} new evidence items.")
    else:
        print("\nNo new evidence found.")

    print("\nDone.")
    print(f"Evidence file updated: {evidence_file}")


if __name__ == "__main__":
    main()