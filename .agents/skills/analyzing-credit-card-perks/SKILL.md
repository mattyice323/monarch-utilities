---
name: analyzing-credit-card-perks
description: >-
  Analyzes Monarch Money accounts, recurring streams, and 12-month transaction
  history to identify which credit cards the user holds, audit utilized versus
  missed credit card perks and statement credits, evaluate annual fee ROI, flag
  misrouted category spend, and recommend new credit cards to fill portfolio
  gaps. Use when the user asks to identify their credit cards from transactions,
  check which card benefits or credits they have used or missed, evaluate
  whether a card's annual fee is worth keeping, optimize which card to swipe by
  category, or get credit card recommendations based on their spending history.
---

# Analyzing Credit Card Perks & Spend Optimization

Identify the user's active and unlinked credit cards from Monarch Money data, audit 12-month perk and statement credit utilization, recommend optimal card-by-category routing, and identify high-impact cards to fill portfolio gaps.

## Workflow

### 1. Fetch Monarch Data in Parallel
Batch initial discovery calls in a single turn with `intent: "spending_analysis"`:
- **`GetAccounts`**: List connected accounts to identify active credit cards (`type: "Credit Card"`) and checking/savings/investment balances (to evaluate relationship-tier reward multipliers).
- **`GetRecurring`**: Detect recurring annual membership/renewal fees, monthly subscription charges, rent/housing outflows, and recurring credit card bill payments.
- **`GetMerchants`** (`limit: 100`): Identify top merchants by transaction frequency to spot high-volume co-brand or store card opportunities.
- **`GetTransactions`** (`limit: 100`, `start_date`: 12 months ago, `end_date`: today): Fetch the first page and inspect `transaction_count`. If `truncated: true`, batch the remaining `offset` pages in parallel (up to 10–15 pages per turn) so the full 12-month window is analyzed accurately.

### 2. Aggregate Transactions Deterministically
When `GetTransactions` spans multiple pages saved to disk, run [scripts/aggregate_card_activity.py](./scripts/aggregate_card_activity.py) passing the saved JSON file paths:
```bash
python3 .agents/skills/analyzing-credit-card-perks/scripts/aggregate_card_activity.py --start YYYY-MM-DD --end YYYY-MM-DD <saved_json_files...>
```
The script deduplicates transactions across pages and outputs:
- Total purchase count, total spend, and active date range per account.
- Spend breakdown by Monarch category and top merchants per card (and checking/ACH spend such as rent).
- All positive credit transactions (`amount > 0`), including small credits (`< $150`) categorized under `Credit Card Payment`, `Transfer`, or `Other Income`.
- Outbound `Credit Card Payment` transactions from checking accounts to identify unlinked credit cards.

### 3. Identify & Disambiguate Credit Cards
Reconcile user-mentioned cards (if provided) with Monarch accounts:
1. **Explicitly Named Cards**: Match connected `Credit Card` accounts by issuer and product name.
2. **Generic Co-Brand Feeds**: When an issuer labels a card generically (e.g., `CREDIT CARD (...XXXX)`), identify the exact card product and tier by inspecting:
   - Annual fee charges in `Miscellaneous` or `Financial Fees` (e.g., $95, $99, $149, $250, $325, $550+).
   - Dominant co-brand merchant purchases (airlines, hotels, retail brands).
3. **Unlinked / External Cards**: Check checking-account outflows categorized as `Credit Card Payment` or `Transfer` to third-party card issuers that lack a connected `Credit Card` account feed. Note the payment totals and remind the user that line-item purchase analysis requires linking the card feed.

### 4. Audit Utilized vs. Missed Perks & Multipliers
For each identified card, evaluate four dimensions:
1. **Direct Statement Credits (Monthly, Semi-Annual, Annual)**:
   - Match positive transactions (`amount > 0`) against the card's credit schedule (monthly dining/coffee/streaming credits, semi-annual restaurant/retail credits, annual travel credits).
   - **Critical Pitfall**: Never filter out `Credit Card Payment`, `Transfer`, or `Other Income` before inspecting positive amounts under `$150`. Monarch frequently auto-categorizes issuer statement credits (such as split restaurant credits or monthly dining rebates) under payment or transfer categories.
2. **In-App Wallet Credits & Complimentary Memberships**:
   - Some perks load credit directly into a partner app wallet (e.g., monthly rideshare/delivery cash) and reduce the net charge before hitting the card statement. Verify utilization by checking monthly transaction frequency at that partner merchant on the card.
   - Check `GetRecurring` and merchant history for complimentary card-linked memberships (e.g., delivery passes) or multi-year credits (e.g., Global Entry / TSA PreCheck).
3. **Banking Relationship Multipliers**:
   - If a card's reward rate scales with deposit/investment balances at the same institution, compare the user's connected `Checking` + `Savings` + `Investments` balances in `GetAccounts` against the institution's tier thresholds. Flag if a flat-rate card is under-earning relative to another catch-all card in their wallet.
4. **Misrouted Category Spend (Multiplier Leakage)**:
   - Identify purchases placed on low-multiplier cards (1x–1.5%) when another card in the user's wallet offers a higher category multiplier (e.g., dining, groceries, direct airfare, transit/rideshare) or a higher flat catch-all rate (e.g., 2% cash back on non-bonus and warehouse club spend).

### 5. Identify Portfolio Gaps & Recommend New Cards
Analyze the user's largest 0x–1.5x spending buckets across all accounts (including checking/ACH outflows) to recommend 2–4 high-impact cards that complement their existing setup:
- **Unrewarded Checking / ACH Outflows**: Flag major recurring expenses like **Rent** (`0x` from checking) that could earn points via a fee-free rent rewards card.
- **High-Spend 1x–1.5x Categories**: Check categories where current cards earn only base rates (e.g., rideshares, public transit, parking, non-co-brand hotels/home rentals, gas, or streaming).
- **High-Frequency Single Merchants**: Cross-reference top merchants from `GetMerchants` (e.g., 50+ annual transactions at a major online retailer, warehouse club, or airline) that are currently placed on a 1x–2% card instead of a 5% store/co-brand card.
- **Point Ecosystem Synergy**: Prioritize cards whose points transfer to or pool with the user's existing airline, hotel, or transferable-point ecosystems, and always include a `$0` annual fee option alongside premium options.

### 6. Format the Report
Present the analysis using the structure and table conventions in [references/output-template.md](./references/output-template.md).
