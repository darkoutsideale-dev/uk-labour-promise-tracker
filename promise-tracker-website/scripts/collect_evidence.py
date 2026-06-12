from pathlib import Path
from datetime import date
from urllib.parse import quote_plus
import pandas as pd
import requests
import time
import re

# -------------------------------------------------
# Paths
# -------------------------------------------------
base = Path(__file__).resolve().parent.parent

promises_file = base / "data" / "promises.csv"
evidence_file = base / "data" / "evidence.csv"

GOVUK_SEARCH_API = "https://www.gov.uk/api/search.json"
PARLIAMENT_BILLS_API = "https://bills-api.parliament.uk/api/v1/Bills"


# -------------------------------------------------
# Filtering configuration
# -------------------------------------------------
CLEARLY_IRRELEVANT_TERMS = [
    "employment tribunal",
    "tribunal decision",
    "carcinogenicity",
    "chemicals in food",
    "consumer products",
    "trade remedies",
    "case management",
    "electric vehicle",
    "chargepoint",
    "levi",
    "radioactive",
    "radiation",
    "dounreay",
    "aviation",
    "aircraft",
    "night noise",
    "sleep disturbance",
    "nuclear",
    "veterinary",
    "marine licence",
    "fishing",
    "school meals",
    "nhs",
    "covid",
    "rail",
    "bus service",
    "animal disease",
    "bovine",
    "pesticide",
    "export health certificate",
    "food standards",
    "tax tribunal",
    "upper tribunal",
    "court of appeal",
]

LOW_RELEVANCE_PARLIAMENT_TERMS = [
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
    "house of lords debate",
]

HOUSING_RELEVANT_TERMS = [
    "housing",
    "housebuilding",
    "house building",
    "homes",
    "new homes",
    "affordable housing",
    "social housing",
    "social rented",
    "council housing",
    "rented homes",
    "renters",
    "tenants",
    "landlord",
    "private rented sector",
    "eviction",
    "section 21",
    "awaab",
    "leasehold",
    "freehold",
    "commonhold",
    "ground rent",
    "fleecehold",
    "planning",
    "local plan",
    "local plans",
    "nppf",
    "national planning policy framework",
    "brownfield",
    "green belt",
    "grey belt",
    "golden rules",
    "mortgage",
    "first-time buyer",
    "first time buyer",
    "homelessness",
    "rough sleeping",
    "cladding",
    "building safety",
    "compulsory purchase",
    "right to buy",
    "stamp duty",
    "housing supply",
    "affordable homes programme",
]


# -------------------------------------------------
# Helper functions
# -------------------------------------------------
def normalise_text(text):
    if pd.isna(text):
        return ""
    return str(text).lower()


def text_tokens(text):
    text = normalise_text(text)
    tokens = re.split(r"[^a-zA-Z0-9]+", text)
    return [t for t in tokens if len(t) >= 4]


def build_keyword_list(keywords):
    return [k.strip() for k in str(keywords).split(";") if k.strip()]


def build_search_query(promise):
    keyword_list = build_keyword_list(promise.get("keywords", ""))
    promise_text = str(promise.get("promise_text", ""))

    if len(keyword_list) >= 3:
        query = " ".join(keyword_list[:3])
    elif len(keyword_list) > 0:
        query = " ".join(keyword_list)
    else:
        query = promise_text[:120]

    if "housing" not in query.lower() and "homes" not in query.lower():
        query = query + " housing"

    return query.strip()


def contains_any(text, terms):
    text = normalise_text(text)
    return any(term in text for term in terms)


def result_has_housing_relevance(title, description):
    """
    IMPORTANT:
    Only judge the evidence result itself.
    Do not count search_query or promise_text here,
    otherwise irrelevant results can be falsely upgraded.
    """
    result_text = f"{title} {description}".lower()
    return sum(1 for term in HOUSING_RELEVANT_TERMS if term in result_text)


def result_has_keyword_match(title, description, keyword_list):
    """
    Check whether the result itself contains promise-specific keywords.
    We ignore very broad single words to avoid weak matches.
    """
    result_text = f"{title} {description}".lower()

    broad_words = {
        "local",
        "authority",
        "authorities",
        "funding",
        "development",
        "reform",
        "review",
        "policy",
        "strategy",
        "community",
        "environmental",
    }

    useful_keywords = []

    for keyword in keyword_list:
        k = keyword.lower().strip()

        if len(k) < 4:
            continue

        # Keep phrase keywords
        if " " in k:
            useful_keywords.append(k)
            continue

        # Remove overly broad single-word keywords
        if k not in broad_words:
            useful_keywords.append(k)

    hits = [k for k in useful_keywords if k in result_text]
    return hits


def assess_govuk_relevance(title, description, keyword_list):
    """
    Strict relevance filter for GOV.UK search results.
    Keeps only evidence that is clearly related to housing/promise keywords.
    """
    result_text = f"{title} {description}".lower()

    if contains_any(result_text, CLEARLY_IRRELEVANT_TERMS):
        return "no", 5, "Filtered out because it contains clearly irrelevant terms."

    if contains_any(result_text, LOW_RELEVANCE_PARLIAMENT_TERMS):
        return "no", 10, "Filtered out because it appears to be debate, speech, or procedural content."

    housing_hits = result_has_housing_relevance(title, description)
    keyword_hits = result_has_keyword_match(title, description, keyword_list)

    # Strong match
    if housing_hits >= 1 and len(keyword_hits) >= 1:
        return "yes", 85, "Relevant: result contains housing-related terms and promise-specific keywords."

    # Still useful if clearly housing-related
    if housing_hits >= 2:
        return "yes", 75, "Relevant: result contains multiple housing-related terms."

    # Maybe useful if phrase keyword matches
    phrase_hits = [k for k in keyword_hits if " " in k]
    if len(phrase_hits) >= 1:
        return "maybe", 60, "Possibly relevant: result contains a promise-specific phrase."

    return "no", 10, "Filtered out because the result is not clearly related to the promise."


def assess_parliament_relevance(title, evidence_text, keyword_list):
    result_text = f"{title} {evidence_text}".lower()

    if contains_any(result_text, CLEARLY_IRRELEVANT_TERMS):
        return "no", 5, "Filtered out because it contains clearly irrelevant terms."

    if contains_any(result_text, LOW_RELEVANCE_PARLIAMENT_TERMS):
        return "no", 10, "Filtered out because it appears to be debate, speech, or procedural content."

    housing_hits = result_has_housing_relevance(title, evidence_text)
    keyword_hits = result_has_keyword_match(title, evidence_text, keyword_list)

    if housing_hits >= 1 and len(keyword_hits) >= 1:
        return "yes", 85, "Relevant bill: housing-related terms and promise keywords found."

    if housing_hits >= 2:
        return "yes", 75, "Relevant bill: multiple housing-related terms found."

    if len(keyword_hits) >= 1:
        return "maybe", 60, "Possibly relevant bill, needs human review."

    return "no", 10, "Filtered out because this bill is not clearly promise-related."


# -------------------------------------------------
# API functions
# -------------------------------------------------
def search_govuk(query, count=8):
    params = {
        "q": query,
        "count": count,
        "order": "-public_timestamp",
    }

    response = requests.get(GOVUK_SEARCH_API, params=params, timeout=25)
    response.raise_for_status()

    data = response.json()
    return data.get("results", [])


def search_parliament_bills(query, count=5):
    params = {
        "SearchTerm": query,
        "Take": count,
        "Skip": 0,
    }

    response = requests.get(PARLIAMENT_BILLS_API, params=params, timeout=25)
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
        (evidence["promise_id"].astype(str) == str(promise_id))
        & (evidence["url"].astype(str) == str(url))
    ]

    return len(duplicate) > 0


def append_evidence(
    new_rows,
    evidence,
    promise_id,
    source_type,
    title,
    url,
    date_published,
    evidence_text,
    relevance_score,
    suggested_status,
    checked_by_human,
    search_query,
    is_relevant,
    review_note,
):
    if is_duplicate(evidence, promise_id, url):
        return False

    evidence_id = make_evidence_id(len(evidence) + len(new_rows))

    new_rows.append(
        {
            "evidence_id": evidence_id,
            "promise_id": promise_id,
            "source_type": source_type,
            "title": title,
            "url": url,
            "date_published": date_published,
            "evidence_text": evidence_text,
            "relevance_score": relevance_score,
            "suggested_status": suggested_status,
            "checked_by_human": checked_by_human,
            "is_relevant": is_relevant,
            "review_note": review_note,
            "search_query": search_query,
            "collected_at": str(date.today()),
        }
    )

    return True


def clean_existing_evidence(evidence, promises):
    """
    Re-check existing evidence and remove clear noise.
    """
    if evidence.empty:
        return evidence

    evidence = evidence.copy()

    for col in [
        "evidence_id",
        "relevance_score",
        "suggested_status",
        "checked_by_human",
        "search_query",
        "is_relevant",
        "review_note",
        "collected_at",
    ]:
        if col not in evidence.columns:
            evidence[col] = ""

    promise_lookup = promises.set_index("promise_id").to_dict("index")

    relevance_values = []
    score_values = []
    note_values = []

    for _, row in evidence.iterrows():
        promise_id = row.get("promise_id", "")
        source_type = str(row.get("source_type", ""))
        title = row.get("title", "")
        evidence_text = row.get("evidence_text", "")
        search_query = row.get("search_query", "")

        promise_info = promise_lookup.get(promise_id, {})
        keyword_list = build_keyword_list(promise_info.get("keywords", ""))

        checked_by_human = str(row.get("checked_by_human", "")).lower().strip()
        old_relevance = str(row.get("is_relevant", "")).lower().strip()

        if checked_by_human == "yes" and old_relevance in ["yes", "maybe"]:
            is_relevant = old_relevance
            score = row.get("relevance_score", 70)
            note = row.get("review_note", "Human-reviewed evidence retained.")
        elif source_type.lower() == "gov.uk search api":
            is_relevant, score, note = assess_govuk_relevance(
                title,
                evidence_text,
                keyword_list,
            )
        elif source_type.lower() == "uk parliament bills api":
            is_relevant, score, note = assess_parliament_relevance(
                title,
                evidence_text,
                keyword_list,
            )
        elif source_type.lower() in ["ons search", "legislation.gov.uk search"]:
            is_relevant = "maybe"
            score = 50
            note = "Official search link retained for manual checking."
        else:
            # Unknown source types are kept only if they are not clearly irrelevant.
            combined = f"{title} {evidence_text}".lower()
            if contains_any(combined, CLEARLY_IRRELEVANT_TERMS):
                is_relevant = "no"
                score = 5
                note = "Filtered out because it contains clearly irrelevant terms."
            else:
                is_relevant = "maybe"
                score = 40
                note = "Unknown source type, needs human review."

        relevance_values.append(is_relevant)
        score_values.append(score)
        note_values.append(note)

    evidence["is_relevant"] = relevance_values
    evidence["relevance_score"] = score_values
    evidence["review_note"] = note_values

    before = len(evidence)

    evidence = evidence[
        evidence["is_relevant"].astype(str).str.lower().isin(["yes", "maybe"])
    ].copy()

    if "url" in evidence.columns:
        evidence = evidence.drop_duplicates(
            subset=["promise_id", "url"],
            keep="first",
        )

    after = len(evidence)

    print(f"Existing evidence cleaned: {before} -> {after} kept.")

    return evidence


# -------------------------------------------------
# Main
# -------------------------------------------------
def main():
    promises = pd.read_csv(promises_file)

    if evidence_file.exists():
        evidence = pd.read_csv(evidence_file)
    else:
        evidence = pd.DataFrame()

    print(f"Promises loaded: {len(promises)}")
    print(f"Existing evidence items loaded: {len(evidence)}")

    # Important: clean old noisy evidence first
    evidence = clean_existing_evidence(evidence, promises)

    new_rows = []

    for _, promise in promises.iterrows():
        promise_id = promise["promise_id"]
        keyword_list = build_keyword_list(promise.get("keywords", ""))
        search_query = build_search_query(promise)

        print(f"\nSearching sources for {promise_id}: {search_query[:80]}")

        # -------------------------------------------------
        # 1. GOV.UK Search API
        # -------------------------------------------------
        try:
            govuk_results = search_govuk(search_query, count=8)
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

                is_relevant, relevance_score, review_note = assess_govuk_relevance(
                    title,
                    description,
                    keyword_list,
                )

                if is_relevant == "no":
                    print(f"   Skipped irrelevant GOV.UK result: {title[:70]}")
                    continue

                added = append_evidence(
                    new_rows=new_rows,
                    evidence=evidence,
                    promise_id=promise_id,
                    source_type="GOV.UK Search API",
                    title=title,
                    url=url,
                    date_published=str(public_timestamp)[:10],
                    evidence_text=description,
                    relevance_score=relevance_score,
                    suggested_status="needs review",
                    checked_by_human="no",
                    search_query=search_query,
                    is_relevant=is_relevant,
                    review_note=review_note,
                )

                if added:
                    valid_gov_count += 1

            print(f"   Added {valid_gov_count} filtered GOV.UK items.")

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

                evidence_text = (
                    f"Parliament bill search result. Current house: {current_house}. "
                    f"This may indicate legislative activity related to the promise, "
                    f"but it still requires human review."
                )

                is_relevant, relevance_score, review_note = assess_parliament_relevance(
                    title,
                    evidence_text,
                    keyword_list,
                )

                if is_relevant == "no":
                    print(f"   Skipped irrelevant Parliament result: {title[:70]}")
                    continue

                added = append_evidence(
                    new_rows=new_rows,
                    evidence=evidence,
                    promise_id=promise_id,
                    source_type="UK Parliament Bills API",
                    title=title,
                    url=url,
                    date_published=str(last_update)[:10],
                    evidence_text=evidence_text,
                    relevance_score=max(int(relevance_score), 60),
                    suggested_status="needs review",
                    checked_by_human="no",
                    search_query=search_query,
                    is_relevant=is_relevant,
                    review_note=review_note,
                )

                if added:
                    valid_bill_count += 1

            print(f"   Added {valid_bill_count} filtered Parliament Bill items.")

        except Exception as e:
            print(f"Parliament Bills search failed for {promise_id}: {e}")

        time.sleep(0.3)

        # -------------------------------------------------
        # 3. ONS Search Link
        # -------------------------------------------------
        ons_url = make_search_link("ONS Search", search_query)

        added = append_evidence(
            new_rows=new_rows,
            evidence=evidence,
            promise_id=promise_id,
            source_type="ONS Search",
            title=f"ONS search results for: {search_query[:80]}",
            url=ons_url,
            date_published="",
            evidence_text=(
                "Search link for related ONS housing statistics and datasets. "
                "This source is useful for tracking measurable outcomes such as housing supply, "
                "rents, prices, and homelessness indicators."
            ),
            relevance_score=50,
            suggested_status="needs review",
            checked_by_human="no",
            search_query=search_query,
            is_relevant="maybe",
            review_note="Statistical source link. Needs manual checking before being used as evidence.",
        )

        if added:
            print("   Added ONS search link.")

        # -------------------------------------------------
        # 4. Legislation.gov.uk Search Link
        # -------------------------------------------------
        legislation_url = make_search_link("Legislation.gov.uk Search", search_query)

        added = append_evidence(
            new_rows=new_rows,
            evidence=evidence,
            promise_id=promise_id,
            source_type="Legislation.gov.uk Search",
            title=f"Legislation.gov.uk search results for: {search_query[:80]}",
            url=legislation_url,
            date_published="",
            evidence_text=(
                "Search link for enacted UK legislation related to this promise. "
                "This source helps check whether a policy promise has moved from proposal "
                "or bill stage into formal law."
            ),
            relevance_score=55,
            suggested_status="needs review",
            checked_by_human="no",
            search_query=search_query,
            is_relevant="maybe",
            review_note="Legislation search link. Needs manual checking before being used as evidence.",
        )

        if added:
            print("   Added Legislation.gov.uk search link.")

    # -------------------------------------------------
    # Save
    # -------------------------------------------------
    if new_rows:
        new_evidence = pd.DataFrame(new_rows)
        updated_evidence = pd.concat([evidence, new_evidence], ignore_index=True)
        print(f"\nAdded {len(new_rows)} new filtered evidence items.")
    else:
        updated_evidence = evidence
        print("\nNo new relevant evidence found.")

    if "url" in updated_evidence.columns:
        updated_evidence = updated_evidence.drop_duplicates(
            subset=["promise_id", "url"],
            keep="first",
        )

    updated_evidence.to_csv(evidence_file, index=False, encoding="utf-8")

    print(f"Total evidence items now: {len(updated_evidence)}")
    print("\nDone.")
    print(f"Evidence file updated: {evidence_file}")


if __name__ == "__main__":
    main()