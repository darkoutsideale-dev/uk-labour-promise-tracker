# Task 5 Notes: Government, Budget, and Statistical Evidence

## Goal

This task collects UK government, budget, and statistical evidence related to housing policy. The purpose is to create an evidence base that can be linked to specific Labour 2024 housing promises.

This part of the project focuses on sources that can help track whether promises are followed by policy action, funding, legal change, or measurable housing outcomes.

## Source types collected

The current evidence table includes three main types of sources:

- **Government policy documents**
- **Government funding or budget documents**
- **Official statistics**

These sources were collected because they can support different parts of the promise tracking process. Some sources show policy action, while others provide measurable indicators of housing outcomes.

## Main evidence areas

The evidence sources mainly cover:

- housing supply and housebuilding
- planning reform
- social and affordable housing
- renters' rights
- leasehold and ground rent reform
- first-time buyers and mortgage guarantee

## Link to promise dataset

After the first version of the promise dataset was created, I linked the outcome evidence sources to relevant promise IDs.

The current evidence table includes 12 sources and links them to relevant housing promises. For example:

- **H01 and H07** are linked to housing supply and housebuilding evidence.
- **H02, H03, and H05** are linked to planning reform and local planning evidence.
- **H07 and H08** are linked to social and affordable housing evidence.
- **H11 and H12** are linked to renters' rights and rent increase evidence.
- **H13 and H14** are linked to leasehold and ground rent reform evidence.
- **H09 and H10** are linked to first-time buyer and mortgage guarantee evidence.

## Dataset created

The main output of this task is:

- `data/processed/outcome_evidence.csv`

This dataset contains the following information:

- evidence ID
- linked promise IDs
- policy area
- source type
- source name
- source URL
- indicator name
- geography
- time period
- value or description
- relevance to the promise
- notes

## Notebook work

The notebook used for this task is:

- `notebooks/05_government_budget_statistics_evidence.ipynb`

The notebook reads the outcome evidence dataset, checks its shape, counts the different source types, checks which promise IDs are covered, and creates a simple bar chart showing the types of evidence sources collected.

## Current findings

At this stage, the outcome evidence dataset contains:

- 12 evidence sources
- government policy sources
- government funding sources
- official statistics sources

The evidence sources are not all the same type. Some sources are useful for tracking actual measurable outcomes, such as housing supply and housebuilding statistics. Other sources are useful for identifying policy action, such as planning reform documents or renters' rights policy documents.

## Limitations

This evidence table is still preliminary.

Some sources are policy or funding evidence rather than final outcome evidence. This means that they can show that the government has taken action, but they do not always prove that a promise has been fully achieved.

Some promises are also broad or long-term, so they cannot be judged only through one source. For example, a promise about increasing housebuilding may need both policy evidence and statistical evidence over several years.

The final status classification still needs human checking. The evidence table helps structure the tracking process, but it does not fully automate the political judgment.

## Next steps

The next steps are:

1. Check the links between evidence sources and promise IDs again after the final promise dataset is confirmed.
2. Add more specific budget or funding documents if needed.
3. Use the evidence table together with the promise dataset to support the final tracker.
4. Decide whether each promise should be classified as achieved, in progress, partially achieved, unclear, or no clear evidence.