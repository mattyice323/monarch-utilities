# Output Template: Credit Card Perks, Spend Optimization & Portfolio Gap Report

Present the findings in four structured sections:
1. **Identified Credit Cards Summary Table**
2. **Card-by-Card Analysis: Perks Utilized vs. Perks Missed**
3. **Quick Cheat-Sheet: Which Card to Swipe Going Forward**
4. **Portfolio Gap Analysis: Recommended Cards to Add** *(include when requested or when large 0x–1.5x spend gaps exist)*

---

## 1. Credit Cards Identified in Your Transaction History

Summarize all active and unlinked credit cards discovered across `GetAccounts` and `GetTransactions`:

```markdown
### 1. Credit Cards Identified in Your Transaction History

| Card Name | Monarch Account Match | 12-Mo Purchases | 12-Mo Spend | Verified Perks & Credits Captured |
| :--- | :--- | :---: | :---: | :--- |
| **<Card Product Name>** | `<Monarch Account Name (...XXXX)>` | <Count> | **$<Spend>** | **$<Credit Total>** in statement credits (`$<X>` <Perk A>, `$<Y>` <Perk B>) + <in-app benefits> |
| **<Co-Brand Card Name>** | `<Generic Feed Name (...XXXX)>` *(<Issuer> — $<Fee> annual fee on <Date>)* | <Count> | **$<Spend>** | **<N> <Brand> purchases ($<Spend>)** earning bonus points |
| **<Unlinked Card Name>** | *Not linked as a card feed (seen via checking payments)* | <N> payments | **$<Total Paid>** | Paid `$<Amount>` (<Date>) from `<Checking Account>` |
```

---

## 2. Card-by-Card Analysis: Perks Utilized vs. Perks Missed

For each card, display its annual fee (and renewal date if detected), then separate **Perks You Utilized** from **Perks & Multipliers You Missed**:

```markdown
### 2. Card-by-Card Analysis: Perks Utilized vs. Perks Missed

#### A. <Card Product Name> (`...XXXX`) — *$<Annual Fee> Annual Fee*

* **Perks You Utilized ($<Total Perk Value> captured vs. $<Annual Fee> fee):**
  * **$<Annual Cap>/yr <Credit Name> ($<Monthly Cap>/mo) — <X>% Utilized ($<Used> / $<Cap>):** Triggered in **<N> of 12 months** via **<Merchant A>** and **<Merchant B>**.
  * **<Multiplier>x on <Category>:** You routed **$<Category Spend>** across <N> purchases (<Top Merchants>) to this card, earning **~<Estimated Points> points**.

* **Perks & Multipliers You Missed:**
  * **$<Misrouted Spend> in <Bonus Category> put on other cards (Missed <Multiplier>x):** You placed **<N> <Category> purchases ($<Spend>)** at <Example Merchants> on 1x–2% cards instead of this card—leaving **~<Missed Points> extra points** on the table.
  * **<Unused Built-In Benefit> (e.g., Global Entry/TSA PreCheck credit, airline fee credit, complimentary membership, or banking relationship tier boost):** State the exact dollar value and how to activate or trigger it.
```

---

## 3. Quick Cheat-Sheet: Which Card to Swipe Going Forward

Provide a scannable routing table for the user's current wallet:

```markdown
### 3. Quick Cheat-Sheet: Which Card to Swipe Going Forward

| Spending Category | Best Card in Your Current Wallet | Multiplier / Perk |
| :--- | :--- | :--- |
| **<Category A (e.g., Dining & Groceries)>** | **<Card A (`...XXXX`)>** | **<Multiplier>x** + <Monthly/Semi-Annual Credits> |
| **<Category B (e.g., Co-Brand Airline/Hotel)>** | **<Card B (`...XXXX`)>** | **<Multiplier>x** + <Ancillary Perks> |
| **<Category C (e.g., Transit & Rideshare)>** | **<Card C (`...XXXX`)>** | **<Multiplier>x** (vs. 1x on other cards) |
| **<Category D (e.g., Warehouse Clubs & Catch-All)>** | **<Card D (`...XXXX`)>** | **Unlimited <X>% Cash Back** + <Ancillary Credit> |
```

---

## 4. Portfolio Gap Analysis: Recommended Cards to Add

When the user asks for card recommendations (or has major spending buckets earning 0x–1.5x), quantify the exact annual gain using their 12-month spending totals:

```markdown
### 4. Top Card Recommendations for Your Spending Profile

#### 1. <Recommended Card Name> — *$<Annual Fee> Annual Fee* (<Primary Target Category>)
* **Why it fits your numbers:**
  * **<Target Category / Merchant> ($<12-Mo Spend>/yr across <N> transactions):** Currently earning **<Current Rate>** on `<Current Account>`. Switching this spend to **<Recommended Card>** at **<New Rate>** unlocks **+<Net Annual Points or Cash Value>/year**.
  * **Ecosystem / Partner Synergy:** Explain how points or perks stack with the user's existing cards, airlines, hotels, or frequent merchants.

### Summary: Optimal Future Wallet

| Category | Your 12-Mo Spend | Current Card & Rate | Upgraded Card & Rate | Estimated Annual Gain |
| :--- | :---: | :--- | :--- | :--- |
| **<Gap Category 1>** | **$<Spend>** | <Current Account> (<Rate>) | **<New Card> (<New Rate>)** | **+<Points / $ Value>** |
| **<Gap Category 2>** | **$<Spend>** | <Current Account> (<Rate>) | **<New Card> (<New Rate>)** | **+<Points / $ Value>** |
```

---

## 5. Next-Step Prompt

Close with an actionable follow-up offer:
> "Would you like me to set up Monarch categorization rules for your statement credits or calculate a month-by-month breakdown for any specific card or merchant category?"
