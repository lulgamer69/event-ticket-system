# 🧪 Testing & Troubleshooting Guide

## 🧪 Testing the System

### 1. Test Registration (Free Ticket - 1 Pass)
```
- Go to: http://localhost:5000/register
- Fill in:
  - Roll Number: 001
  - Child Name: Test Child 1
  - Class: A-1
  - Parent 1: Test Parent
  - Parent 2: Test Parent 2
  - Phone: 1234567890
  - Passes: 1 (Free)
- Click Register
- Should show success message immediately (no payment needed)
- Check database: payment_status should be "FREE"
```

### 2. Test Payment Flow (Paid Ticket - 3+ Passes)
```
- Go to: http://localhost:5000/register
- Fill in:
  - Roll Number: 002
  - Child Name: Test Child 2
  - Class: B-1
  - Parent 1: Parent Name
  - Parent 2: Parent Name 2
  - Phone: 9876543210
  - Passes: 2 (₹100 required for extra pass)
- Click Register
- Should redirect to /payment page
- Verify page shows:
  ✓ Ticket number (EVT-2026-XXXXX)
  ✓ Amount: ₹100
  ✓ QR code image
  ✓ Payment Done button
- Click "Payment Done" button
- Should see success page
- Check database: payment_status should be "AWAITING_VERIFICATION"
```

### 3. Test Admin Verification
```
- Go to: http://localhost:5000/admin
- Should see pending payments list with:
  ✓ Child name
  ✓ Parent name
  ✓ Phone number
  ✓ Amount
  ✓ Ticket number
  ✓ Status badge (AWAITING_VERIFICATION)
- Click "✅ Verify & Send Ticket"
- Should show success: "✅ Ticket sent to parent WhatsApp!"
- Check database: payment_status should be "VERIFIED"
```

### 4. Test Entry Verification
```
- Go to: http://localhost:5000/verify
- Enter ticket number from registered child
- Should show:
  ✓ Child name
  ✓ Parent names
  ✓ Number of people allowed
  ✓ Success message
- Entry marked as attended
- Try scanning same ticket again
- Should show: "❌ Ticket already used"
```

---

## 🐛 Troubleshooting

### Issue: WhatsApp messages not being sent

**Cause**: Free API might be rate-limited or blocked in your region

**Solutions**:
1. Check your internet connection
2. Try sending message manually to test
3. Switch to paid WhatsApp API:
   - Twilio (Recommended)
   - WhatsApp Business API
   - WhatSender Pro

**Code to replace** (in `send_whatsapp_message` function):
```python
# Use Twilio instead:
from twilio.rest import Client

def send_whatsapp_message(phone, message):
    account_sid = "YOUR_TWILIO_SID"
    auth_token = "YOUR_TWILIO_TOKEN"
    
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_="whatsapp:+14155238886",
        body=message,
        to=f"whatsapp:+91{phone}"
    )
    return message.sid is not None
```

### Issue: QR code not displaying

**Cause**: Image path issue

**Solutions**:
1. Check if `static/images/upi_qr.png` exists
2. Verify file is a valid image
3. Check file permissions

```bash
# Verify file exists:
ls -la static/images/upi_qr.png
```

### Issue: Ticket PDF not generating

**Cause**: Missing reportlab or PIL dependencies

**Solutions**:
```bash
pip install reportlab pillow
python -c "from reportlab.lib import pagesizes; print('OK')"
python -c "from PIL import Image; print('OK')"
```

### Issue: Database errors

**Cause**: Corrupted database or permission issue

**Solutions**:
```bash
# Delete and recreate database:
rm database.db
python app.py  # Will recreate on first run
```

### Issue: Registration already exists error

**Cause**: Roll number already registered

**Solutions**:
```bash
# Check registrations:
sqlite3 database.db "SELECT child_roll, child_name FROM registrations;"

# Delete specific registration:
sqlite3 database.db "DELETE FROM registrations WHERE child_roll='001';"
```

---

## 📊 Database Queries

### View all registrations:
```bash
sqlite3 database.db "SELECT child_roll, child_name, payment_status, ticket_number FROM registrations;"
```

### View pending payments:
```bash
sqlite3 database.db "SELECT child_name, parent1_name, phone, amount_paid FROM registrations WHERE payment_status='AWAITING_VERIFICATION';"
```

### View verified payments:
```bash
sqlite3 database.db "SELECT child_name, parent1_name, phone, payment_status FROM registrations WHERE payment_status='VERIFIED';"
```

### Update payment status manually:
```bash
sqlite3 database.db "UPDATE registrations SET payment_status='VERIFIED' WHERE ticket_number='EVT-2026-123456';"
```

---

## 🚀 Deployment Checklist

- [ ] Test all registration flows
- [ ] Test payment confirmation
- [ ] Test admin panel
- [ ] Test entry verification
- [ ] Verify WhatsApp integration works
- [ ] Create backup of database
- [ ] Set event closing date in code
- [ ] Update QR code image with actual UPI code
- [ ] Test with real phone numbers
- [ ] Document owner's WhatsApp number
- [ ] Train owner on admin panel usage
- [ ] Prepare entry verification setup

---

## 📞 Support

For issues, check:
1. Flask error logs in terminal
2. Browser console (F12) for frontend errors
3. Database integrity with SQLite commands
4. Network connectivity for WhatsApp API

