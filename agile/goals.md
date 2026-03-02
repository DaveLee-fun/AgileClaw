# AgileClaw Goals

## Sprint: Multi-Goal Agile Sprint
Period: 2026-03-02 → 2026-03-08

## Goal Teams
- team-growth-threads: Social growth objective
- team-revenue-product: Revenue optimization objective

## Global KPI Snapshot

| Metric | Current | Target | Source | Status |
|--------|---------|--------|--------|--------|
| Threads followers (optional) | 160 | 250 | threads_get_followers | 🟡 |
| Reddit total karma (optional) | 1200 | 1500 | reddit_get_karma | 🟡 |
| App downloads | 42 | 80 | App Store Connect | 🔴 |
| Daily revenue (USD) | 120 | 300 | LearnWorlds dashboard | 🔴 |

## This Week's Focus
1. For every goal request, create or update a dedicated Agile Team charter.
2. Confirm KPI measurement method first, then execute.
3. Prioritize the highest-risk KPI in each team.

## How to Measure
- Use generic KPI tools for team metrics (`kpi_upsert_metric`, `kpi_log_measurement`, `kpi_list_metrics`).
- Use KPI-specific tool only when needed (`threads_get_followers`, `reddit_get_karma`).
- If dashboard metric, fetch from analytics URL or manual source.

## Notes
Agile loop is metric-agnostic. Platform-specific tools are optional.
