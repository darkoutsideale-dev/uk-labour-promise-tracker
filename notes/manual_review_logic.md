# Promise Dataset and Manual Review Logic 

# Commitment Dataset and Manual Review Criteria
This paper describes how Labour's housing pledge dataset was strucutred and how each pledge was manually reviewed and categorized.

## Commitment Dataset Strucuture
This dataset consists of 18 housing related pledges extracted from Labour's 2024 manifesto. Each pledge has been congressional data, legal data, government data, and statistical data.

Each pledge includes the following item:
promise_id: a unique ID from H01 to H18
promise_text: the original housing pledge
topic: the policy area of the promise
keywords: search terms used to identify relevant evidence
evidence_summary: a short explanation of the available evidence
status: the manually reviewed progress category
progress_score: a numerical score representing the level of progress

## Manual Review Criteria
Manual review was necessary because keyword matching alone cannot prove that certain pledges have actually ben fulfilled. Keyword matching can show that a specific topic has been mentioned, but it cannot be seens as meaning actual policy progress or implementation.
Therefore, each pledge was reviewed according to the strength and type of evidence found.
| Status | Score | Meaning |
|---|---:|---|
| Not started | 0 | No relevant official evidence was found. |
| In progress | 50 | Some policy movement, parliamentary discussion, government action, or ongoing reform was found. |
| Implemented | 100 | Evidence of enacted legislation or clear policy implementation was found. |

## Review Principles 
Congressional data were important evidence, but not the only type of evidence. For example, some pledges, such as planning system reform or tenant rights, can be evaluated through legislation or enacted laws. But pledges such as building 1.5 million new homes or reducing homelessness issues require long term evidence such as housing supply statistics, budget documents, government updates, and local government reports.
Therefore, pledges without congressional data were not automatically treated as irrelevant or unfulfilled. Instead, if necesssary, it was indicated as a pledge that should be additionally tracked through other official evidence.