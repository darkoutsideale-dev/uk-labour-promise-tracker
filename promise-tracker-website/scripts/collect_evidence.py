from pathlib import Path
from datetime import date
from urllib.parse import quote_plus
import pandas as pd
import requests
import time

base = Path(__file__).resolve().parent.parent

promises_file = base / "data" / "promises.csv"
evidence_file = base / "data" / "evidence.csv"

GOVUK_SEARCH_API = "https://www.gov.uk/api/search.json"
PARLIAMENT_BILLS_API = "https://bills-api.parliament.uk/api/v1/Bills"


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


def search_parliament_bills(query, count=3):
    params = {
        "SearchTerm": query,
        "Take": count,
        "Skip": 0,
    }

    response = requests.get(PARLIAMENT_BILLS_API, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("items", [])


def make_search_link(source, query):
    encoded = quote_plus(query)

    if source == "ONS Search":
        return f"https://www.ons.gov.uk/search?q={encoded}"

    if source == "Legislation.gov.uk Search":
        return f"https://www.legislation.gov.uk/all?title={encoded}"

    if source == "UK Parliament Search":
        return f"https://www.parliament.uk/search/results/?q={encoded}"

    return ""


def make_evidence_id(existing_count):
    return f"E{existing_count + 1:04d}"


def is_duplicate(evidence, promise_id, url):
    if evidence.empty or "url" not in evidence.columns:
        return False

    duplicate = evidence[
        (evidence["promise_id"] == promise_id)
        & (evidence["url"] == url)
    ]

    return len(duplicate) > 0


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

        print(f"\nSearching sources for {promise_id}: {search_query}")

        # -------------------------------------------------
        # 1. GOV.UK Search API
        # -------------------------------------------------
        try:
            govuk_results = search_govuk(search_query, count=3)
            print(f"GOV.UK results: {len(govuk_results)}")

            for result in govuk_results:
                title = result.get("title", "")
                link = result.get("link", "")
                description = result.get("description", "")
                public_timestamp = result.get("public_timestamp", "")

                if link.startswith("http"):
                    url = link
                else:
                    url = "https://www.gov.uk" + link

                if is_duplicate(evidence, promise_id, url):
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

        except Exception as e:
            print(f"GOV.UK search failed for {promise_id}: {e}")

        time.sleep(0.3)

        # -------------------------------------------------
        # 2. UK Parliament Bills API
        # -------------------------------------------------
        try:
            bill_results = search_parliament_bills(search_query, count=3)
            print(f"Parliament Bills results: {len(bill_results)}")

            for item in bill_results:
                bill = item.get("bill", item)

                bill_id = bill.get("billId", "")
                title = bill.get("shortTitle") or bill.get("longTitle") or "Untitled bill"
                current_house = bill.get("currentHouse", "")
                last_update = bill.get("lastUpdate", "")

                if bill_id:
                    url = f"https://bills.parliament.uk/bills/{bill_id}"
                else:
                    url = make_search_link("UK Parliament Search", search_query)

                if is_duplicate(evidence, promise_id, url):
                    continue

                evidence_text = (
                    f"Parliament bill search result. Current house: {current_house}. "
                    f"This may indicate legislative activity related to the promise."
                )

                evidence_id = make_evidence_id(len(evidence) + len(new_rows))

                new_rows.append(
                    {
                        "evidence_id": evidence_id,
                        "promise_id": promise_id,
                        "source_type": "UK Parliament Bills API",
                        "title": title,
                        "url": url,
                        "date_published": str(last_update)[:10],
                        "evidence_text": evidence_text,
                        "relevance_score": 60,
                        "suggested_status": "needs review",
                        "checked_by_human": "no",
                        "search_query": search_query,
                        "collected_at": str(date.today()),
                    }
                )

        except Exception as e:
            print(f"Parliament Bills search failed for {promise_id}: {e}")

        time.sleep(0.3)

        # -------------------------------------------------
        # 3. ONS Search Link
        # -------------------------------------------------
        ons_url = make_search_link("ONS Search", search_query)

        if not is_duplicate(evidence, promise_id, ons_url):
            evidence_id = make_evidence_id(len(evidence) + len(new_rows))

            new_rows.append(
                {
                    "evidence_id": evidence_id,
                    "promise_id": promise_id,
                    "source_type": "ONS Search",
                    "title": f"ONS search results for: {search_query}",
                    "url": ons_url,
                    "date_published": "",
                    "evidence_text": "Search link for related ONS housing statistics and datasets. This source is useful for tracking measurable outcomes such as housing supply, rents, prices, and homelessness indicators.",
                    "relevance_score": 40,
                    "suggested_status": "needs review",
                    "checked_by_human": "no",
                    "search_query": search_query,
                    "collected_at": str(date.today()),
                }
            )

        # -------------------------------------------------
        # 4. Legislation.gov.uk Search Link
        # -------------------------------------------------
        legislation_url = make_search_link("Legislation.gov.uk Search", search_query)

        if not is_duplicate(evidence, promise_id, legislation_url):
            evidence_id = make_evidence_id(len(evidence) + len(new_rows))

            new_rows.append(
                {
                    "evidence_id": evidence_id,
                    "promise_id": promise_id,
                    "source_type": "Legislation.gov.uk Search",
                    "title": f"Legislation.gov.uk search results for: {search_query}",
                    "url": legislation_url,
                    "date_published": "",
                    "evidence_text": "Search link for enacted UK legislation related to this promise. This source helps check whether a policy promise has moved from proposal or bill stage into formal law.",
                    "relevance_score": 45,
                    "suggested_status": "needs review",
                    "checked_by_human": "no",
                    "search_query": search_query,
                    "collected_at": str(date.today()),
                }
            )

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