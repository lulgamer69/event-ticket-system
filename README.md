# 🚀 Quick Start Guide

## In 2 Minutes - Get Running

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the App
```bash
python app.py
```

### Step 3: Open in Browser
- **Registration**: http://localhost:5000/register
- **Admin Panel**: http://localhost:5000/admin
- **Entry Check**: http://localhost:5000/verify

---

## 🧪 Quick Test

### Test Case 1: Free Ticket (1 Pass)
```
1. Go to /register
2. Fill form with any details
3. Select "1 Pass"
4. Submit → Should see "Registration Successful ✅"
```

### Test Case 2: Paid Ticket (2+ Passes)
```
1. Go to /register
2. Fill form with any details
3. Select "2 Passes" or more
4. Submit → Redirects to /payment
5. See QR code + "Payment Done" button
6. Click button → See "Payment Received ✅"
7. Go to /admin → See pending payment
8. Click "Verify & Send Ticket" → "Ticket sent ✅"
```

---

## 🎯 The Flow Explained

```
Parent Registration
    ↓
Pay via QR Code (₹100 per extra pass)
    ↓
Click "Payment Done"
    ↓
Owner gets WhatsApp notification
    ↓
Owner opens /admin & clicks "Verify"
    ↓
Parent gets WhatsApp with ticket
    ↓
Parent downloads & brings to event
```

---

## 📱 What Parent Sees

1. **Registration Page**: Simple form for child & parent details
2. **Payment Page**: QR code to scan + instructions
3. **Success Message**: "Waiting for verification..."
4. **WhatsApp**: Ticket message with download link

---

## 👤 What Owner Does

1. **Receives WhatsApp**: "New Payment Notification"
2. **Checks Bank Account**: Verifies payment received
3. **Opens /admin**: Logs in to dashboard
4. **Clicks Button**: "Verify & Send Ticket"
5. **Done**: Automatic WhatsApp sent to parent

---

## 🔧 Important Settings

**Owner's WhatsApp Number** (in `app.py`):
```python
OWNER_WHATSAPP = "8591367049"
```

**Event Closing Date** (in `app.py`):
```python
if date.today() > date(2026, 2, 10):  # Change 2026, 2, 10
    return render_template("closed.html")
```

**QR Code Image** (in `static/images/`):
```
upi_qr.png  ← Replace with actual UPI QR code
```

---

## 🆘 If Something Goes Wrong

### App won't start?
```bash
python app.py  # Check error messages
```

### Database issues?
```bash
rm database.db  # Delete and recreate
python app.py   # Restart
```

### WhatsApp not working?
- Check internet connection
- Free API might be rate-limited
- Check terminal for error messages

---

## 📚 Full Documentation

- [PAYMENT_SYSTEM.md](PAYMENT_SYSTEM.md) - Complete system details
- [FLOW_DIAGRAM.md](FLOW_DIAGRAM.md) - Visual diagrams
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Detailed testing & troubleshooting
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - All changes made

---

## ✅ What's Ready

✅ Registration system  
✅ QR code payment page  
✅ Admin verification dashboard  
✅ WhatsApp notifications  
✅ PDF ticket generation  
✅ Entry verification system  
✅ Database setup  
✅ All documentation  

---

## 🎉 You're All Set!

The app is ready to use. Just:
1. Replace `upi_qr.png` with your actual QR code
2. Run `python app.py`
3. Share `/register` link with parents
4. Monitor `/admin` during payment period
5. Verify payments and send tickets

Happy Annual Day! 🎊

