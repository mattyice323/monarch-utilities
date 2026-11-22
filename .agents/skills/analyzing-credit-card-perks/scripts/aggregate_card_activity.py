#!/usr/bin/env python3
"""Aggregate Monarch Money GetTransactions JSON pages for credit card perk analysis.

Usage:
    python3 aggregate_card_activity.py --start YYYY-MM-DD --end YYYY-MM-DD <json_files...>
"""

import argparse
from collections import defaultdict
import json
import sys


def load_transactions(paths, start_date, end_date):
    txs = {}
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for t in data.get("transactions", []):
            date = t.get("date", "")
            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue
            txs[t["id"]] = t
    return txs


def main():
    parser = argparse.ArgumentParser(description="Aggregate Monarch transactions by account, category, and credits.")
    parser.add_argument("--start", default="", help="Start date inclusive (YYYY-MM-DD)")
    parser.add_argument("--end", default="", help="End date inclusive (YYYY-MM-DD)")
    parser.add_argument("--max-small-credit", type=float, default=150.0, help="Threshold to surface positive credits inside payment/transfer categories")
    parser.add_argument("files", nargs="+", help="Paths to saved GetTransactions JSON output files")
    args = parser.parse_args()

    txs = load_transactions(args.files, args.start, args.end)
    print(f"Total unique transactions loaded: {len(txs)}")
    if not txs:
        return 0

    all_dates = sorted(t.get("date", "") for t in txs.values() if t.get("date"))
    print(f"Date range covered: {all_dates[0]} to {all_dates[-1]}")

    by_account = defaultdict(list)
    for t in txs.values():
        by_account[t.get("account", "Unknown Account")].append(t)

    for acct, items in sorted(by_account.items(), key=lambda kv: -len(kv[1])):
        acct_dates = sorted(x.get("date", "") for x in items if x.get("date"))
        debits = [
            x for x in items
            if x.get("amount", 0) < 0 and x.get("category") not in ("Credit Card Payment", "Transfer")
        ]
        # Include all non-payment positive credits AND small positive credits (< max_small_credit)
        # even if Monarch auto-categorized them as Credit Card Payment or Transfer.
        perk_credits = [
            x for x in items
            if x.get("amount", 0) > 0 and (
                x.get("category") not in ("Credit Card Payment", "Transfer", "Paychecks")
                or x.get("amount", 0) < args.max_small_credit
            )
        ]

        debit_sum = sum(-x.get("amount", 0) for x in debits)
        credit_sum = sum(x.get("amount", 0) for x in perk_credits)

        print(f"\n======================================================================")
        print(f"ACCOUNT: {acct}")
        print(f"Active dates: {acct_dates[0]} to {acct_dates[-1]} | Total txs: {len(items)}")
        print(f"Purchases: {len(debits)} txs (${debit_sum:,.2f}) | Candidate Credits/Rebates: {len(perk_credits)} txs (+${credit_sum:,.2f})")

        if perk_credits:
            print("\n  Candidate Statement Credits & Rebates (amount > 0):")
            for c in sorted(perk_credits, key=lambda x: x.get("date", "")):
                print(
                    f"    {c.get('date')} | {c.get('merchant') or 'Unknown'} | "
                    f"+${c.get('amount', 0):.2f} | Category: {c.get('category')}"
                )

        cat_totals = defaultdict(lambda: [0, 0.0, defaultdict(float)])
        for x in debits:
            cat = x.get("category") or "Uncategorized"
            merch = x.get("merchant") or "Unknown"
            amt = -x.get("amount", 0)
            cat_totals[cat][0] += 1
            cat_totals[cat][1] += amt
            cat_totals[cat][2][merch] += amt

        if cat_totals:
            print("\n  Spend by Category (with top merchants):")
            for cat, (cnt, amt, merch_map) in sorted(cat_totals.items(), key=lambda kv: -kv[1][1]):
                top_m = sorted(merch_map.items(), key=lambda kv: -kv[1])[:4]
                top_str = ", ".join(f"{m} (${a:,.2f})" for m, a in top_m)
                print(f"    {cat}: {cnt} txs, ${amt:,.2f} -> [{top_str}]")

        # Also check outbound Credit Card Payments / Transfers to spot unlinked cards
        cc_payments = [
            x for x in items
            if x.get("amount", 0) < 0 and x.get("category") in ("Credit Card Payment", "Loan Repayment")
        ]
        if cc_payments:
            pmt_by_merch = defaultdict(lambda: [0, 0.0])
            for x in cc_payments:
                m = x.get("merchant") or "Unknown"
                pmt_by_merch[m][0] += 1
                pmt_by_merch[m][1] += -x.get("amount", 0)
            print("\n  Outbound Card / Loan Payments from this account:")
            for m, (cnt, amt) in sorted(pmt_by_merch.items(), key=lambda kv: -kv[1][1]):
                print(f"    {m}: {cnt} payments, ${amt:,.2f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
