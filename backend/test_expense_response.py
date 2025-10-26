#!/usr/bin/env python3
"""
Test script to verify that GET /api/groups/<id>/ now includes payer information.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_expense_response():
    print("=" * 80)
    print("Testing Expense GET Response with Payer Information")
    print("=" * 80)
    
    # Step 1: Register test users
    print("\n[1] Registering test users...")
    users = []
    for username in ['alice_test', 'bob_test', 'charlie_test']:
        response = requests.post(
            f"{BASE_URL}/register/",
            json={"username": username, "password": "test123"}
        )
        if response.status_code == 201:
            print(f"   ✓ Registered {username}")
            users.append(response.json())
        elif "username" in response.json() and "already exists" in str(response.json()["username"]):
            # User already exists, login to get token
            print(f"   ℹ {username} already exists, logging in...")
            login_response = requests.post(
                f"{BASE_URL}/login/",
                json={"username": username, "password": "test123"}
            )
            if login_response.status_code == 200:
                user_data = login_response.json()['user']
                user_data['token'] = login_response.json()['token']
                users.append(user_data)
        else:
            print(f"   ✗ Failed to register {username}: {response.json()}")
            return
    
    # Get tokens for each user
    tokens = {}
    for i, username in enumerate(['alice_test', 'bob_test', 'charlie_test']):
        response = requests.post(
            f"{BASE_URL}/login/",
            json={"username": username, "password": "test123"}
        )
        if response.status_code == 200:
            tokens[username] = response.json()['token']
            print(f"   ✓ Got token for {username}")
        else:
            print(f"   ✗ Failed to login {username}")
            return
    
    # Step 2: Create a bill group with Alice as creator
    print("\n[2] Creating bill group with members...")
    alice_token = tokens['alice_test']
    
    # Get user IDs
    alice_id = users[0]['id']
    bob_id = users[1]['id']
    charlie_id = users[2]['id']
    
    group_response = requests.post(
        f"{BASE_URL}/groups/",
        headers={"Authorization": f"Token {alice_token}"},
        json={
            "name": "Test Expense Group",
            "description": "Testing payer field in response",
            "members": [bob_id, charlie_id]
        }
    )
    
    if group_response.status_code == 201:
        group = group_response.json()
        group_id = group['id']
        print(f"   ✓ Created group (ID: {group_id})")
        print(f"   Members: {[m['username'] for m in group['members']]}")
    else:
        print(f"   ✗ Failed to create group: {group_response.json()}")
        return
    
    # Step 3: Create an expense with Alice as payer
    print("\n[3] Creating expense with Alice as payer...")
    expense_response = requests.post(
        f"{BASE_URL}/expenses/",
        headers={"Authorization": f"Token {alice_token}"},
        json={
            "group": group_id,
            "description": "Dinner at Italian Restaurant",
            "total_amount": "90.00",
            "payer_id": alice_id,
            "split_type": "E",
            "splits": [
                {"user_owed_id": alice_id, "amount_owed": "30.00"},
                {"user_owed_id": bob_id, "amount_owed": "30.00"},
                {"user_owed_id": charlie_id, "amount_owed": "30.00"}
            ]
        }
    )
    
    if expense_response.status_code == 201:
        expense = expense_response.json()
        print(f"   ✓ Created expense (ID: {expense['id']})")
    else:
        print(f"   ✗ Failed to create expense: {expense_response.json()}")
        return
    
    # Step 4: GET the group details and check if payer info is present
    print("\n[4] Fetching group details to verify payer information...")
    group_detail_response = requests.get(
        f"{BASE_URL}/groups/{group_id}/",
        headers={"Authorization": f"Token {alice_token}"}
    )
    
    if group_detail_response.status_code == 200:
        group_detail = group_detail_response.json()
        print(f"   ✓ Fetched group details")
        
        print("\n" + "=" * 80)
        print("📋 GROUP DETAIL RESPONSE")
        print("=" * 80)
        print(json.dumps(group_detail, indent=2))
        
        # Verify payer information is present
        print("\n" + "=" * 80)
        print("✅ VERIFICATION RESULTS")
        print("=" * 80)
        
        if group_detail['expenses']:
            expense = group_detail['expenses'][0]
            
            checks = [
                ("payer field present", "payer" in expense),
                ("payer_username field present", "payer_username" in expense),
                ("date field present", "date" in expense),
                ("splits_read field present", "splits_read" in expense),
                ("payer value correct", expense.get('payer') == alice_id),
                ("payer_username correct", expense.get('payer_username') == 'alice_test'),
            ]
            
            for check_name, result in checks:
                status = "✅" if result else "❌"
                print(f"{status} {check_name}")
            
            # Check splits_read structure
            if "splits_read" in expense and expense['splits_read']:
                print(f"\n📊 Splits Information:")
                for split in expense['splits_read']:
                    print(f"   • {split.get('user_owed_username', 'Unknown')} (ID: {split.get('user_owed')}) owes ${split.get('amount_owed')}")
            
            # Summary
            all_passed = all(result for _, result in checks)
            if all_passed:
                print("\n" + "=" * 80)
                print("🎉 SUCCESS! All payer information is properly included in GET response")
                print("=" * 80)
            else:
                print("\n" + "=" * 80)
                print("⚠️  FAILED! Some fields are missing in GET response")
                print("=" * 80)
        else:
            print("❌ No expenses found in group")
    else:
        print(f"   ✗ Failed to fetch group details: {group_detail_response.json()}")
    
    # Step 5: Test GET /api/expenses/ endpoint
    print("\n[5] Testing GET /api/expenses/ endpoint...")
    expenses_list_response = requests.get(
        f"{BASE_URL}/expenses/",
        headers={"Authorization": f"Token {alice_token}"}
    )
    
    if expenses_list_response.status_code == 200:
        expenses_list = expenses_list_response.json()
        print(f"   ✓ Fetched expenses list")
        if expenses_list:
            expense = expenses_list[0]
            print(f"\n   Expense fields present:")
            print(f"      • payer: {expense.get('payer', 'MISSING')}")
            print(f"      • payer_username: {expense.get('payer_username', 'MISSING')}")
            print(f"      • date: {expense.get('date', 'MISSING')}")
            print(f"      • splits_read: {'Present' if 'splits_read' in expense else 'MISSING'}")
    else:
        print(f"   ✗ Failed to fetch expenses: {expenses_list_response.json()}")

if __name__ == "__main__":
    test_expense_response()
