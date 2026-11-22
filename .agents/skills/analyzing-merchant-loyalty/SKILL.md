---
name: analyzing-merchant-loyalty
description: >-
  Analyzes Monarch Money transaction history and merchant frequency to identify
  high-value loyalty programs, store memberships, rewards accounts, and credit
  card perks. Use when the user asks which merchants they shop at most often,
  where they should sign up for memberships or rewards accounts to accrue
  points, or how to maximize store loyalty and card-linked benefits from past
  purchases.
---

# Analyzing Merchant Loyalty & Membership Opportunities

Identify high-frequency merchants from the user's Monarch Money data and recommend actionable loyalty programs, store memberships, and card-linked perks.

## Workflow

### 1. Fetch Monarch Data in Parallel
Batch these three `monarch-mcp` tool calls in a single turn with `intent: "spending_analysis"`:
- **`GetMerchants`** (`limit: 100`): Returns merchants ordered by total `transaction_count`. Use this as the primary frequency ranking instead of paging through thousands of individual transactions.
- **`GetTransactions`** (`limit: 100`, `start_date`: 12 months ago, `end_date`: today): Inspect recent transaction amounts, categories, payment `account` names (to identify credit cards used), and positive credit adjustments (e.g., existing statement credits).
- **`GetRecurring`**: Identify existing recurring subscriptions and memberships so you can flag what the user already pays for rather than recommending duplicate memberships.

### 2. Filter & Group Frequent Merchants
From the `GetMerchants` results (focusing on merchants with 3+ transactions):
1. **Exclude non-loyalty entities**: Filter out P2P transfers (e.g., Venmo, Zelle, PayPal), bank/card payments (e.g., credit card autopays, loan payments, brokerage transfers), payroll/employers, rent/mortgage/landlords, utilities (electric, gas, water, internet), insurance, and generic placeholders (`Payment`, `Restaurants`, `ATM Withdrawal`).
2. **Consolidate split merchant names**: Combine variants of the same brand (e.g., `Coffee Shop` + `Coffee Shop #104`, `Delivery App` + `Delivery App Marketplace`, or regional store locations under one retail banner).
3. **Group into logical spending tiers**:
   - Groceries & Everyday Retail
   - Coffee, Quick Dining & Convenience
   - Rideshare & Food Delivery
   - Travel, Recreation & Fuel

### 3. Cross-Reference Credit Card Perks & Existing Subscriptions
Before recommending a paid or free membership, inspect the `account` field and positive credit amounts in `GetTransactions` plus active streams in `GetRecurring`:
- **Active Card Credits**: Check which credit cards the user swipes (from the `account` field on transactions). Highlight built-in merchant perks on those specific cards (such as monthly rideshare credits, dining/delivery credits, streaming rebates, or complimentary delivery passes) and note whether positive credit transactions show they are already utilizing them.
- **Cross-Brand Bundles**: If the user pays for major retail or travel memberships, note free linked partner benefits (for example, retail memberships that include complimentary food-delivery tiers, or grocery loyalty programs that stack with fuel rewards).
- **Existing Memberships**: Acknowledge active memberships found in `GetRecurring` (e.g., fitness clubs, streaming services, annual retail memberships) so recommendations focus on *new* optimization opportunities.

### 4. Format the Recommendations
Structure the final response using the layout and table conventions in [references/output-template.md](./references/output-template.md).
