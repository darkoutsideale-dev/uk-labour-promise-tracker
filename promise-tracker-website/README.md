# UK Labour Housing Promise Tracker

This project is a semi-automatic website dashboard for tracking the implementation progress of Labour's 2024 housing promises.

The tracker combines a structured promise dataset, automatically collected evidence from official sources, and a visual dashboard that displays the current progress of each promise.

## Project Aim

The aim of this project is to explore how political campaign promises can be tracked after an election.

Instead of only asking whether a promise is true or false, this tracker focuses on implementation progress. Each promise is assigned a status and progress score based on available evidence.

The project focuses on housing-related promises from Labour's 2024 manifesto.

## Research Question

To what extent can UK Labour's 2024 manifesto promises on housing be tracked through parliamentary, governmental, and official policy evidence?

## Project Structure

```text
promise-tracker-website/
├── data/
│   ├── promises.csv
│   ├── evidence.csv
│   └── promise_status_suggestions.csv
│
├── scripts/
│   ├── collect_evidence.py
│   ├── update_status.py
│   └── update_tracker.py
│
├── website/
│   └── app.py
│
└── README.md
