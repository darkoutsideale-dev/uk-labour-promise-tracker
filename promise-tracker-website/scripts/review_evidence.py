from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_EVIDENCE_FILE = BASE_DIR / "data" / "evidence.csv"
REVIEWED_EVIDENCE_FILE = BASE_DIR / "data" / "evidence_reviewed.csv"


# -------------------------------------------------
# Manual review rules
# -------------------------------------------------
# Use lowercase matching. The script checks whether the title contains the pattern.
# keep = yes / maybe / no
# yes = clearly relevant
# maybe = weak/background/needs checking
# no = remove from dashboard
MANUAL_REVIEW_RULES = [
    # H02 / H03 planning
    {
        "promise_id": "H02",
        "title_contains": "planning and infrastructure act",
        "keep": "yes",
        "note": "Directly relevant to planning reform and planning system changes.",
        "description": "Official legislation related to planning reform, infrastructure, NPPF updates, compulsory purchase reform, and development corporations.",
    },
    {
        "promise_id": "H03",
        "title_contains": "planning and infrastructure act",
        "keep": "yes",
        "note": "Relevant to planning reform and local planning system changes.",
        "description": "Official legislation related to planning reform, infrastructure, local plans, compulsory purchase reform, and development corporations.",
    },
    {
        "promise_id": "H02",
        "title_contains": "planning policy framework",
        "keep": "yes",
        "note": "Directly relevant to NPPF and mandatory housing targets.",
        "description": "The National Planning Policy Framework sets out the government planning policies for England and is relevant to housing targets and planning reform.",
    },
    {
        "promise_id": "H03",
        "title_contains": "planning policy framework",
        "keep": "yes",
        "note": "Relevant to Local Plans and the presumption in favour of development.",
        "description": "The National Planning Policy Framework provides the policy framework for local planning authorities and development decisions.",
    },
    {
        "promise_id": "H03",
        "title_contains": "local planning authorities (energy and energy efficiency)",
        "keep": "no",
        "note": "Not relevant: this bill concerns energy efficiency, not housing targets or local plans.",
        "description": "",
    },
    {
        "promise_id": "H03",
        "title_contains": "local planning authorities (protection of local services)",
        "keep": "no",
        "note": "Not relevant: this bill concerns local services, not housing delivery or local plans.",
        "description": "",
    },
    {
        "promise_id": "H03",
        "title_contains": "local plans (burial space)",
        "keep": "no",
        "note": "Not relevant: burial space is not related to housing planning promises.",
        "description": "",
    },

    # H07 social and affordable housing
    {
        "promise_id": "H07",
        "title_contains": "carers bedroom entitlement",
        "keep": "maybe",
        "note": "Weakly relevant: related to social housing, but not direct evidence for increasing social and affordable housing supply.",
        "description": "Parliamentary bill related to bedroom entitlement in the social housing sector. This is only weakly related to wider social housing supply promises.",
    },
    {
        "promise_id": "H07",
        "title_contains": "prevention of social housing fraud act 2013",
        "keep": "no",
        "note": "Not relevant: older legislation on fraud, not evidence for Labour's 2024 housing promise.",
        "description": "",
    },

    # H09 / H10 first-time buyers and mortgage
    {
        "promise_id": "H09",
        "title_contains": "first-time buyers and mortgage guarantee",
        "keep": "yes",
        "note": "Relevant to first-time buyers and mortgage access.",
        "description": "Government information related to first-time buyers and the mortgage guarantee scheme.",
    },
    {
        "promise_id": "H10",
        "title_contains": "first-time buyers and mortgage guarantee",
        "keep": "yes",
        "note": "Directly relevant to the permanent mortgage guarantee scheme promise.",
        "description": "Government information on the mortgage guarantee scheme for buyers with small deposits.",
    },

    # H11 / H12 renters
    {
        "promise_id": "H11",
        "title_contains": "renters' rights act",
        "keep": "yes",
        "note": "Directly relevant to abolishing Section 21 and strengthening renters' rights.",
        "description": "Official legislation that abolishes Section 21 no-fault evictions and introduces stronger rights for renters.",
    },
    {
        "promise_id": "H12",
        "title_contains": "renters' rights act",
        "keep": "yes",
        "note": "Relevant to renters' legal rights, including rent increase challenges.",
        "description": "Official legislation introducing stronger legal rights for renters, including protections related to rent increases.",
    },
    {
        "promise_id": "H11",
        "title_contains": "private rented sector reform",
        "keep": "yes",
        "note": "Relevant government policy evidence for private rented sector reform.",
        "description": "Government guide explaining the Renters' Rights Bill and proposed reforms for private renters.",
    },
    {
        "promise_id": "H12",
        "title_contains": "private rented sector reform",
        "keep": "yes",
        "note": "Relevant to renters' rights and rent increase protections.",
        "description": "Government guide explaining reforms in the private rented sector, including stronger rights for renters.",
    },

    # H13 leasehold reform
    {
        "promise_id": "H13",
        "title_contains": "leasehold reform (amendment) act",
        "keep": "maybe",
        "note": "Relevant to leasehold reform, but not direct evidence for banning new leasehold flats or making commonhold default.",
        "description": "Legislation related to leasehold reform. It is useful background evidence but does not fully prove the core promise has been implemented.",
    },
    {
        "promise_id": "H13",
        "title_contains": "leasehold reform (disclosure and insurance commissions)",
        "keep": "maybe",
        "note": "Weakly relevant to leasehold reform; stronger relevance for H14 charges and commissions.",
        "description": "Parliamentary bill related to leasehold disclosure and insurance commissions. This is relevant to leasehold reform but needs human review.",
    },
    {
        "promise_id": "H13",
        "title_contains": "leasehold reform (forfeiture)",
        "keep": "maybe",
        "note": "Related to leasehold reform, but not the central promise on commonhold/default tenure.",
        "description": "Parliamentary bill related to leasehold forfeiture. It is connected to leasehold reform but is not direct evidence for the whole H13 promise.",
    },
    {
        "promise_id": "H13",
        "title_contains": "leasehold reform (tribunal judgments and legal costs)",
        "keep": "maybe",
        "note": "Related to leasehold legal reform, but not direct evidence for commonhold default or banning leasehold flats.",
        "description": "Parliamentary bill related to leasehold tribunal judgments and legal costs. It is weakly relevant and needs human review.",
    },
    {
        "promise_id": "H13",
        "title_contains": "leaseholder remediation",
        "keep": "no",
        "note": "Not suitable for H13: this is more about building safety/remediation than leasehold tenure reform.",
        "description": "",
    },
    {
        "promise_id": "H13",
        "title_contains": "telecommunications infrastructure",
        "keep": "no",
        "note": "Not relevant: telecommunications infrastructure is not housing leasehold reform.",
        "description": "",
    },
    {
        "promise_id": "H13",
        "title_contains": "leasehold and freehold reform act 2024",
        "keep": "maybe",
        "note": "Relevant background legislation, but it predates the Labour 2024 government and does not prove full implementation of the promise.",
        "description": "The Leasehold and Freehold Reform Act 2024 is relevant background for leasehold reform, but it should not be treated as full evidence of Labour's later promise implementation.",
    },

    # H14 ground rents / charges
    {
        "promise_id": "H14",
        "title_contains": "leasehold reform (amendment) act",
        "keep": "maybe",
        "note": "Related to leasehold reform, but not direct evidence for ground rents or fleecehold charges.",
        "description": "Legislation related to leasehold reform. It may be relevant to leasehold charges but needs human review.",
    },
    {
        "promise_id": "H14",
        "title_contains": "leasehold reform (disclosure and insurance commissions)",
        "keep": "yes",
        "note": "Relevant to unfair leasehold costs and insurance commissions.",
        "description": "Parliamentary bill related to disclosure and insurance commissions in leasehold properties, relevant to unfair leasehold charges.",
    },
    {
        "promise_id": "H14",
        "title_contains": "leasehold reform (forfeiture)",
        "keep": "maybe",
        "note": "Related to leasehold reform, but not directly about ground rents or fleecehold charges.",
        "description": "Parliamentary bill related to leasehold forfeiture. It is weakly relevant to wider leasehold reform.",
    },
    {
        "promise_id": "H14",
        "title_contains": "leasehold reform (reasonableness of service charges)",
        "keep": "yes",
        "note": "Directly relevant to unfair service charges and leasehold costs.",
        "description": "Parliamentary bill related to the reasonableness of service charges in leasehold properties, relevant to unfair leasehold charges.",
    },
    {
        "promise_id": "H14",
        "title_contains": "leasehold reform (tribunal judgments and legal costs)",
        "keep": "maybe",
        "note": "Related to leasehold legal costs, but not direct evidence for ground rent caps.",
        "description": "Parliamentary bill related to leasehold tribunal judgments and legal costs. It is relevant to leasehold costs but needs human review.",
    },
    {
        "promise_id": "H14",
        "title_contains": "telecommunications infrastructure",
        "keep": "no",
        "note": "Not relevant to ground rents, service charges, or fleecehold estate charges.",
        "description": "",
    },
    {
        "promise_id": "H14",
        "title_contains": "leasehold and freehold reform act 2024",
        "keep": "maybe",
        "note": "Relevant background legislation, but it predates the Labour 2024 government.",
        "description": "The Leasehold and Freehold Reform Act 2024 made changes to leasehold and freehold rules, but it should be treated as background evidence rather than full implementation of H14.",
    },

    # H16 building safety / cladding
    {
        "promise_id": "H16",
        "title_contains": "building safety act 2022",
        "keep": "maybe",
        "note": "Relevant background evidence for building safety, but it predates Labour 2024 and does not prove accelerated remediation.",
        "description": "The Building Safety Act 2022 is relevant background legislation for building safety and remediation, but it is not direct evidence of Labour accelerating cladding remediation.",
    },
    {
        "promise_id": "H16",
        "title_contains": "fire and building safety (public inquiry)",
        "keep": "no",
        "note": "Weak connection only; public inquiry is not direct evidence of cladding remediation or developer payment.",
        "description": "",
    },
]


GENERAL_REMOVE_PATTERNS = [
    "employment tribunal",
    "tribunal decision",
    "carcinogenicity",
    "chemicals in food",
    "consumer products",
    "trade remedies",
    "case management",
    "electric vehicle",
    "chargepoint",
    "radioactive",
    "aviation",
    "night noise",
    "sleep disturbance",
    "burial space",
    "energy efficiency",
    "local services",
    "telecommunications infrastructure",
]


def clean_text_value(value):
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.lower() in ["nan", "none", "null"]:
        return ""
    return text


def normalise_url(url):
    url = clean_text_value(url)
    if not url:
        return ""
    return url.split("?")[0].rstrip("/").lower()


def apply_manual_review(row):
    promise_id = clean_text_value(row.get("promise_id"))
    title = clean_text_value(row.get("title")).lower()
    evidence_text = clean_text_value(row.get("evidence_text"))

    for rule in MANUAL_REVIEW_RULES:
        if promise_id == rule["promise_id"] and rule["title_contains"] in title:
            return rule["keep"], rule["note"], rule["description"]

    # General remove rule
    combined = f"{title} {evidence_text}".lower()
    for pattern in GENERAL_REMOVE_PATTERNS:
        if pattern in combined:
            return "no", f"Removed because it matches irrelevant pattern: {pattern}", ""

    # Keep existing relevance if available
    existing_relevance = clean_text_value(row.get("is_relevant")).lower()
    if existing_relevance in ["yes", "maybe", "no"]:
        return existing_relevance, clean_text_value(row.get("review_note")), ""

    return "maybe", "Needs manual checking.", ""


def build_fallback_description(row):
    title = clean_text_value(row.get("title"))
    source_type = clean_text_value(row.get("source_type"))
    suggested_status = clean_text_value(row.get("suggested_status"))
    review_note = clean_text_value(row.get("review_note"))

    title_lower = title.lower()

    if "planning policy framework" in title_lower:
        return "The National Planning Policy Framework sets out government planning policies for England and is relevant to housing targets, local plans, and planning reform."

    if "planning and infrastructure act" in title_lower:
        return "Official legislation related to planning reform, infrastructure, compulsory purchase, and the planning system."

    if "renters' rights" in title_lower:
        return "Official evidence related to renters' rights, Section 21 no-fault evictions, and private rented sector reform."

    if "private rented sector" in title_lower:
        return "Government information about reforms to the private rented sector and renters' rights."

    if "mortgage guarantee" in title_lower or "first-time buyers" in title_lower:
        return "Government information related to first-time buyers and the mortgage guarantee scheme."

    if "leasehold and freehold reform act" in title_lower:
        return "Official legislation related to leasehold and freehold reform. It is useful background evidence but may not prove full implementation of Labour's later promise."

    if "leasehold reform" in title_lower:
        return "Parliamentary evidence related to leasehold reform. This source may require human review to confirm its relevance to the specific promise."

    if "building safety act" in title_lower:
        return "Official building safety legislation relevant as background evidence for cladding and remediation policy."

    if "building safety" in title_lower or "cladding" in title_lower:
        return "Official evidence related to building safety or cladding remediation. Human review is needed to confirm whether it supports the promise."

    if source_type:
        return f"{source_type} item related to this promise. Human review is needed to confirm its relevance."

    if review_note:
        return review_note

    return "No short description was available. Open the official source for more details."


def main():
    if not RAW_EVIDENCE_FILE.exists():
        print(f"No evidence file found: {RAW_EVIDENCE_FILE}")
        return

    evidence = pd.read_csv(RAW_EVIDENCE_FILE)

    print(f"Original evidence rows: {len(evidence)}")

    # Ensure required columns exist
    for col in [
        "is_relevant",
        "review_note",
        "evidence_text",
        "date_published",
        "url",
        "title",
        "promise_id",
        "source_type",
        "suggested_status",
    ]:
        if col not in evidence.columns:
            evidence[col] = ""

    reviewed_labels = []
    review_notes = []
    manual_descriptions = []

    for _, row in evidence.iterrows():
        keep, note, description = apply_manual_review(row)
        reviewed_labels.append(keep)
        review_notes.append(note)
        manual_descriptions.append(description)

    evidence["is_relevant"] = reviewed_labels
    evidence["review_note"] = review_notes
    evidence["manual_description"] = manual_descriptions

    # Remove no
    reviewed = evidence[
        evidence["is_relevant"].astype(str).str.lower().isin(["yes", "maybe"])
    ].copy()

    # Clean nan descriptions
    final_descriptions = []

    for _, row in reviewed.iterrows():
        existing_text = clean_text_value(row.get("evidence_text"))
        manual_description = clean_text_value(row.get("manual_description"))

        if manual_description:
            final_descriptions.append(manual_description)
        elif existing_text:
            final_descriptions.append(existing_text)
        else:
            final_descriptions.append(build_fallback_description(row))

    reviewed["evidence_text"] = final_descriptions

    # Clean dates
    reviewed["date_published"] = reviewed["date_published"].apply(
        lambda x: "Not available" if clean_text_value(x) == "" else clean_text_value(x)
    )

    # Deduplicate within the same promise by URL
    reviewed["normalized_url"] = reviewed["url"].apply(normalise_url)

    before_dedup = len(reviewed)

    reviewed = reviewed.drop_duplicates(
        subset=["promise_id", "normalized_url"],
        keep="first"
    ).copy()

    after_dedup = len(reviewed)

    # Add a global duplicate flag, so the website can count unique sources fairly
    reviewed["global_source_key"] = reviewed["normalized_url"]
    reviewed["is_duplicate_global_source"] = reviewed.duplicated(
        subset=["global_source_key"],
        keep="first"
    )

    # Remove helper column if you do not want to show it
    # Keep normalized_url and global_source_key because they are useful for debugging/counting.
    reviewed.to_csv(REVIEWED_EVIDENCE_FILE, index=False, encoding="utf-8")

    print(f"Rows after relevance review: {len(reviewed)}")
    print(f"Removed as irrelevant: {len(evidence) - len(evidence[evidence['is_relevant'].isin(['yes', 'maybe'])])}")
    print(f"Removed as duplicate within promise: {before_dedup - after_dedup}")
    print(f"Reviewed evidence saved to: {REVIEWED_EVIDENCE_FILE}")


if __name__ == "__main__":
    main()