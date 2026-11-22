# Monarch MCP Agent Guide

This guide explains how to use the `monarch-mcp` server efficiently and safely. It covers non-obvious tool behaviors, data quirks, and workflow patterns that are not immediately clear from the tool schemas alone.

## 1. Core Rules of the Server

1. **IDs Only on Writes**: Every write tool (`UpdateTransaction`, `BulkUpdateTransactions`, `CreateRule`, `MergeMerchants`, etc.) requires stable numeric ID strings returned by the read tools. Never pass category, tag, or merchant names to write tools.
2. **Required `intent` Parameter**: Every tool requires an `intent` enum value (such as `"organizing_finances"`, `"spending_analysis"`, or `"budgeting"`). Avoid `"other"` unless necessary; if you use `"other"`, keep `intent_description` generic (2 to 5 words describing the task, never personal user details).
3. **JSON-Encoded Strings for `filters` and `updates`**:
   - In `GetTransactions`, `BulkUpdateTransactions`, and `BulkRecategorizeTransactions`, the `filters` and `updates` parameters take a **serialized JSON string**, not a nested object.
   - Good: `updates: "{\"tag_ids\": [\"123456789012345678\"]}"`
   - Bad: `updates: {"tag_ids": ["123456789012345678"]}`

## 2. Recommended Discovery Workflow

Before querying transactions, run these lightweight read calls in parallel to map the account structure:
1. `GetCategories`: Returns all category groups and categories (including custom and disabled ones) with their IDs.
2. `GetTags`: Returns all tags, their IDs, and `transaction_count` (how many transactions currently use each tag).
3. `ListRules`: Shows how the user currently automates categorization, merchant renaming, and tagging.
4. `GetTransactions(total_count_only=True, start_date=..., end_date=...)`: Returns the exact transaction count for a date range so you know how many pages to fetch.

## 3. Fetching Transactions Efficiently (`GetTransactions`)

### Summary Mode vs. Detail Mode (`include_details`)
`GetTransactions` has two very different operating modes:

- **Summary Mode (`include_details=False`, default)**:
  - Returns up to `limit=100` transactions per call with `id`, `date`, `amount`, `pending`, `merchant`, `merchant_id`, `category`, `category_id`, `account`, and `account_id`.
  - Use this mode to scan large date ranges. Once you know the total count from `total_count_only=True`, fetch multiple pages in parallel (`offset=0`, `100`, `200`, etc.).
- **Detail Mode (`include_details=True`)**:
  - Adds `cleansed_description` (the raw bank statement description), `tags` / `tag_ids`, `notes`, `review_status`, `is_split`, and `is_recurring`.
  - **Important limit**: Setting `include_details=True` forces a hard maximum of **20 transactions per call**, even if you pass `limit=100`.
  - **Best practice**: Never page through months of history with `include_details=True`. First scan in summary mode (`limit=100`), identify specific dates or merchants that need inspection, and then call `GetTransactions(include_details=True)` on narrow 1-to-3-day date windows.

### Filter String Gotchas
- If you pass a non-empty `filters` JSON string to `GetTransactions`, it **must** include `"transaction_type"` set to `"All"`, `"Debit"`, or `"Credit"`. Omitting `transaction_type` in a non-empty filter causes a validation error.
- Hidden transactions are excluded by default (`"visibility": "visible_only"`).

### Processing Large Outputs
- `GetCategories` and 100-item `GetTransactions` pages produce large JSON responses that are often saved to step output files.
- Instead of reading large JSON files directly into context, run a short Python script via `run_command` to aggregate unique merchants, transaction counts, sums, categories, and IDs across all saved page files at once.

## 4. Hidden Data Quirks You Must Watch For

### 1. Never Trust Merchant Names Alone (The Auto-Cleansing Trap)
Monarch automatically converts raw bank descriptions into merchant names. When a POS terminal truncates a name (for example, `TST*SUNRISECAFE SEATTLE` or `SQ *PINEVALLEYMKT`), Monarch often guesses wrong and creates bizarre merchant names:
- Examples of how truncated POS strings get misparsed:
  - `TST*SUNRISECAFE SEATTLE` (a local cafe) might be turned into `Sunrise`, `Cafe`, or an unrelated business starting with `Sunrise`.
  - `SQ *PINEVALLEYMKT` (Pine Valley Market) might be turned into `Pine Valley`, `Pine`, or a mismatched person/entity name.
  - `SP *OAKRIDGESPORTS` (Oakridge Sports) might be mangled into an unrelated proper name.
- **How to handle this**: When searching for expenses in a domain, do not rely only on substring searches of the merchant name. Scan all unique merchants in the date range, flag suspicious or generic names, and inspect their `cleansed_description` using `include_details=True`. Look for shared POS prefixes like `SQ *`, `TST*`, `SP *`, or industry-specific prefixes.

### 2. Mis-Categorized Charges Hidden in Transfers or Payments
Monarch's auto-categorizer sometimes places real expenses into `Credit Card Payment`, `Transfer`, or `Other Income`:
- Any expense categorized under `Credit Card Payment` or `Transfer` is excluded from Monarch spending reports and budgets.
- Conversely, merchant refunds (positive amounts) often land in `Other Income`. Moving a refund into the same expense category as the original charge properly offsets net spending in that category.

### 3. `tag_ids` Replaces Existing Tags
In both `UpdateTransaction` and `BulkUpdateTransactions`, passing `tag_ids` **overwrites** the transaction's entire tag list (`[]` removes all tags).
- Before running a bulk tag update, check `GetTags` (if all tags have `transaction_count: 0`, no transactions have tags) or inspect the target transactions with `include_details=True` so you do not wipe out existing tags.

## 5. Choosing the Right Write Tool

### Updating Transactions
- **`BulkRecategorizeTransactions`**: Best when you only need to change `category_id` (up to 500 transactions per call). Supports matching by `filters` (`start_date`, `end_date`, `merchant_id`, `category_id`, `account_id`) or explicit `transaction_ids`.
- **`BulkUpdateTransactions`**: Best when updating `tag_ids`, `notes`, `review_status`, `hide_from_reports`, or multiple fields at once on up to 500 `transaction_ids`.
- **Dry Run**: Both bulk tools support `dry_run=True` to preview `would_affect_count` before committing changes.

### Cleaning Up Duplicate Merchants (`MergeMerchants` + `UpdateMerchant`)
When bank descriptions create multiple merchant records for the same business, do not update `merchant_id` on individual transactions. Instead:
1. Pick one target `merchant_id` to keep.
2. Call `MergeMerchants(target_merchant_id=..., source_merchant_ids=[...])` (up to 25 source IDs per call). This automatically re-points every historical transaction across all years and every rule to the target merchant, then deletes the source merchants.
3. Call `UpdateMerchant(merchant_id=..., new_name=...)` to give the kept merchant a clean display name.

## 6. Categories vs. Tags vs. Rules

- **Categories vs. Tags**:
  - A transaction can have **only one Category** (unless split via `UpdateTransactionSplits`), which controls budgets and category spending charts.
  - A transaction can have **multiple Tags**, which work across categories (useful for trips, reimbursements, hobbies, or sub-types within a category).
- **Rules (`CreateRule` / `UpdateRule`)**:
  - Rules **only apply to future transactions**. Creating or updating a rule never modifies existing transactions; always pair rule creation with `BulkUpdateTransactions` or `BulkRecategorizeTransactions` if historical data needs updating.
  - A rule's `merchant_names` list matches literal text substrings, while `set_merchant_id` can only point to **one** merchant.
  - Therefore, a single catch-all rule matching 10 different businesses can set `set_category_id` and `add_tag_ids`, but **cannot** set `set_merchant_id`. To auto-rename mangled merchants on future charges, create one rule per merchant that sets both `set_merchant_id` and `set_category_id`.
