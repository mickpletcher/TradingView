# TradingView n8n Project Analysis

Last reviewed: 2026-04-28

## Purpose

This file is the quick-reference analysis for the `tradingview_n8n` subproject. It exists so future changes can start from a concise overview of the module instead of re-reading the entire subproject first.

## Current Scope

- `tradingview_n8n` is a sibling subproject to `tradingview_alpaca`, not part of it.
- Its purpose is to receive TradingView alerts through an n8n webhook flow rather than execute trades directly.
- It is currently a documentation-and-design scaffold, not a code implementation.
- The current assets are:
  - `README.md`
  - `tradingview-message-example.json`

## What This Subproject Does

- Routes TradingView alerts into n8n.
- Treats n8n as the automation hub for downstream actions.
- Makes it easy to:
  - notify
  - log
  - enrich
  - filter
  - forward to brokers or other systems later

This is the multiplier module in the repo because a single TradingView alert can be turned into many downstream automations without binding the project to one broker.

## Current Design Intent

The intended high-level flow is:

```text
TradingView alert
  -> n8n webhook trigger
  -> validation / normalization
  -> filter stage
  -> branch stage
  -> notification / logging / enrichment / forwarding
```

The payload shape is intentionally close to the Alpaca module so future interop stays simple.

Current example payload fields:

- `symbol`
- `side`
- `qty`
- `strategy`
- `price`
- `interval`
- `time`
- `source`

## Strengths

- Clean separation from broker-specific execution logic.
- Good fit for your broader automation environment because n8n can orchestrate many systems from one webhook.
- Low-friction expansion path for notifications, journaling, sheets, morning briefings, and broker fan-out.
- Keeps the repo moving toward a modular TradingView automation workspace instead of a single-broker project.

## Gaps

### 1. No runnable workflow export yet

The subproject explains how the flow should work, but it does not yet include an exported n8n workflow JSON file that could be imported directly.

### 2. No payload validation artifact yet

The design references validation and normalization, but there is no checked-in validator node definition, schema, or sample workflow branch yet.

### 3. No operational examples yet

There are no concrete examples yet for:

- send to Discord
- send to Telegram
- write to a spreadsheet
- hand off to a broker module
- branch by strategy or symbol

### 4. No local test harness yet

There is no replay script, sample request script, or mock alert runner for testing the n8n flow outside TradingView.

## Recommended Next Steps

1. Add an importable n8n workflow JSON export for a minimal intake-and-log path.
2. Add one concrete downstream example such as Discord notification or Google Sheets logging.
3. Add a validation/normalization step definition so the payload contract is explicit.
4. Add a simple local test example showing how to POST the sample payload into n8n.
5. Decide whether this subproject will stay docs-first or grow into a packaged collection of reusable n8n workflow templates.

## Relationship To Other Repo Modules

- `tradingview_alpaca` is execution-focused and broker-specific.
- `tradingview_n8n` is orchestration-focused and broker-agnostic.
- Future router, journal, and notification modules can naturally connect to this subproject.

## Editing Guidance

Before changing this subproject, check:

- whether the change is still n8n-centered rather than broker-specific
- whether the payload shape should stay aligned with other TradingView modules
- whether the change belongs in `README.md`, the example payload, or a future workflow export file

When new implementation artifacts are added, append to this file so it remains the fastest way to understand the subproject.
