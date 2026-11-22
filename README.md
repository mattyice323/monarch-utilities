# Monarch Utilities

Agent skills and MCP reference guides for analyzing personal finances, credit card perks, and merchant loyalty in [Monarch Money](https://www.monarchmoney.com/) via `monarch-mcp`.

## Included Agent Skills

Skills live in `.agents/skills/` and follow the [Agent Skills](https://agentskills.io/) progressive-disclosure format:

| Skill | What It Does | Example Prompt |
| :--- | :--- | :--- |
| **[`analyzing-credit-card-perks`](./.agents/skills/analyzing-credit-card-perks/SKILL.md)** | Identifies active/unlinked credit cards from 12-month transaction history, audits utilized vs. missed statement credits & perks, flags misrouted category spend, and recommends cards to fill portfolio gaps. | *"Analyze my past year of transactions to see which credit cards I use, which perks I've used or missed, and which card I should swipe by category."* |
| **[`analyzing-merchant-loyalty`](./.agents/skills/analyzing-merchant-loyalty/SKILL.md)** | Ranks high-frequency merchants and cross-references recurring subscriptions and card perks to recommend store loyalty programs and memberships. | *"Which merchants do I shop at most often, and which loyalty programs or memberships should I sign up for?"* |

## MCP Guides & Reference

- **[`monarch_mcp.md`](./monarch_mcp.md)** — Practical operational guide for the `monarch-mcp` server (parallel pagination, summary vs. detail modes, POS merchant name quirks, and safe bulk mutations).
- **[`tools.md`](./tools.md)** — Full schema and parameter reference for all 47 `monarch-mcp` tools.

## Usage

1. Connect the `monarch-mcp` server in your AI coding agent (Antigravity, Claude Code, Cursor, etc.).
2. Open this repository (or copy `.agents/skills/` into your workspace) so your agent discovers the skills automatically.
3. Ask natural-language questions about your spending, credit card perks, or merchant loyalty.
