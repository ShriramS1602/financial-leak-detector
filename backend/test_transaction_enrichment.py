#!/usr/bin/env python
"""
Test script for transaction enrichment logic
Tests Level 1, Level 2, Level 3 tags and Merchant extraction
"""

import pandas as pd
import sys
from datetime import datetime
from app.core.transaction_processor import TransactionEnricher, PatternConfig

def enrich_transaction(narration: str, withdrawal_amount: float = 0, deposit_amount: float = 0):
    """
    Test a single transaction enrichment
    
    Args:
        narration: Transaction description/narration
        withdrawal_amount: Withdrawal amount (default 0)
        deposit_amount: Deposit amount (default 0)
    
    Returns:
        Dict with enriched transaction data
    """
    
    # Create a simple dataframe with the transaction
    df = pd.DataFrame({
        PatternConfig.DATE_COLUMN: [datetime.now()],
        PatternConfig.NARRATION_COLUMN: [narration],
        PatternConfig.AMOUNT_COLUMNS[0]: [withdrawal_amount],  # Withdrawal Amt.
        PatternConfig.AMOUNT_COLUMNS[1]: [deposit_amount],      # Deposit Amt.
    })
    
    # Apply enrichment steps
    df = TransactionEnricher.add_money_flow(df)
    df = TransactionEnricher.add_level_1_tag(df, narration_col=PatternConfig.NARRATION_COLUMN)
    df = TransactionEnricher.add_level_2_tag(df)
    df = TransactionEnricher.add_level_3_tag(df)
    df = TransactionEnricher.add_merchant_hint(df, narration_col=PatternConfig.NARRATION_COLUMN)
    
    # Extract results
    result = {
        "narration": narration,
        "withdrawal_amount": withdrawal_amount,
        "deposit_amount": deposit_amount,
        "money_flow": df["money_flow"].iloc[0],
        "level_1_tag": df["level_1_tag"].iloc[0],
        "level_2_tag": df["level_2_tag"].iloc[0],
        "level_3_tag": df["level_3_tag"].iloc[0],
        "merchant_hint": df["merchant_hint"].iloc[0],
    }
    
    return result


def print_result(result: dict):
    """Pretty print the enrichment result"""
    print("\n" + "="*70)
    print(f"NARRATION: {result['narration']}")
    print("="*70)
    print(f"Withdrawal Amount: {result['withdrawal_amount']}")
    print(f"Deposit Amount:    {result['deposit_amount']}")
    print("-"*70)
    print(f"💰 Money Flow:     {result['money_flow']}")
    print(f"🔌 Level 1 Tag:    {result['level_1_tag']} (Payment Rail)")
    print(f"📊 Level 2 Tag:    {result['level_2_tag']} (Transaction Role)")
    print(f"🏷️  Level 3 Tag:    {result['level_3_tag']} (Spending Category)")
    print(f"🏪 Merchant Hint:  {result['merchant_hint']}")
    print("="*70 + "\n")


def main():
    """Main test function"""
    
    # Test cases
    test_cases = [
        # (narration, withdrawal, deposit)
        ("TO ONL UPI/DR/503588113656/CHAI WAA/YESB/PAYTM-7320/U::00271", 450, 0),
                ("TO ONL UPI-DR-03588113656-CHAI WAA-YESB-PAYTM-732-U::00271", 450, 0),
    ]
    
    print("\n" + "#"*70)
    print("# TRANSACTION ENRICHMENT TEST SCRIPT")
    print("#"*70)
    print(f"\nTesting {len(test_cases)} transactions...\n")
    
    results = []
    for narration, withdrawal, deposit in test_cases:
        try:
            result = enrich_transaction(narration, withdrawal, deposit)
            results.append(result)
            print_result(result)
        except Exception as e:
            print(f"❌ Error processing '{narration}': {str(e)}")
            continue
    
    # Summary table
    print("\n" + "#"*70)
    print("# SUMMARY TABLE")
    print("#"*70 + "\n")
    
    summary_df = pd.DataFrame([
        {
            "Narration": r["narration"][:40] + "..." if len(r["narration"]) > 40 else r["narration"],
            "Level 1": r["level_1_tag"],
            "Level 2": r["level_2_tag"],
            "Level 3": r["level_3_tag"],
            "Merchant": r["merchant_hint"][:20] + "..." if len(r["merchant_hint"]) > 20 else r["merchant_hint"],
        }
        for r in results
    ])
    
    print(summary_df.to_string(index=False))
    print("\n" + "#"*70 + "\n")


if __name__ == "__main__":
    main()
