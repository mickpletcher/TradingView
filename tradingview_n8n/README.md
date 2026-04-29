# TradingView to n8n Webhook Router

This subproject routes TradingView alerts into your n8n instance by webhook instead of sending them straight to a broker.

That gives you the full n8n workflow graph after the alert lands:

- notify by email, SMS, Discord, or Telegram
- log to Google Sheets, Airtable, or a database
- hand off to your morning briefing pipeline
- branch by symbol, strategy, or alert type
- fan out to one or more broker automations later

This is the multiplier play for the repo because one TradingView alert can become a reusable automation entry point.

## What This Subproject Is

`tradingview_n8n` is a sibling module to `tradingview_alpaca`, not part of it.

Use this module when you want:

- alert routing without immediate trade execution
- a central automation hub
- a low-friction way to expand into notifications, logging, and multi-destination workflows

## Recommended Flow

```text
TradingView alert fires
        |
        v
TradingView sends JSON webhook to n8n
        |
        v
n8n webhook trigger receives payload
        |
        v
n8n workflow branches by symbol / side / strategy
        |
        +--> notify
        +--> log
        +--> enrich data
        +--> forward to broker or another service
```

## Basic n8n Setup

1. Create a new workflow in n8n.
2. Add a `Webhook` trigger node.
3. Copy the production webhook URL from n8n.
4. In TradingView, create or edit your alert.
5. Paste the n8n webhook URL into the TradingView `Webhook URL` field.
6. Paste a JSON message similar to the example in [tradingview-message-example.json](tradingview-message-example.json).
7. In n8n, add downstream nodes for the actions you want:
   - notifications
   - spreadsheet/database logging
   - filtering
   - broker handoff

## Suggested Workflow Stages

### 1. Intake

- Receive the TradingView payload.
- Validate that expected fields are present.
- Normalize symbol, side, and strategy values.

### 2. Filter

- Ignore unwanted symbols or strategies.
- Optionally enforce time-of-day or session rules.
- Prevent duplicate processing if the same alert arrives twice.

### 3. Branch

- Send important alerts to notifications.
- Log all alerts to a durable data store.
- Forward specific alerts to other automation targets.

### 4. Enrich

- Add metadata like received time, workflow name, routing target, or market session.
- Optionally call other services before deciding what to do next.

### 5. Dispatch

- Send to Home Assistant
- Send to Discord or Telegram
- Write to Google Sheets or SQLite
- Forward to a broker-specific module later

## Example Use Cases

- Notify your phone when a major signal fires.
- Log every signal to a sheet for later review.
- Feed selected alerts into a daily or morning market briefing workflow.
- Route only a subset of alerts into a broker automation path.
- Mirror a single alert to multiple downstream systems.

## TradingView Message Shape

The example payload file in this folder uses a simple, reusable structure:

- `symbol`
- `side`
- `qty`
- `strategy`
- `price`
- `interval`
- `time`
- `source`

That shape is intentionally close to the Alpaca module so future routing between subprojects stays easy.

## Future Expansion Ideas

- Add a reusable n8n workflow export file to this folder.
- Add a payload validator step before downstream routing.
- Add a router workflow that can fan out to multiple broker or notification targets.
- Add a journal/logging workflow that writes every alert to a local database or sheet.

## Related Files

- Root overview: [../README.md](../README.md)
- Alpaca execution module: [../tradingview_alpaca/README.md](../tradingview_alpaca/README.md)
- Project analysis log: [../prompts/project-analysis/project_analysis.md](../prompts/project-analysis/project_analysis.md)
