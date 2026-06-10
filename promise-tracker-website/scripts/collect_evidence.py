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

# -------------------------------------------------
# Smart Filtering Configurations
# -------------------------------------------------
EXCLUDE_KEYWORDS = [
    "debate", 
    "speech", 
    "oral contribution", 
    "written question", 
    "question for short debate", 
    "prime minister's questions", 
    "pmqs",
    "urgent question", 
    "business statement", 
    "procedural",
    "house of commons debate",
    "house of lords debate"
]

def should_exclude(title, text):
    """Returns True if the content matches low-relevance or conversational speech text."""
    combined = (str(title) + " " + str(text)).lower()
    return any(word in combined for word in EXCLUDE_KEYWORDS)

def matches_keywords(title, text, keyword_list):
    """Returns True if at least one exact keyword/phrase from the database is found."""
    combined = (str(title) + " " + str(text)).lower()
    return any(k.lower() in combined for k in keyword_list)


def search_govuk(query, count=5):
    params = {
        "q": query,
        "count": count,
        "order": "-public_timestamp",
    }

    response = requests.get(GOVUK_SEARCH_API, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def search_parliament_bills(query, count=5):
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
        for col in ['evidence_id', 'relevance_score', 'suggested_status',
                    'checked_by_human', 'search_query']:
            if col not in evidence.columns:
                evidence[col] = ''
    else:
        evidence = pd.DataFrame()

    print(f"Promises loaded: {len(promises)}")
    print(f"Existing evidence items loaded: {len(evidence)}")

    new_rows = []

    for _, promise in promises.iterrows():
        promise_id = promise["promise_id"]
        keywords = str(promise["keywords"])

        keyword_list = [k.strip() for k in keywords.split(";") if k.strip()]

        # Space separated search provides cleaner contextual tracking results than commas
        search_query = " ".join(keyword_list[:3]) if keyword_list else "housing"

        print(f"\nSearching sources for {promise_id}: {search_query[:60]}...")

        # -------------------------------------------------
        # 1. GOV.UK Search API
        # -------------------------------------------------
        try:
            govuk_results = search_govuk(search_query, count=5)
            valid_gov_count = 0

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

                # Apply Filtering Protections
                if should_exclude(title, description):
                    print(f"   ⚠️ Skipped conversational debate/speech: {title[:40]}...")
                    continue

                if not matches_keywords(title, description, keyword_list):
                    print(f"   ⚠️ Skipped (no explicit keyword match): {title[:40]}...")
                    continue

                evidence_id = make_evidence_id(len(evidence) + len(new_rows))
                valid_gov_count += 1

                new_rows.append(
                    {
                        "evidence_id": evidence_id,
                        "promise_id": promise_id,
                        "source_type": "GOV.UK Search API",
                        "title": title,
                        "url": url,
                        "date_published": str(public_timestamp)[:10],
                        "evidence_text": description,
                        "relevance_score": 50,
                        "suggested_status": "needs review",
                        "checked_by_human": "no",
                        "search_query": search_query,
                        "collected_at": str(date.today()),
                    }
                )
            print(f"   Added {valid_gov_count} verified GOV.UK items.")

        except Exception as e:
            print(f"GOV.UK search failed for {promise_id}: {e}")

        time.sleep(0.3)

        # -------------------------------------------------
        # 2. UK Parliament Bills API
        # -------------------------------------------------
        bill_query = keyword_list[0] if keyword_list else search_query

        try:
            bill_results = search_parliament_bills(bill_query, count=5)
            valid_bill_count = 0

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

                # Apply Filtering Protections for Bills
                if should_exclude(title, ""):
                    continue

                if not matches_keywords(title, "", keyword_list):
                    continue

                evidence_text = (
                    f"Parliament bill search result. Current house: {current_house}. "
                    f"This may indicate legislative activity related to the promise."
                )

                evidence_id = make_evidence_id(len(evidence) + len(new_rows))
                valid_bill_count += 1

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
            print(f"   Added {valid_bill_count} verified Legislative Bills.")

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
                    "title": f"ONS search results for: {search_query[:60]}",
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
                    "title": f"Legislation.gov.uk search results for: {search_query[:60]}",
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
        print(f"\nAdded {len(new_rows)} highly filtered evidence items.")
    else:
        print("\nNo new relevant evidence found.")

    print("\nDone.")
    print(f"Evidence file updated: {evidence_file}")


if __name__ == "__main__":
    main()
    