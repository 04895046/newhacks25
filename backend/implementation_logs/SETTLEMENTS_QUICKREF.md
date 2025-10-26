# Quick Reference: Settlements Endpoint

## Question Answered
**"How much does A owe B in a group?"**

## API Endpoint
```
GET /api/groups/<id>/settlements/
```

## Response Example
```json
[
  {"from": "bob", "to": "alice", "amount": "30.00"},
  {"from": "charlie", "to": "alice", "amount": "70.00"},
  {"from": "david", "to": "alice", "amount": "150.00"}
]
```

## What It Does
- Calculates optimal payment plan
- Minimizes number of transactions
- Shows exactly who pays whom

## Difference from Balances

### `/balances/` - Shows net position
```json
[
  {"username": "alice", "balance": "+250.00"},
  {"username": "bob", "balance": "-30.00"}
]
```
**Tells you:** Alice is owed $250, Bob owes $30

### `/settlements/` - Shows payment instructions
```json
[
  {"from": "bob", "to": "alice", "amount": "30.00"}
]
```
**Tells you:** Bob should pay Alice $30

## Mobile Usage

### Display Settlements
```kotlin
api.getGroupSettlements(groupId).forEach { settlement ->
    showPaymentCard(
        message = "${settlement.from} pays ${settlement.to}",
        amount = settlement.amount
    )
}
```

### Result in UI
```
┌─────────────────────────────┐
│ Bob pays Alice              │
│ $30.00                      │
│ [Mark as Paid]              │
└─────────────────────────────┘
```

## Test Results
✅ All tests passing  
✅ Calculations verified  
✅ Algorithm optimized  

## Files Modified
- `api/views.py` - Added `settlements()` action
- `COMPLETE_API_DOCUMENTATION.md` - Added endpoint docs
- `test_settlements.py` - Comprehensive tests

## Status
🚀 **Production Ready** - October 26, 2025
