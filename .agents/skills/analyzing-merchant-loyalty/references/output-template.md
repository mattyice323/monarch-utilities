# Output Template: Merchant Loyalty & Membership Report

Present the findings in two parts: **Categorized Merchant Breakdowns** followed by a **Summary Checklist Table** and a **Follow-up Offer**.

## 1. Categorized Merchant Breakdowns

Group top merchants into 3–4 thematic sections based on the user's spending profile. For each merchant entry, include:
- **Merchant Name & Combined Transaction Count**: e.g., `**<Merchant Name> (42 transactions):**`
- **Recommended Program & Cost**: Name the specific loyalty program or tier and state whether it is free, card-linked, or paid.
- **Concrete Value / Mechanics**: State the exact earn rate, redemption threshold, or fee waiver (e.g., `1 point per $1 spent; 1,000 points = $10 reward`, `$0 delivery fees + 6% back on rides`).
- **Card / Bundle Synergy (when applicable)**: Call out if one of the user's active credit cards or existing memberships already unlocks a credit or free tier at that merchant.

### Example Section Format

```markdown
### 1. Groceries & Everyday Retail (Free Loyalty Programs)
* **<Merchant A> (<N> transactions):** Sign up for **<Program Name>** (free). You earn **<earn rate/perk>** and **<redemption value>**.
* **<Merchant B> (<N> transactions):** Get a free **<Program Name>** account for **<digital coupons / fuel points / cross-brand synergy>**.

### 2. Coffee, Quick Dining & Convenience (Free App Rewards)
* **<Merchant C> (<N> transactions):** Load your card into the **<App Name>** app to earn **<points/$1>**. *(Note any detected credit card statement credits already triggering).*

### 3. Rideshare & Food Delivery (Card-Linked & Paid Memberships)
* **<Merchant D> (<N> transactions):** Evaluate **<Paid Membership>** ($X/mo) based on high transaction volume, and stack with **<Card Name>** monthly credits or **<Cross-Brand Partner Bundle>**.

### 4. Travel, Recreation & Fuel (Free Loyalty & Existing Memberships)
* **<Merchant E> (<N> transactions):** Link your **<Loyalty Program>** number. *(Note any existing recurring memberships detected in `GetRecurring` so the user knows they are accounted for).*
```

## 2. Summary Checklist Table

End the analysis with a scannable action table ranking the highest-impact programs:

```markdown
### Summary Checklist of Top Actions
| Merchant | Transactions | Recommended Program | Cost | Key Benefit |
| :--- | :---: | :--- | :---: | :--- |
| **<Merchant>** | <Count> | <Program + Card Synergy> | <Free / $X/mo> | <1-line concrete reward or credit> |
```

## 3. Next-Step Prompt

Close by offering a targeted deep dive using `GetTransactions` filtered to specific merchants:
> "Would you like me to calculate the exact total dollar amount you've spent over the last 12 months at any of these specific merchants to estimate your exact annual savings?"
