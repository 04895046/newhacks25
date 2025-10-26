#!/usr/bin/env python
"""
Test script for mobile integration changes:
1. Login returns user info
2. Group details include member IDs
3. User search endpoint works
"""
import requests
import json
import sys

BASE_URL = 'http://127.0.0.1:8000'

def print_step(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_response(res):
    try:
        print(f"STATUS: {res.status_code}")
        print("RESPONSE:")
        print(json.dumps(res.json(), indent=2))
    except:
        print(res.text)

def main():
    session = requests.Session()
    
    # Step 1: Register a test user
    print_step("STEP 1: Register Test User 'mobile_test'")
    res = session.post(f"{BASE_URL}/api/register/", json={
        "username": "mobile_test",
        "password": "password123"
    })
    print_response(res)
    
    if res.status_code not in [201, 400]:
        print("❌ Registration failed!")
        return False
    
    # Step 2: Test Custom Login (should return user info)
    print_step("STEP 2: Login with Custom View (Check for user info)")
    res = session.post(f"{BASE_URL}/api/login/", json={
        "username": "mobile_test",
        "password": "password123"
    })
    print_response(res)
    
    if res.status_code != 200:
        print("❌ Login failed!")
        return False
    
    login_data = res.json()
    if 'token' not in login_data or 'user' not in login_data:
        print("❌ Login response missing token or user info!")
        return False
    
    if 'id' not in login_data['user'] or 'username' not in login_data['user']:
        print("❌ User info missing id or username!")
        return False
    
    print("✅ Login returns token AND user info (id + username)")
    
    token = login_data['token']
    user_id = login_data['user']['id']
    headers = {'Authorization': f'Token {token}'}
    
    # Step 3: Register more users for search test
    print_step("STEP 3: Register Additional Users for Search")
    for username in ['alice', 'alice_smith', 'bob']:
        res = session.post(f"{BASE_URL}/api/register/", json={
            "username": username,
            "password": "password123"
        })
        print(f"Registered {username}: {res.status_code}")
    
    # Step 4: Test User Search
    print_step("STEP 4: Test User Search Endpoint")
    res = session.get(f"{BASE_URL}/api/users/search/?q=alice", headers=headers)
    print_response(res)
    
    if res.status_code != 200:
        print("❌ User search failed!")
        return False
    
    search_results = res.json()
    if not isinstance(search_results, list):
        print("❌ Search results not a list!")
        return False
    
    # Check if results have id and username
    if search_results:
        first_result = search_results[0]
        if 'id' not in first_result or 'username' not in first_result:
            print("❌ Search results missing id or username!")
            return False
        print(f"✅ Found {len(search_results)} user(s) matching 'alice'")
    
    # Step 5: Create a group with members
    print_step("STEP 5: Create Group with Members (by ID)")
    
    # Get alice's ID from search results
    alice_id = None
    for result in search_results:
        if result['username'] == 'alice':
            alice_id = result['id']
            break
    
    if alice_id:
        res = session.post(f"{BASE_URL}/api/groups/", headers=headers, json={
            "name": "Mobile Test Group",
            "members": [alice_id]  # Add alice by ID
        })
        print_response(res)
        
        if res.status_code != 201:
            print("❌ Group creation failed!")
            return False
        
        group_data = res.json()
        group_id = group_data['id']
        
        # Check if members field has both id and username
        if 'members' not in group_data:
            print("❌ Group response missing members field!")
            return False
        
        members = group_data['members']
        if not isinstance(members, list) or len(members) == 0:
            print("❌ Members field is not a list or is empty!")
            return False
        
        first_member = members[0]
        if 'id' not in first_member or 'username' not in first_member:
            print("❌ Member objects missing id or username!")
            return False
        
        print("✅ Group created with members showing ID and username")
        
        # Step 6: Get group details
        print_step("STEP 6: Get Group Details (Check member format)")
        res = session.get(f"{BASE_URL}/api/groups/{group_id}/", headers=headers)
        print_response(res)
        
        if res.status_code != 200:
            print("❌ Get group details failed!")
            return False
        
        detail_data = res.json()
        if 'members' not in detail_data:
            print("❌ Group detail missing members field!")
            return False
        
        members = detail_data['members']
        if members and isinstance(members, list):
            first_member = members[0]
            if 'id' in first_member and 'username' in first_member:
                print("✅ Group details include member IDs and usernames")
            else:
                print("❌ Group details member objects missing id or username!")
                return False
    
    # All tests passed!
    print("\n" + "="*60)
    print(" ✅ ALL MOBILE INTEGRATION TESTS PASSED! ")
    print("="*60)
    print("\nSummary of Changes:")
    print("1. ✅ Login now returns: {'token': '...', 'user': {'id': X, 'username': '...'}}")
    print("2. ✅ Groups now show members as: [{'id': X, 'username': '...'}, ...]")
    print("3. ✅ User search endpoint works: GET /api/users/search/?q=...")
    return True

if __name__ == "__main__":
    try:
        requests.get(BASE_URL)
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to {BASE_URL}.")
        print("Please make sure your Django server is running.")
        print("Run: python manage.py runserver")
        sys.exit(1)
    
    success = main()
    sys.exit(0 if success else 1)
