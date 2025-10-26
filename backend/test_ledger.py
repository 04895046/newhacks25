import requests
import json
import sys

# --- CONFIGURATION ---
BASE_URL = 'http://127.0.0.1:8000'
# We will no longer hardcode IDs. This dict will be filled automatically.
USER_IDS = {
    'alice': None,
    'bob': None,
    'charlie': None
}
USERNAMES = list(USER_IDS.keys())

# --- HELPER FUNCTIONS ---
def print_step(title):
    print("\n" + "="*50)
    print(f" STEP: {title}")
    print("="*50)

def print_response(res):
    try:
        print(f"STATUS: {res.status_code}")
        print("RESPONSE:\n", json.dumps(res.json(), indent=2))
    except json.JSONDecodeError:
        print("RESPONSE: (Not JSON)")
        print(res.text)

def check_balances(balances_data, expected, step_name):
    """Helper to check if balances are correct"""
    print(f"\n--- Checking Balances for {step_name} ---")
    
    balances_map = {item['username']: float(item['balance']) for item in balances_data}
    
    all_match = True
    for username, expected_balance in expected.items():
        if balances_map.get(username) != expected_balance:
            all_match = False
            print(f"  [FAIL] {username}: Expected {expected_balance}, Got {balances_map.get(username)}")
        else:
            print(f"  [PASS] {username}: Expected {expected_balance}, Got {balances_map.get(username)}")
    
    if not all_match:
        print("\n[TEST FAILED!] Balances do not match. Halting.")
        sys.exit(1)
    
    print("--- Balances Match! ---")


# --- TEST SCRIPT ---
session = requests.Session()
auth_tokens = {}
group_id = None

def run_test():
    global group_id

    # --- STEP 1: REGISTER USERS ---
    print_step("Registering Users (Alice, Bob, Charlie)")
    for username in USERNAMES:
        res = session.post(f"{BASE_URL}/api/register/", json={
            "username": username,
            "password": "password123"
        })
        print(f"Registered {username}: {res.status_code}")
        
        if res.status_code == 201:
            # New user created, save their ID
            USER_IDS[username] = res.json()['id']
            print(f"  > User '{username}' created with ID: {USER_IDS[username]}")
        elif res.status_code == 400:
            # User already exists, we need to find their ID
            print(f"  > User '{username}' already exists. Logging in to find ID.")
            # We will find the ID in the login step
            pass
        else:
            print("Failed to register. Exiting.")
            sys.exit(1)

    # --- STEP 2: LOG IN USERS (AND FIND IDs) ---
    print_step("Logging in Users")
    for username in USERNAMES:
        res = session.post(f"{BASE_URL}/api/login/", json={
            "username": username,
            "password": "password123"
        })
        if res.status_code != 200:
            print(f"Failed to log in {username}. Exiting.")
            print_response(res)
            sys.exit(1)
            
        auth_tokens[username] = res.json()['token']
        print(f"Logged in {username}.")
        
        # If we didn't get the ID during registration, get it now.
        if USER_IDS[username] is None:
            # The user already existed. We need to find their ID.
            # Since login doesn't return user data, we must use the UserSerializer fix
            # or require a fresh database.
            print("\n[TEST SCRIPT ERROR] Can't auto-find User IDs for existing users.")
            print("Please DELETE your db.sqlite3 file and run `python manage.py migrate` again.")
            print("Then re-run this test script. It MUST run on a fresh database.")
            sys.exit(1)


    # --- STEP 3: CREATE GROUP (by Alice) ---
    print_step("Creating Group 'Trip to NYC'")
    alice_header = {'Authorization': f'Token {auth_tokens["alice"]}'}
    
    # --- THIS IS THE KEY ---
    # We now use the User IDs we found, not the hardcoded ones.
    member_id_list = [USER_IDS['alice'], USER_IDS['bob'], USER_IDS['charlie']]
    
    res = session.post(f"{BASE_URL}/api/groups/", headers=alice_header, json={
        "name": "Trip to NYC",
        "members": member_id_list
    })
    print_response(res)
    if res.status_code != 201:
        print("Failed to create group. Exiting.")
        sys.exit(1)
    group_id = res.json()['id']
    print(f"Group created with ID: {group_id}")

    # --- STEP 4: ADD SHARED BILL (Alice pays $90 for Dinner) ---
    print_step("Adding Bill 1: Alice pays $90 for Dinner (Even Split)")
    res = session.post(f"{BASE_URL}/api/expenses/", headers=alice_header, json={
        "group": group_id,
        "payer_id": USER_IDS['alice'],
        "description": "Group Dinner",
        "total_amount": "90.00",
        "split_type": "E",
        "splits": [
            {"user_owed_id": USER_IDS['alice'], "amount_owed": "30.00"},
            {"user_owed_id": USER_IDS['bob'], "amount_owed": "30.00"},
            {"user_owed_id": USER_IDS['charlie'], "amount_owed": "30.00"}
        ]
    })
    print_response(res)
    if res.status_code != 201:
        print("Failed to create expense. Exiting.")
        sys.exit(1)

    # --- STEP 5: ADD MANUAL BILL (Bob pays $20 for Charlie) ---
    print_step("Adding Bill 2: Bob pays $20 for Taxi (for Charlie)")
    bob_header = {'Authorization': f'Token {auth_tokens["bob"]}'}
    res = session.post(f"{BASE_URL}/api/expenses/", headers=bob_header, json={
        "group": group_id,
        "payer_id": USER_IDS['bob'],
        "description": "Taxi for Charlie",
        "total_amount": "20.00",
        "split_type": "M",
        "splits": [
            # Only Charlie owes for this
            {"user_owed_id": USER_IDS['charlie'], "amount_owed": "20.00"}
        ]
    })
    print_response(res)
    if res.status_code != 201:
        print("Failed to create expense. Exiting.")
        sys.exit(1)

    # --- STEP 6: CHECK BALANCES (PRE-REPAYMENT) ---
    print_step("Checking Balances (Pre-Repayment)")
    res = session.get(f"{BASE_URL}/api/groups/{group_id}/balances/", headers=alice_header)
    print_response(res)
    # Alice: Paid 90, Owed 30. Net = +60.00
    # Bob:   Paid 20, Owed 30. Net = -10.00
    # Charlie: Paid 0, Owed 30 (Dinner) + 20 (Taxi) = 50. Net = -50.00
    expected_balances_1 = {
        'alice': 60.00,
        'bob': -10.00,
        'charlie': -50.00
    }
    check_balances(res.json(), expected_balances_1, "Step 6")
    
    # --- STEP 7: ADD REPAYMENT (Charlie pays Alice $50) ---
    print_step("Adding Repayment: Charlie pays Alice $50")
    charlie_header = {'Authorization': f'Token {auth_tokens["charlie"]}'}
    res = session.post(f"{BASE_URL}/api/expenses/", headers=charlie_header, json={
        "group": group_id,
        "payer_id": USER_IDS['charlie'],
        "description": "Repayment to Alice",
        "total_amount": "50.00",
        "split_type": "M",
        "splits": [
            # This is a payment TO Alice, so she is the one "owing"
            {"user_owed_id": USER_IDS['alice'], "amount_owed": "50.00"}
        ]
    })
    print_response(res)
    if res.status_code != 201:
        print("Failed to create expense. Exiting.")
        sys.exit(1)
        
    # --- STEP 8: CHECK FINAL BALANCES ---
    print_step("Checking Final Balances")
    res = session.get(f"{BASE_URL}/api/groups/{group_id}/balances/", headers=alice_header)
    print_response(res)
    # Alice: Was +60, received 50 (so 'owed' 50). Net = +10.00
    # Bob:   Was -10. No change. Net = -10.00
    # Charlie: Was -50, paid 50. Net = 0.00
    expected_balances_2 = {
        'alice': 10.00,
        'bob': -10.00,
        'charlie': 0.00
    }
    check_balances(res.json(), expected_balances_2, "Step 8")

    print("\n" + "="*50)
    print("   ALL LEDGER TESTS PASSED SUCCESSFULLY! ")
    print("="*50)
    # ... (Keep all existing code from STEP 1 to STEP 8) ...
    # ... (Right after checking the balances for Step 8) ...

    # --- STEP 9: VALIDATION TEST (Mismatched Splits) ---
    print_step("Adding Bill 3 (VALIDATION): Alice pays $100, splits add to $90")
    # This should fail with a 400 Bad Request
    res = session.post(f"{BASE_URL}/api/expenses/", headers=alice_header, json={
        "group": group_id,
        "payer_id": USER_IDS['alice'],
        "description": "Bad Math Bill",
        "total_amount": "100.00",
        "split_type": "M",
        "splits": [
            {"user_owed_id": USER_IDS['bob'], "amount_owed": "45.00"},
            {"user_owed_id": USER_IDS['charlie'], "amount_owed": "45.00"}
        ]
    })
    
    print_response(res)
    if res.status_code == 400:
        print("  [PASS] Server correctly rejected the request (400 Bad Request).")
    else:
        print(f"  [FAIL] Server accepted mismatched splits! Status: {res.status_code}")
        sys.exit(1)


    # --- STEP 10: VALIDATION TEST (Non-Member Payer) ---
    print_step("Adding Bill 4 (VALIDATION): Charlie tries to add expense with invalid payer")
    # Charlie will try to say a non-existent user (ID 999) paid.
    res = session.post(f"{BASE_URL}/api/expenses/", headers=charlie_header, json={
        "group": group_id,
        "payer_id": 999, # Invalid Payer ID
        "description": "Ghost Bill",
        "total_amount": "10.00",
        "split_type": "M",
        "splits": [
            {"user_owed_id": USER_IDS['alice'], "amount_owed": "10.00"}
        ]
    })
    
    print_response(res)
    if res.status_code == 400:
        print("  [PASS] Server correctly rejected the request (400 Bad Request).")
    else:
        print(f"  [FAIL] Server accepted an invalid payer! Status: {res.status_code}")
        sys.exit(1)


    # --- STEP 11: EDGE CASE (Payer not in split) ---
    print_step("Adding Bill 5 (EDGE CASE): Alice pays $40 for Bob and Charlie")
    # Alice pays, but her share is $0.
    res = session.post(f"{BASE_URL}/api/expenses/", headers=alice_header, json={
        "group": group_id,
        "payer_id": USER_IDS['alice'],
        "description": "Drinks for friends",
        "total_amount": "40.00",
        "split_type": "M",
        "splits": [
            {"user_owed_id": USER_IDS['bob'], "amount_owed": "20.00"},
            {"user_owed_id": USER_IDS['charlie'], "amount_owed": "20.00"}
        ]
    })
    
    print_response(res)
    if res.status_code != 201:
        print("Failed to create expense. Exiting.")
        sys.exit(1)


    # --- STEP 12: CHECK BALANCES (After Edge Case) ---
    print_step("Checking Balances (After Edge Case)")
    res = session.get(f"{BASE_URL}/api/groups/{group_id}/balances/", headers=alice_header)
    print_response(res)
    # Alice: Was +10, paid 40 (for others). Net = +50.00
    # Bob:   Was -10, owed 20. Net = -30.00
    # Charlie: Was 0, owed 20. Net = -20.00
    expected_balances_3 = {
        'alice': 50.00,
        'bob': -30.00,
        'charlie': -20.00
    }
    # Check that (50.00) + (-30.00) + (-20.00) == 0. It does.
    check_balances(res.json(), expected_balances_3, "Step 12")


    # --- STEP 13: FINAL SETTLEMENT (Everyone pays Alice) ---
    print_step("Adding Final Repayments (Bob pays Alice $30, Charlie pays Alice $20)")
    
    # Bob pays Alice $30
    res_bob = session.post(f"{BASE_URL}/api/expenses/", headers=bob_header, json={
        "group": group_id,
        "payer_id": USER_IDS['bob'],
        "description": "Settling up with Alice",
        "total_amount": "30.00",
        "split_type": "M",
        "splits": [{"user_owed_id": USER_IDS['alice'], "amount_owed": "30.00"}]
    })
    print(f"Bob's repayment: {res_bob.status_code}")

    # Charlie pays Alice $20
    res_charlie = session.post(f"{BASE_URL}/api/expenses/", headers=charlie_header, json={
        "group": group_id,
        "payer_id": USER_IDS['charlie'],
        "description": "Settling up with Alice",
        "total_amount": "20.00",
        "split_type": "M",
        "splits": [{"user_owed_id": USER_IDS['alice'], "amount_owed": "20.00"}]
    })
    print(f"Charlie's repayment: {res_charlie.status_code}")

    if res_bob.status_code != 201 or res_charlie.status_code != 201:
        print("  [FAIL] One or more final repayments failed.")
        sys.exit(1)


    # --- STEP 14: FINAL BALANCE CHECK (ALL ZEROS) ---
    print_step("Checking Final Balances (Should be all zero)")
    res = session.get(f"{BASE_URL}/api/groups/{group_id}/balances/", headers=alice_header)
    print_response(res)
    
    # Everyone should be at 0.00
    expected_balances_final = {
        'alice': 0.00,
        'bob': 0.00,
        'charlie': 0.00
    }
    check_balances(res.json(), expected_balances_final, "Step 14: All Settled")

    print("\n" + "="*50)
    print("   ALL LEDGER TESTS PASSED SUCCESSFULLY! ")
    print("="*50)


if __name__ == "__main__":
    # Ensure your Django server is running first!
    # `python manage.py runserver`
    try:
        requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to {BASE_URL}.")
        print("Please make sure your Django server is running.")
        print("Run: python manage.py runserver")
        sys.exit(1)
        
    run_test()
