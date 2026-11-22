# Monarch MCP Tool Reference Guide

This document provides a comprehensive reference for all **47 tools** provided by the `monarch-mcp` server. It covers server-wide rules, a functional breakdown grouped by financial domain, and the full catalog of tool schemas, arguments, and parameter types.

---

## 1. Core Server Rules & Conventions

1. **Numeric String IDs on All Mutations**: Write operations (`UpdateTransaction`, `BulkUpdateTransactions`, `MergeMerchants`, `CreateRule`, etc.) strictly require stable numeric ID strings returned by read tools. Never pass entity names directly to write tools.
2. **Required `intent` Parameter**: Every single tool call requires an `intent` enum value (e.g., `"organizing_finances"`, `"spending_analysis"`, `"budgeting"`). Monarch attaches this to data provider compliance logs. When using `"other"`, supply a brief 2–5 word task description in `intent_description` without personal details.
3. **JSON-Serialized Strings for `filters` and `updates`**: In `GetTransactions`, `BulkUpdateTransactions`, and `BulkRecategorizeTransactions`, the `filters` and `updates` arguments take a **serialized JSON string**, not a raw JSON object (e.g., `updates: '{"tag_ids": ["..."]}'`).
4. **Tag Replacement Safety**: Updating `tag_ids` on a transaction replaces its entire tag array. To preserve existing tags, read current tags first and pass `[<existing_tags>, <new_tag>]`.
5. **Dry Run Previews**: `BulkUpdateTransactions` and `BulkRecategorizeTransactions` support `dry_run=true` to preview `would_affect_count` and resolved updates prior to committing writes.

---

## 2. Functional Tool Directory

### Transactions & Activity

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetTransactions`](#gettransactions) | **Read** | Search and list the authenticated user's transactions. |
| [`CreateTransaction`](#createtransaction) | **Write** | Create a manual transaction in the user's account. |
| [`UpdateTransaction`](#updatetransaction) | **Write** | Update fields on a single transaction. Pass only the fields you want to change. |
| [`DeleteTransaction`](#deletetransaction) | **Write** | Permanently delete a manual transaction. Synced transactions cannot be deleted. |
| [`BulkUpdateTransactions`](#bulkupdatetransactions) | **Write** | Apply the same change to many transactions at once: recategorize, tag, mark reviewed, etc. |
| [`BulkRecategorizeTransactions`](#bulkrecategorizetransactions) | **Write** | Move many transactions into one category in a single call. |
| [`UpdateTransactionSplits`](#updatetransactionsplits) | **Write** | Replace the splits on a transaction. |
| [`GetRecurring`](#getrecurring) | **Read** | List the user's recurring activity — paychecks, bills, subscriptions, transfers. |

### Merchants & Vendor Cleanup

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetMerchants`](#getmerchants) | **Read** | List the household's merchants. |
| [`CreateMerchant`](#createmerchant) | **Write** | Create a merchant and return its `merchant_id`. |
| [`UpdateMerchant`](#updatemerchant) | **Write** | Rename a merchant and return the updated merchant, including its `merchant_id` and new name. |
| [`MergeMerchants`](#mergemerchants) | **Write** | Merge multiple merchants into one. Transactions and rules from the source merchants |

### Categories & Tags

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetCategories`](#getcategories) | **Read** | List all of the user's spending categories and the groups they belong to. |
| [`CreateCategory`](#createcategory) | **Write** | Create a custom category in the household. |
| [`UpdateCategory`](#updatecategory) | **Write** | Rename, re-group, or re-icon a custom category. System categories cannot be modified. |
| [`DeleteCategory`](#deletecategory) | **Write** | Delete a custom category. System categories cannot be deleted. |
| [`GetTags`](#gettags) | **Read** | List the user's transaction tags. |
| [`CreateTag`](#createtag) | **Write** | Create a transaction tag for the household and return it, including its `id`, name and color. |
| [`UpdateTag`](#updatetag) | **Write** | Rename a tag and/or change its color. Pass only the fields you want to change. |
| [`DeleteTag`](#deletetag) | **Write** | Delete a tag. Removes it from any transactions it's attached to. |

### Rules Engine & Automation

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`ListRules`](#listrules) | **Read** | List the household's transaction rules. |
| [`CreateRule`](#createrule) | **Write** | Create a transaction rule. At least one criteria AND one action is required. |
| [`UpdateRule`](#updaterule) | **Write** | Update a transaction rule. Use ListRules first to find its rule_id. Only supplied params change. |
| [`DeleteRule`](#deleterule) | **Write** | Delete a transaction rule. Use ListRules first to find the rule_id. |

### Accounts & Net Worth

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetAccounts`](#getaccounts) | **Read** | List the user's connected accounts and their current balances. |
| [`GetNetWorthHistory`](#getnetworthhistory) | **Read** | Get the user's net worth over time, with optional per-account breakdown. |
| [`GetInvestments`](#getinvestments) | **Read** | List the user's investment holdings with current values and period performance. |
| [`GetRealEstate`](#getrealestate) | **Read** | List the user's real estate properties and their related home loans. |
| [`GetCreditScoreHistory`](#getcreditscorehistory) | **Read** | Get the user's credit score history over a date range. |
| [`UpdateAccountBalanceHistory`](#updateaccountbalancehistory) | **Write** | Write balance history to a manual account, replacing the dates the entries cover. |
| [`UpdateAccountDebtDetails`](#updateaccountdebtdetails) | **Write** | Update debt details stored on an account. |

### Budgets & Cash Flow Planning

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetBudget`](#getbudget) | **Read** | Get the user's budget for a date range. |
| [`SetBudgetAmount`](#setbudgetamount) | **Write** | Set the planned budget amount for a month (ISO YYYY-MM-DD, normalized to month start). |
| [`MoveBudgetAmount`](#movebudgetamount) | **Write** | Move a positive planned amount between two different budget lines for one month (ISO YYYY-MM-DD). |
| [`GetCashFlow`](#getcashflow) | **Read** | Run a flexible cash flow query over a date range with two-stage aggregation. |
| [`GetSpendingByCategory`](#getspendingbycategory) | **Read** | Get the user's spending broken down by category for a date range. |
| [`GetDebtPaydownBudget`](#getdebtpaydownbudget) | **Read** | Get planned, actual, and remaining debt-paydown budget amounts by account and month. |
| [`GetDebtPaydownPlan`](#getdebtpaydownplan) | **Read** | Project the household's eligible debt payoff plan without saving anything. |

### Goals & Savings Tracking

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetGoals`](#getgoals) | **Read** | List the user's savings goals and progress. |
| [`CreateGoal`](#creategoal) | **Write** | Create a savings goal for the household. |
| [`UpdateGoal`](#updategoal) | **Write** | Edit a savings goal and/or change which accounts count toward it. Pass only the fields you want to change. |
| [`DeleteGoal`](#deletegoal) | **Write** | Delete a savings goal. |
| [`AllocateToGoal`](#allocatetogoal) | **Write** | Allocate part of an account's balance to a savings goal in Monarch's goal tracking. |
| [`ReduceGoalAllocation`](#reducegoalallocation) | **Write** | Reduce how much of an account's balance is allocated to a savings goal. |

### Household & Administration

| Tool Name | Type | Summary Description |
| :--- | :---: | :--- |
| [`GetHouseholdMembers`](#gethouseholdmembers) | **Read** | List the members of the authenticated user's household. |
| [`GetBusinesses`](#getbusinesses) | **Read** | List the businesses the user has set up for tracking (e.g. LLCs, side hustles). |
| [`ReportIssue`](#reportissue) | **Read** | Report when something seemed off during this session. |

---

## 3. Complete Tool Catalog & Schemas

Below is the full specification for each tool, including its description, parameter requirements, accepted types, and default values.

### `AllocateToGoal`

Allocate part of an account's balance to a savings goal in Monarch's goal tracking.

The amount must be positive and is limited by the account's unallocated balance. If the amount
is capped, the result includes a 'user_notice'.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_id` | `string` | Yes | — | Account ID from GetAccounts whose balance is allocated. |
| `amount` | `number` | Yes | — | Positive amount to allocate. |
| `date` | `string | null` | No | None | Optional ISO date (YYYY-MM-DD) for the allocation; defaults to today. |
| `goal_id` | `string` | Yes | — | Goal ID from GetGoals. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `notes` | `string | null` | No | None | Optional free-text note. |

---

### `BulkRecategorizeTransactions`

Move many transactions into one category in a single call.

Use this for audit-and-fix loops like "put every Costco charge in Groceries."
Provide exactly one of transaction_ids or filters.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `category_id` | `string` | Yes | — | target category ID (from GetCategories) applied to every match. |
| `dry_run` | `boolean` | No | False | if true, returns a preview ({would_affect_count, requested_count, sample_transaction_ids, target_category_id, target_category}) without writing. Call once with dry_run=true to show the user what will change, then again with dry_run=false to commit. |
| `filters` | `string | null` | No | None | JSON object selecting the transactions to move; mutually exclusive with transaction_ids. Supported keys: `start_date` and `end_date` (ISO YYYY-MM-DD, both required when filtering), `merchant_id`, `category_id` (the *current* category to move out of), `account_id`. All IDs come from the read tools. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `transaction_ids` | `array | null` | No | None | explicit IDs from GetTransactions. Mutually exclusive with filters. At most 500 transactions per call, whether listed or matched by filters; larger requests are rejected, so narrow the filter or split into batches. |

---

### `BulkUpdateTransactions`

Apply the same change to many transactions at once: recategorize, tag, mark reviewed, etc.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `dry_run` | `boolean` | No | False | if true, returns a preview ({would_affect_count, sample_transaction_ids, resolved_updates}) without writing. If false, applies the updates. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `transaction_ids` | `array[string]` | Yes | — | List of IDs from GetTransactions, at most 500 per call. |
| `updates` | `string` | Yes | — | JSON object with any subset of: `date` (ISO YYYY-MM-DD, manual and synced transactions), `category_id`, `notes`, `hide_from_reports`, `review_status`, `is_recurring`, `needs_review_by_user_id`, `owner_user_id`, `owner_is_joint`, `business_entity_id`, `tag_ids` (list of tag IDs from GetTags; replaces each transaction's existing tags, so pass [] to clear them). Cross-entity references are IDs from the read tools. |

---

### `CreateCategory`

Create a custom category in the household.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `group_id` | `string` | Yes | — | ID of the existing category group to place this under (from GetCategories). |
| `icon` | `string | null` | No | None | Optional emoji or icon string. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `name` | `string` | Yes | — | Category name. Must be unique in the household. |

---

### `CreateGoal`

Create a savings goal for the household.

A new goal starts with a zero balance. To track progress, either link accounts whose
balance counts toward the goal (UpdateGoal with account_ids_to_link) or allocate part of an
account's balance to it (AllocateToGoal).

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `is_sinking_fund` | `boolean` | No | False | True for a recurring/spend-down fund where linked spending reduces progress. |
| `name` | `string` | Yes | — | Goal name. |
| `target_amount` | `number | null` | No | None | Optional amount you want to save toward this goal. |
| `target_date` | `string | null` | No | None | Optional ISO date (YYYY-MM-DD) you want to reach the target by. |
| `type` | `string` | No | 'savings' | Must be 'savings' (default), 'emergency_fund', 'home_down_payment', 'car', 'vacation', 'wedding', 'education', or 'retirement'. Debt payoff types aren't supported. |

---

### `CreateMerchant`

Create a merchant and return its `merchant_id`.

Use this when you need to assign a merchant that does not exist yet: first check
with GetMerchants(search=...); if there is no match, call this to create one, then
pass the returned `merchant_id` to a write tool (e.g. CreateTransaction).

If a merchant with this exact name already exists, its `merchant_id` is returned
instead of creating a duplicate.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `name` | `string` | Yes | — | Merchant name to create. |

---

### `CreateRule`

Create a transaction rule. At least one criteria AND one action is required.

Criteria (when do we match?): merchant_names, category_ids, account_ids, amount_min,
amount_max. `merchant_names` are literal text patterns matched against a transaction's
merchant name (not entity references); `category_ids`/`account_ids` are IDs from the read
tools.

Actions (what do we do?): set_merchant_id (use CreateMerchant first if it doesn't exist),
set_category_id, add_tag_ids, set_hide_from_reports, set_needs_review, set_reviewed.
set_needs_review and set_reviewed are mutually exclusive.

New rules only affect future transactions. Returns the created rule and a 'user_notice'
explaining how to apply it to existing transactions in Monarch.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_ids` | `array | null` | No | None |  |
| `add_tag_ids` | `array | null` | No | None |  |
| `amount_max` | `number | null` | No | None |  |
| `amount_min` | `number | null` | No | None |  |
| `category_ids` | `array | null` | No | None |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `merchant_names` | `array | null` | No | None |  |
| `set_category_id` | `string | null` | No | None |  |
| `set_hide_from_reports` | `boolean | null` | No | None |  |
| `set_merchant_id` | `string | null` | No | None |  |
| `set_needs_review` | `boolean | null` | No | None |  |
| `set_reviewed` | `boolean | null` | No | None |  |

---

### `CreateTag`

Create a transaction tag for the household and return it, including its `id`, name and color.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `color` | `string | null` | No | None | Optional hex color (e.g. '#abcdef'). |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `name` | `string` | Yes | — | Tag name. Must be unique within the household. |

---

### `CreateTransaction`

Create a manual transaction in the user's account.

Cross-entity references are by ID. Use the read tools to look up IDs first
(GetMerchants, GetCategories, GetAccounts, GetBusinesses, GetHouseholdMembers).
To attach a merchant that doesn't exist yet, call CreateMerchant first.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_id` | `string` | Yes | — | ID of an existing account (from GetAccounts). Manual accounts have their balance updated automatically. |
| `amount` | `number` | Yes | — | Signed amount. Outflow (purchases, payments) is negative; inflow (income, refunds) is positive — same convention as GetTransactions. |
| `business_entity_id` | `string | null` | No | None | Optional business entity ID (from GetBusinesses) to attribute this to. |
| `category_id` | `string` | Yes | — | ID of an existing category (from GetCategories). |
| `date` | `string` | Yes | — | ISO date (YYYY-MM-DD). |
| `hide_from_reports` | `boolean | null` | No | None | When true, the new transaction is excluded from budgets/reports. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `merchant_id` | `string` | Yes | — | ID of an existing merchant (from GetMerchants / CreateMerchant). |
| `notes` | `string | null` | No | None | Optional free-text notes. |
| `owner_is_joint` | `boolean | null` | No | None | Set true for shared ownership. Do not pass with owner_user_id. |
| `owner_user_id` | `string | null` | No | None | Optional household member ID (from GetHouseholdMembers). Omit to inherit from the account's owner. |

---

### `DeleteCategory`

Delete a custom category. System categories cannot be deleted.

The category must have zero transactions assigned and no rules referencing it. If transactions
are still on it, first move them to another category (UpdateTransaction or
BulkUpdateTransactions). If rules reference it (as a filter, set-category action, or split),
update or delete those rules (ListRules, UpdateRule, DeleteRule) first. Then retry the delete.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `category_id` | `string` | Yes | — |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `DeleteGoal`

Delete a savings goal.

The goal must have no linked accounts. If accounts are still linked, the call fails with the
count — unlink them first with UpdateGoal(account_ids_to_unlink=[...]) so their balances no
longer count toward the goal, then retry the delete.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `goal_id` | `string` | Yes | — |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `DeleteRule`

Delete a transaction rule. Use ListRules first to find the rule_id.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `rule_id` | `string` | Yes | — |  |

---

### `DeleteTag`

Delete a tag. Removes it from any transactions it's attached to.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `tag_id` | `string` | Yes | — |  |

---

### `DeleteTransaction`

Permanently delete a manual transaction. Synced transactions cannot be deleted.

Manual accounts have their balance updated automatically. Returns the deleted transaction's ID.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `transaction_id` | `string` | Yes | — |  |

---

### `GetAccounts`

List the user's connected accounts and their current balances.

Returns each account's id, name, notes (when set), type (e.g. Checking, Credit Card, 401k),
current balance, and — for credit cards — APR and — for loans — interest rate,
minimum payment, and remaining term.
Also returns total assets, total liabilities, and net worth. Pass an account
`id` to the write tools that take `account_id`.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_sub_types` | `array | null` | No | None | filter by specific account SUBTYPE display name (e.g. ["Checking", "Savings", "401k", "Brokerage (Taxable)"]). Use this for specific questions; do NOT also pass account_types. |
| `account_types` | `array | null` | No | None | filter by broad account TYPE display name (e.g. ["Cash", "Investments", "Credit Cards", "Loans", "Real Estate"]). Use this for broad questions; do NOT also pass account_sub_types. |
| `accounts` | `array | null` | No | None | filter to specific account names. |
| `businesses` | `array | null` | No | None | filter to accounts attached to one of these businesses. |
| `include_unassigned_businesses` | `boolean` | No | False | when filtering by businesses, also include accounts not attached to any business. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `ownership` | `string` | No | '{}' | JSON object describing whose accounts to include. Shape: `{"scope": "household" \| "user", "user": "self" \| "<name>" \| "User N", "jointly_owned_setting": true \| false \| null}`. Default `"{}"` means everyone in the household. Each account's `owner_user_id` matches `GetHouseholdMembers` `user_id`. |

---

### `GetBudget`

Get the user's budget for a date range.

Returns budgeted amounts per category (or category group, depending on the
user's setup), monthly and overall totals, and — when `include_actuals` is
true — actual spending for each line plus an "over/under/on budget" status.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `end_date` | `string` | Yes | — | ISO date string. Will be clamped to start of month. |
| `include_actuals` | `boolean` | No | False | when true, also include per-line actual spending and over/under-budget status. Use this for budget-vs-actual comparisons. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `start_date` | `string` | Yes | — | ISO date string (YYYY-MM-DD). Will be clamped to start of month. |

---

### `GetBusinesses`

List the businesses the user has set up for tracking (e.g. LLCs, side hustles).

Returns each business's stable `id`, name, and structure (e.g. llc,
sole_proprietorship), along with how many accounts and how many transactions
are tied to it.

Use this to discover businesses before filtering other tools by business, or
when the user asks "what businesses do I have?". Pass a business `id` to the write
tools that take `business_entity_id`.

Requires an active Monarch Plus subscription.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `GetCashFlow`

Run a flexible cash flow query over a date range with two-stage aggregation.

Stage 1 (`base_query`) buckets transactions by time and/or by an entity dimension.
Stage 2 (`post_aggregation`, optional) further reduces those buckets — averaging,
summing, counting, or selecting the top/bottom N per group.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `base_query` | `string` | No | '{}' | JSON shape `{"group_by_time": "day"\|"week"\|"month"\|"quarter"\|"year", "group_by_entity": "category"\|"category_group"\|"merchant"\|"household_merchant"\|"account"\|"needs_review_by_user"\|"business_entity"}`. Both fields optional. Default `"{}"` means a single overall total. |
| `end_date` | `string` | Yes | — | ISO date string, inclusive. |
| `filters` | `string` | No | '{}' | JSON object with any of: `accounts`, `include_categories`, `exclude_categories`, `merchants`, `business_entities`, `include_unassigned_business_entities`, `tags`, `tag_match_mode` ("any"\|"all"), `is_untagged`, `exclude_tags`, `exclude_tag_match_mode`, `exclude_merchants`, `exclude_accounts`, `exclude_business_entities`, `category_type` ("expense"\|"income"\|"transfer"), `ownership_setting` (incl. `exclude_users`), `search`. All filters intersect (AND). |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `post_aggregation` | `string | null` | No | None | optional JSON `{"group_by": [<dim>...], "operation": "sum"\|"avg"\|"max"\|"min"\|"count", "limit": <int for max/min>}`. |
| `start_date` | `string` | Yes | — | ISO date string (YYYY-MM-DD), inclusive. |

---

### `GetCategories`

List all of the user's spending categories and the groups they belong to.

Returns the full set of categories the household has set up — including unused,
disabled, and budget-excluded ones. Each category and group includes a stable
`id` plus its group, type (income / expense / transfer), budget variability
(fixed / flexible / non-monthly), and whether unused budget rolls over.

Use this to discover categories before filtering other tools by category, or
when the user asks "what categories do I have?". Pass a category `id` (or a group
`id`) to the write tools that take `category_id` / `group_id`.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `GetCreditScoreHistory`

Get the user's credit score history over a date range.

Returns one reading per month for each household member who has connected a
credit report, including the score, the score category (Poor / Fair / Good /
Great / Excellent), and any factors that influenced it.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `end_date` | `string` | Yes | — | ISO date string (YYYY-MM-DD), inclusive. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `start_date` | `string` | Yes | — | ISO date string (YYYY-MM-DD), inclusive. |

---

### `GetDebtPaydownBudget`

Get planned, actual, and remaining debt-paydown budget amounts by account and month.

planned_amount is the debt payment budgeted for that month (null when none is set); actual_amount is the payments linked to that debt account in the month.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `end_month` | `string` | Yes | — | ISO date (YYYY-MM-DD); the month is normalized to its first day. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `start_month` | `string` | Yes | — | ISO date (YYYY-MM-DD); the month is normalized to its first day. |

---

### `GetDebtPaydownPlan`

Project the household's eligible debt payoff plan without saving anything.

Avalanche pays the highest-rate debt first and rolls freed payments to the next debt.
Snowball pays the smallest balance first and rolls freed payments to the next debt.
Planned follows each debt's own payment without rolling freed payments over.
Top-level projected_interest, projected_total, and debt_free_date are for the selected method including any extra payments, and match the account rows. baseline is every debt paid at its own current payment with no rollover and no extra payments; compare against it to answer "how much sooner" or "how much interest saved".
Extra monthly or one-time payments are hypothetical and are never saved.

Debts missing a required rate or payment appear in `accounts_missing_details`.
Debts with no payment or no rate at all are left out of totals and the debt-free
date; a debt with its rate stored only in the other rate field is projected at
0% interest. UpdateAccountDebtDetails can save the missing values on the account.

Each account row's rate_field says which UpdateAccountDebtDetails field holds its rate ('apr' for credit cards, 'interest_rate' otherwise).

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `additional_monthly_payment` | `number | null` | No | None | optional extra amount paid toward debt every month. |
| `additional_one_time_payment` | `number | null` | No | None | optional one-time extra payment applied now. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `method` | `string` | No | 'avalanche' | 'avalanche' (default), 'snowball', or 'planned'. |

---

### `GetGoals`

List the user's savings goals and progress.

Returns each goal's name, current amount, target amount, and (for goals using
the newer savings-goal model) per-account allocations, totals for contributions,
withdrawals, and rebalancing adjustments, and the schedule shown on the goal card:
target date, forecasted completion date, status, months ahead of target (negative
when behind), and this month's planned contribution.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `GetHouseholdMembers`

List the members of the authenticated user's household.

Returns each member's stable `user_id`, `name`, `display_name`, and
`household_role`. Use this to discover the `user_id` before assigning
transaction ownership or a reviewer.

Pass `user_id` to the `owner_user_id` / `needs_review_by_user_id` write inputs.
For shared ownership, set `owner_is_joint=true` instead of passing `owner_user_id`.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `GetInvestments`

List the user's investment holdings with current values and period performance.

Holdings are always current — this tool cannot show past portfolio composition.
The date range only controls the period-over-period change shown for each
holding.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `accounts` | `array | null` | No | None | filter to specific account names (e.g. ["Fidelity Brokerage"]). |
| `end_date` | `string | null` | No | None |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `ownership` | `string` | No | '{}' | JSON shape — same as GetAccounts. Use `scope="user"` for "only my investments" type queries. |
| `start_date` | `string | null` | No | None |  |

---

### `GetMerchants`

List the household's merchants.

Returns each merchant's stable `merchant_id`, `name`, and `transaction_count`,
ordered by how many transactions use them. Pass `merchant_id` to the write tools
(e.g. CreateTransaction, UpdateMerchant, MergeMerchants). If no merchant matches,
use CreateMerchant to make one. Merchants with no transactions are omitted by default.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `include_merchants_without_transactions` | `boolean` | No | False | also return merchants with zero transactions (e.g. ones only referenced by rules). Default false. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `limit` | `integer` | No | 100 | max merchants to return (1-200, default 100). |
| `offset` | `integer` | No | 0 | number of merchants to skip, for paging. When `is_truncated` is true, pass the response's `next_offset` here for the next page. |
| `search` | `string | null` | No | None | optional case-insensitive substring filter on merchant name. |

---

### `GetNetWorthHistory`

Get the user's net worth over time, with optional per-account breakdown.

Returns dated readings of total net worth, total assets, and total liabilities.
By default readings are daily for ranges up to 31 days, weekly up to 92 days,
and monthly beyond that.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_sub_types` | `array | null` | No | None | filter by specific account SUBTYPE display name (e.g. ["Checking", "Savings", "401k", "Brokerage (Taxable)"]). Use this for specific questions; do NOT also pass account_types. |
| `account_types` | `array | null` | No | None | filter by broad account TYPE display name (e.g. ["Cash", "Investments", "Credit Cards", "Loans", "Real Estate"]). Use this for broad questions; do NOT also pass account_sub_types. |
| `accounts` | `array | null` | No | None | filter to specific account names. |
| `businesses` | `array | null` | No | None | filter to accounts attached to one of these businesses. |
| `end_date` | `string | null` | No | None | ISO date string. Defaults to today when omitted. |
| `include_account_breakdown` | `boolean` | No | False | when true, each reading also includes per-account balances and the response includes per-account changes over the period — useful for "what drove the change?" questions. |
| `include_unassigned_businesses` | `boolean` | No | False | also include accounts with no business. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `interval` | `string | null` | No | None | 'day', 'week', or 'month' to override the default reading interval when finer detail is needed. |
| `ownership` | `string` | No | '{}' | JSON shape — same as GetAccounts. |
| `start_date` | `string` | Yes | — | ISO date string (YYYY-MM-DD), inclusive. |

---

### `GetRealEstate`

List the user's real estate properties and their related home loans.

Returns each property (id, name, type, current value) and each property
loan (mortgage, home equity, etc., with current balance), plus a computed
total equity (property value minus loan balance).

If the user has property loans but no real estate accounts, equity cannot
be computed and the response includes a `message` explaining how to add
a property to fix that.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `GetRecurring`

List the user's recurring activity — paychecks, bills, subscriptions, transfers.

Returns four buckets: recurring income, recurring expenses, credit-card bill
payments, and recurring transfers (transfers are excluded from expense totals).
Each item includes its name, amount, category, account, frequency, last paid
date, and next forecasted date.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `include_liabilities` | `boolean` | No | True | include credit card bills and loan payments from connected credit reports. Set to false when the user is asking specifically about "subscriptions" — those are merchant-based (Netflix, Spotify, gym), not credit card bills. |
| `include_pending` | `boolean` | No | False | include suspected/unconfirmed recurring items. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `GetSpendingByCategory`

Get the user's spending broken down by category for a date range.

Returns total spending, the top 5 spending categories (with up to 3 top
merchants in each), and the single largest expense in the period.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `end_date` | `string` | Yes | — | ISO date string, inclusive. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `start_date` | `string` | Yes | — | ISO date string (YYYY-MM-DD), inclusive. |
| `totals_and_categories_only` | `boolean` | No | False | when true, skip merchant breakdown and the largest-expense lookup. Faster — use for historical comparisons or when only the per-category totals are needed. |

---

### `GetTags`

List the user's transaction tags.

Tags are a way to group transactions across categories (e.g. "vacation",
"tax-deductible"). Returns each tag's id, name, color, and how many
transactions currently use it. Pass a tag `id` to the write tools that take
`tag_ids` (and to UpdateTag / DeleteTag).

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `search` | `string | null` | No | None | optional case-insensitive substring filter on tag name. |

---

### `GetTransactions`

Search and list the authenticated user's transactions.

Supports fuzzy merchant/account matching, exact category or category-group
name matching, business-entity filters, review-state and pending-status
filters, and free-text search. Returns LLM-friendly JSON with formatted
amounts and each transaction's `pending` status. Use this for
natural-language queries like "my biggest restaurant charges last month"
or "transactions that need review."

Each transaction includes the IDs of its associated entities (`merchant_id`,
`category_id`, `account_id`, `business_entity_id`; with `include_details` also
`owner_user_id`, `needs_review_by_user_id`, `goal_id`, `tag_ids`) to identify
the referenced entities.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `end_date` | `string` | Yes | — |  |
| `filters` | `string` | No | '{"transaction_type": "All"}' | JSON string matching TransactionsToolFilterInput. Omit it or pass "{}" for defaults (`transaction_type` = 'All', visible-only, no category/merchant/account constraints). Non-empty filters must include `transaction_type` ('Credit', 'Debit', or 'All'). Hidden transactions are excluded by default; set `visibility` to 'all' to include them or 'hidden_only' for only hidden ones ('visible_only' is the default). Set `is_pending` to true for pending transactions or false for posted ones. To filter by category, pass `category_ids` (a list of stable category IDs from GetCategories or a transaction's `category_id`) and/or `categories` (a list of category or category-group NAMES, matched exactly as GetCategories returns them); both are accepted and combined. For "except X", use `exclude_categories`, `exclude_tags`, `exclude_merchants`, `exclude_accounts`, `exclude_business_entities`, or `ownership_setting.exclude_users`. Tags match any listed tag unless `tag_match_mode` is "all". |
| `include_details` | `boolean` | No | False | if true, each transaction also includes notes, cleansed_description (bank description with identifiers removed), hide_from_reports, review status, recurring flag, ownership, linked goal, tags, splits, and attachments. Forces the result limit to at most 20; pair with narrow filters when using it. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `limit` | `integer` | No | 50 | maximum transactions to return (1-100, default 50). |
| `offset` | `integer` | No | 0 | number of matching transactions to skip, for paging. When more transactions match than were returned, the response includes `next_offset` to pass here. |
| `sort_by` | `string` | No | 'date' | 'date' (most recent first), 'inverse_date', 'amount', or 'inverse_amount'. |
| `start_date` | `string` | Yes | — |  |
| `total_count_only` | `boolean` | No | False | if true, return only the total count. |

---

### `ListRules`

List the household's transaction rules.

Returns each rule's criteria (what it matches) and actions (what it does).
Category, account, tag, and merchant references include both their name and a
stable `id` (e.g. `category_ids`, `set_category_id`, `add_tag_ids`) to identify
the referenced entities.
Actions also include splits (`split_transactions`), goal links, owner and
business-entity assignment, notes, and notifications.

Useful for discovering existing automation before suggesting a new rule, or
before deleting a rule by id.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `MergeMerchants`

Merge multiple merchants into one. Transactions and rules from the source merchants
are re-pointed to the target, then the sources are deleted.
At most 25 source merchants can be merged per call; merge more in batches.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `source_merchant_ids` | `array[string]` | Yes | — | List of merchant IDs to merge into the target (from GetMerchants). |
| `target_merchant_id` | `string` | Yes | — | ID of the merchant to keep. Must not be in the source list. |

---

### `MoveBudgetAmount`

Move a positive planned amount between two different budget lines for one month (ISO YYYY-MM-DD).

Choose exactly one category ID, category group ID, or flex=True on each side, using the from_/to_ arguments.
IDs come from GetCategories. Use the category/group/flex line shown by GetBudget.
The source must have sufficient remaining budget. Does not change future months or move real money.
To change defaults, use SetBudgetAmount; its apply_to_future overwrites later months' explicit amounts.
Recategorizing transactions changes actuals, not planned amounts.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `amount` | `number` | Yes | — |  |
| `from_category_group_id` | `string | null` | No | None |  |
| `from_category_id` | `string | null` | No | None |  |
| `from_flex` | `boolean` | No | False |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `month` | `string` | Yes | — |  |
| `to_category_group_id` | `string | null` | No | None |  |
| `to_category_id` | `string | null` | No | None |  |
| `to_flex` | `boolean` | No | False |  |

---

### `ReduceGoalAllocation`

Reduce how much of an account's balance is allocated to a savings goal.

The amount must be positive and cannot exceed what is currently allocated to the goal from that
account.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_id` | `string` | Yes | — | Account ID (GetAccounts) the allocation was made from. |
| `amount` | `number` | Yes | — | Positive amount to reduce the allocation by. |
| `date` | `string | null` | No | None | Optional ISO date (YYYY-MM-DD) for the reduction; defaults to today. |
| `goal_id` | `string` | Yes | — | Goal ID from GetGoals. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `notes` | `string | null` | No | None | Optional free-text note. |

---

### `ReportIssue`

Report when something seemed off during this session.

Records an issue such as a tool returning unexpected or confusing output,
data that looks self-contradictory, or an earlier answer that was wrong.
Reports persist for later review and analysis.

Free-text fields (`summary`, `details`) are stored only in the
database — they are NOT written to observability/log pipelines. Even so,
avoid pasting raw user financial data into these fields when you can
describe the problem without it.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `category` | `string | null` | No | None | optional — tool_output, data_quality, or other. |
| `details` | `string` | Yes | — | longer description — what you saw, what you expected, why it seems wrong (max 2000 characters). |
| `summary` | `string` | Yes | — | short headline of what's wrong (max 200 characters). |
| `tool_name` | `string | null` | No | None | optional — the MCP tool involved, when an issue is tied to a specific tool. |

---

### `SetBudgetAmount`

Set the planned budget amount for a month (ISO YYYY-MM-DD, normalized to month start).

Choose exactly one category_id, category_group_id, or flex=True. IDs come from GetCategories.
Use the line GetBudget reports: group budgets require group budgeting; flexible expenses use flex=True.
apply_to_future=True overwrites later months' explicit amounts as well as setting the default going forward.
Default False changes only this month. Recategorizing transactions changes actuals, not planned amounts.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `amount` | `number` | Yes | — |  |
| `apply_to_future` | `boolean` | No | False |  |
| `category_group_id` | `string | null` | No | None |  |
| `category_id` | `string | null` | No | None |  |
| `flex` | `boolean` | No | False |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `month` | `string` | Yes | — |  |

---

### `UpdateAccountBalanceHistory`

Write balance history to a manual account, replacing the dates the entries cover.

Uploads historical balances for an account that does not sync from an institution. Find the
account id with GetAccounts; only manual accounts can be written. To read existing history, use
GetNetWorthHistory(include_account_breakdown=true, accounts=[...]).

The dates spanned by `balances` are rewritten: existing snapshots in that range are deleted,
days with no entry carry the previous balance forward (one snapshot per day), and the account's
current balance is updated when the upload reaches the most recent data point.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_id` | `string` | Yes | — | ID of a manual account (from GetAccounts). |
| `balances` | `string` | Yes | — | JSON list of {"date": "YYYY-MM-DD", "balance": number} entries. Balance is signed the same way GetAccounts reports it: positive for assets, negative for amounts owed on liabilities. A single entry sets that one day's balance. |
| `dry_run` | `boolean` | No | False | if true, returns a preview (date range, snapshots to write, existing snapshots that would be replaced, whether the current balance would change) without writing. Call once with dry_run=true to show the user the effect, then again with dry_run=false to commit. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |

---

### `UpdateAccountDebtDetails`

Update debt details stored on an account.

Rates are percentages: 6.99 means 6.99%. Use `apr` for credit cards and
`interest_rate` for loans and other debts; `rate_field` in GetDebtPaydownPlan
indicates which field to use. Pass only the fields to change.

Values are saved on the account itself and apply everywhere in Monarch (account details, Debt Paydown plan, budgets), not just this conversation.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_id` | `string` | Yes | — |  |
| `apr` | `number | null` | No | None |  |
| `exclude_from_debt_paydown` | `boolean | null` | No | None |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `interest_rate` | `number | null` | No | None |  |
| `minimum_payment` | `number | null` | No | None |  |
| `planned_payment` | `number | null` | No | None |  |

---

### `UpdateCategory`

Rename, re-group, or re-icon a custom category. System categories cannot be modified.

Pass only the fields you want to change. `group_id` is a category group ID from GetCategories.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `category_id` | `string` | Yes | — |  |
| `group_id` | `string | null` | No | None |  |
| `icon` | `string | null` | No | None |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `name` | `string | null` | No | None |  |

---

### `UpdateGoal`

Edit a savings goal and/or change which accounts count toward it. Pass only the fields you want to change.

Linking an account counts that account's whole balance toward the goal in Monarch's tracking;
unlinking stops counting it. Account IDs come from GetAccounts. The goal ID comes from GetGoals.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_ids_to_link` | `array | null` | No | None | Account IDs (GetAccounts) to link to this goal. |
| `account_ids_to_unlink` | `array | null` | No | None | Account IDs to unlink from this goal. |
| `goal_id` | `string` | Yes | — | Goal ID from GetGoals. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `is_sinking_fund` | `boolean | null` | No | None |  |
| `name` | `string | null` | No | None |  |
| `target_amount` | `number | null` | No | None |  |
| `target_date` | `string | null` | No | None |  |

---

### `UpdateMerchant`

Rename a merchant and return the updated merchant, including its `merchant_id` and new name.

The new name applies to every transaction and rule that uses this merchant.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `merchant_id` | `string` | Yes | — | ID of the merchant to rename (from GetMerchants / GetTransactions / ListRules). |
| `new_name` | `string` | Yes | — | New name. On a case-insensitive name collision, use MergeMerchants to combine merchants. |

---

### `UpdateRule`

Update a transaction rule. Use ListRules first to find its rule_id. Only supplied params change.

Pass [] to clear merchant_names, category_ids, account_ids, or add_tag_ids; pass "" to clear
set_merchant_id or set_category_id; pass False to clear set_hide_from_reports. Pass
set_needs_review=False or set_reviewed=False to clear only a matching current review status;
those two flags cannot both be True. Passing only amount_min or only amount_max keeps the
rule's other existing bound. For an exact-amount rule, give both bounds or use clear_amount=True
with bounds to replace it; a one-bound edit without clear_amount is rejected. Use clear_amount=True
alone to remove amount criteria, or with bounds to set exactly those bounds (e.g. drop a max).
Bounds must be positive amounts (zero is allowed), and keep the rule's existing income/expense
direction. Clearing the last criterion or action is not allowed.

Goal links, ownership, business entity, splits, and notifications are not exposed here and are kept.
Edits only affect future transactions; transactions the rule already changed are not updated or
reverted. Returns the updated rule and a 'user_notice' explaining how to apply it to existing
transactions in Monarch.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `account_ids` | `array | null` | No | None |  |
| `add_tag_ids` | `array | null` | No | None |  |
| `amount_max` | `number | null` | No | None |  |
| `amount_min` | `number | null` | No | None |  |
| `category_ids` | `array | null` | No | None |  |
| `clear_amount` | `boolean` | No | False |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `merchant_names` | `array | null` | No | None |  |
| `rule_id` | `string` | Yes | — |  |
| `set_category_id` | `string | null` | No | None |  |
| `set_hide_from_reports` | `boolean | null` | No | None |  |
| `set_merchant_id` | `string | null` | No | None |  |
| `set_needs_review` | `boolean | null` | No | None |  |
| `set_reviewed` | `boolean | null` | No | None |  |

---

### `UpdateTag`

Rename a tag and/or change its color. Pass only the fields you want to change.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `color` | `string | null` | No | None |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `name` | `string | null` | No | None |  |
| `tag_id` | `string` | Yes | — |  |

---

### `UpdateTransaction`

Update fields on a single transaction. Pass only the fields you want to change.

Cross-entity references are by ID — look them up with the read tools first.
Dates can be changed on manual and synced transactions. Amount can only be changed
on manual transactions; synced transactions return an error for amount changes.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `amount` | `number | null` | No | None | Signed amount. Manual transactions only. |
| `business_entity_id` | `string | null` | No | None |  |
| `category_id` | `string | null` | No | None |  |
| `date` | `string | null` | No | None | ISO date (YYYY-MM-DD). |
| `hide_from_reports` | `boolean | null` | No | None |  |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `is_recurring` | `boolean | null` | No | None |  |
| `merchant_id` | `string | null` | No | None |  |
| `needs_review_by_user_id` | `string | null` | No | None | Household member ID (from GetHouseholdMembers) who should review this. |
| `notes` | `string | null` | No | None |  |
| `owner_is_joint` | `boolean | null` | No | None | Set true for shared ownership. |
| `owner_user_id` | `string | null` | No | None | Household member ID for ownership; or set owner_is_joint=true for shared. Do not pass both. |
| `review_status` | `string | null` | No | None | 'needs_review' or 'reviewed'. |
| `tag_ids` | `array | null` | No | None | List of tag IDs (from GetTags). Replaces the existing tag set on the transaction (pass [] to clear all tags). |
| `transaction_id` | `string` | Yes | — | ID from GetTransactions. |

---

### `UpdateTransactionSplits`

Replace the splits on a transaction.

#### Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :---: | :--- | :--- |
| `dry_run` | `boolean` | No | False | if true, returns a preview ({transaction_amount, current_splits, proposed_splits, proposed_split_count}) without writing. Call once with dry_run=true to show the user the proposed split structure, then call again with dry_run=false to commit. |
| `intent` | `string` | Yes | — | The general financial task this call supports. Pick the closest category; use 'other' only when none fit. |
| `intent_description` | `string | null` | No | None | Required only when intent is 'other'. A generic 2-5 word label for the task category, e.g. 'retirement planning' or 'rent affordability'. Name the task, never the reason behind it: no names, relationships, life events, health, legal, or employment details from the conversation. Bad: 'because the user is getting divorced'. Good: 'household budgeting'. |
| `splits` | `string` | Yes | — | JSON list. Pass `[]` to unsplit. Each entry must include `amount` (signed the same way as the parent; outflow negative) and may include `merchant_id`, `category_id`, `notes`, `hide_from_reports`, `tag_ids`. Cross-entity references are IDs from the read tools. Amounts must sum to the parent's amount. |
| `transaction_id` | `string` | Yes | — | ID of the parent transaction. |

---
