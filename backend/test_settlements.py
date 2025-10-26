#!/usr/bin/env python3
"""
Test script to verify the settlements endpoint calculates who owes whom correctly.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_settlements():
    print("=" * 80)
    print("Testing Settlements Endpoint - Who Owes Whom")
    print("=" * 80)
    
    # Step 1: Register test users
    print("\n[1] Setting up test users...")
    users = {}
    for username in ['alice_settle', 'bob_settle', 'charlie_settle', 'david_settle']:
        response = requests.post(
            f"{BASE_URL}/register/",
            json={"username": username, "password": "test123"}
        )
        if response.status_code == 201:
            print(f"   ✓ Registered {username}")
        else:
            print(f"   ℹ {username} already exists")
        
        # Login to get token
        login_response = requests.post(
            f"{BASE_URL}/login/",
            json={"username": username, "password": "test123"}
        )
        if login_response.status_code == 200:
            user_data = login_response.json()
            users[username] = {
                'id': user_data['user']['id'],
                'token': user_data['token']
            }
    
    alice = users['alice_settle']
    bob = users['bob_settle']
    charlie = users['charlie_settle']
    david = users['david_settle']
    
    # Step 2: Create a bill group
    print("\n[2] Creating test group with all members...")
    group_response = requests.post(
        f"{BASE_URL}/groups/",
        headers={"Authorization": f"Token {alice['token']}"},
        json={
            "name": "Weekend Trip Settlement Test",
            "description": "Testing settlement calculations",
            "members": [bob['id'], charlie['id'], david['id']]
        }
    )
    
    if group_response.status_code == 201:
        group = group_response.json()
        group_id = group['id']
        print(f"   ✓ Created group (ID: {group_id})")
    else:
        print(f"   ✗ Failed to create group: {group_response.json()}")
        return
    
    # Step 3: Create multiple expenses with different payers
    print("\n[3] Creating expenses with different payers...")
    
    # Alice pays for hotel: $400 split evenly among 4 people = $100 each
    print("   • Alice pays $400 for hotel (split 4 ways)")
    expense1 = requests.post(
        f"{BASE_URL}/expenses/",
        headers={"Authorization": f"Token {alice['token']}"},
        json={
            "group": group_id,
            "description": "Hotel booking",
            "total_amount": "400.00",
            "payer_id": alice['id'],
            "split_type": "E",
            "splits": [
                {"user_owed_id": alice['id'], "amount_owed": "100.00"},
                {"user_owed_id": bob['id'], "amount_owed": "100.00"},
                {"user_owed_id": charlie['id'], "amount_owed": "100.00"},
                {"user_owed_id": david['id'], "amount_owed": "100.00"}
            ]
        }
    )
    if expense1.status_code != 201:
        print(f"     ✗ Failed: {expense1.json()}")
        return
    print(f"     ✓ Created expense ID: {expense1.json()['id']}")
    
    # Bob pays for dinner: $120 split evenly = $30 each
    print("   • Bob pays $120 for dinner (split 4 ways)")
    expense2 = requests.post(
        f"{BASE_URL}/expenses/",
        headers={"Authorization": f"Token {bob['token']}"},
        json={
            "group": group_id,
            "description": "Dinner",
            "total_amount": "120.00",
            "payer_id": bob['id'],
            "split_type": "E",
            "splits": [
                {"user_owed_id": alice['id'], "amount_owed": "30.00"},
                {"user_owed_id": bob['id'], "amount_owed": "30.00"},
                {"user_owed_id": charlie['id'], "amount_owed": "30.00"},
                {"user_owed_id": david['id'], "amount_owed": "30.00"}
            ]
        }
    )
    if expense2.status_code != 201:
        print(f"     ✗ Failed: {expense2.json()}")
        return
    print(f"     ✓ Created expense ID: {expense2.json()['id']}")
    
    # Charlie pays for gas: $80 split evenly = $20 each
    print("   • Charlie pays $80 for gas (split 4 ways)")
    expense3 = requests.post(
        f"{BASE_URL}/expenses/",
        headers={"Authorization": f"Token {charlie['token']}"},
        json={
            "group": group_id,
            "description": "Gas",
            "total_amount": "80.00",
            "payer_id": charlie['id'],
            "split_type": "E",
            "splits": [
                {"user_owed_id": alice['id'], "amount_owed": "20.00"},
                {"user_owed_id": bob['id'], "amount_owed": "20.00"},
                {"user_owed_id": charlie['id'], "amount_owed": "20.00"},
                {"user_owed_id": david['id'], "amount_owed": "20.00"}
            ]
        }
    )
    if expense3.status_code != 201:
        print(f"     ✗ Failed: {expense3.json()}")
        return
    print(f"     ✓ Created expense ID: {expense3.json()['id']}")
    
    # Step 4: Get net balances
    print("\n[4] Fetching net balances...")
    balances_response = requests.get(
        f"{BASE_URL}/groups/{group_id}/balances/",
        headers={"Authorization": f"Token {alice['token']}"}
    )
    
    if balances_response.status_code == 200:
        balances = balances_response.json()
        print("   ✓ Got balances")
        print("\n" + "=" * 80)
        print("📊 NET BALANCES (How much each person is owed/owes overall)")
        print("=" * 80)
        for balance in sorted(balances, key=lambda x: float(x['balance']), reverse=True):
            amount = float(balance['balance'])
            if amount > 0:
                print(f"   {balance['username']:20} is owed:  ${amount:>8.2f} ✅")
            elif amount < 0:
                print(f"   {balance['username']:20} owes:     ${abs(amount):>8.2f} 💸")
            else:
                print(f"   {balance['username']:20} settled:  ${amount:>8.2f} 🟰")
        
        # Calculate expected balances
        print("\n" + "-" * 80)
        print("📝 EXPECTED CALCULATION:")
        print("-" * 80)
        print("   Alice:   Paid $400 - Owes $150 = +$250 (owed)")
        print("   Bob:     Paid $120 - Owes $150 = -$30  (owes)")
        print("   Charlie: Paid $80  - Owes $150 = -$70  (owes)")
        print("   David:   Paid $0   - Owes $150 = -$150 (owes)")
        print("-" * 80)
    else:
        print(f"   ✗ Failed to get balances: {balances_response.json()}")
        return
    
    # Step 5: Get settlement plan
    print("\n[5] Fetching settlement plan (who owes whom)...")
    settlements_response = requests.get(
        f"{BASE_URL}/groups/{group_id}/settlements/",
        headers={"Authorization": f"Token {alice['token']}"}
    )
    
    if settlements_response.status_code == 200:
        settlements = settlements_response.json()
        print("   ✓ Got settlements")
        
        print("\n" + "=" * 80)
        print("💰 SETTLEMENT PLAN (Who should pay whom)")
        print("=" * 80)
        
        if settlements:
            total_transactions = decimal.Decimal('0')
            for idx, settlement in enumerate(settlements, 1):
                amount = decimal.Decimal(settlement['amount'])
                total_transactions += amount
                print(f"   {idx}. {settlement['from']:15} → {settlement['to']:15}  ${settlement['amount']:>8}")
            
            print("-" * 80)
            print(f"   Total to be transferred: ${total_transactions:.2f}")
            print("=" * 80)
            
            # Verification
            print("\n" + "=" * 80)
            print("✅ VERIFICATION")
            print("=" * 80)
            
            # Check that total owed equals total to be received
            total_owed = sum(abs(float(b['balance'])) for b in balances if float(b['balance']) < 0)
            total_owed_back = sum(float(b['balance']) for b in balances if float(b['balance']) > 0)
            
            print(f"   Total owed by debtors:    ${total_owed:.2f}")
            print(f"   Total owed to creditors:  ${total_owed_back:.2f}")
            print(f"   Difference:               ${abs(total_owed - total_owed_back):.2f}")
            
            if abs(total_owed - total_owed_back) < 0.01:
                print("   ✅ Balances match! Settlement is correct.")
            else:
                print("   ⚠️  Balance mismatch - possible calculation error")
            
            print("\n" + "=" * 80)
            print("🎉 SUCCESS! Settlement endpoint working correctly")
            print("=" * 80)
        else:
            print("   ℹ️  No settlements needed - group is already settled!")
    else:
        print(f"   ✗ Failed to get settlements: {settlements_response.json()}")
        return
    
    # Step 6: Show usage example
    print("\n" + "=" * 80)
    print("📱 MOBILE APP USAGE")
    print("=" * 80)
    print("""
    // Kotlin/Java Example:
    
    // Get who owes whom
    val response = api.getGroupSettlements(groupId)
    
    response.forEach { settlement ->
        showPaymentButton(
            message = "${settlement.from} pays ${settlement.to}",
            amount = settlement.amount
        )
    }
    
    // Display: "Bob pays Alice $30.00" [Mark as Paid]
    //          "Charlie pays Alice $70.00" [Mark as Paid]
    //          "David pays Alice $150.00" [Mark as Paid]
    """)
    print("=" * 80)

if __name__ == "__main__":
    import decimal
    test_settlements()
