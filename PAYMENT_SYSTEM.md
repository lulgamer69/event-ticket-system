# 🎉 Event Registration - QR Code Payment System

## 🔄 New Payment Flow

### For Parents:
1. **Register**: Parent fills in child and parent details on `/register`
2. **Pay ₹100**: Redirected to `/payment` page with:
   - QR code for payment (UPI)
   - Clear payment instructions
3. **Click "Payment Done"**: After scanning and paying via QR code
   - Parent clicks the "✅ Payment Done" button
   - Payment status is recorded as `AWAITING_VERIFICATION`
   - Owner receives WhatsApp notification
4. **Receive Ticket**: 
   - Owner verifies payment on admin panel
   - Owner clicks "✅ Verify & Send Ticket"
   - Ticket is sent to parent's WhatsApp number
   - Parent can download and use the PDF ticket at the event

### For Preschool Owner:
1. **Monitor Payments**: Visit `/admin` to see pending payments
2. **Verify Payment**: 
   - Check parent's bank account for payment confirmation
   - Click "✅ Verify & Send Ticket" button
3. **Send Ticket**: 
   - WhatsApp message automatically sent to parent
   - Includes ticket number and event details
4. **Parent Downloads**: Parent uses ticket at event entrance

---

## 📋 Database Updates

**Payment Status Values:**
- `FREE`: No payment required (1 pass)
- `PENDING`: Initial state when registration created
- `AWAITING_VERIFICATION`: Parent clicked "Payment Done", awaiting owner verification
- `VERIFIED`: Payment verified, ticket sent to parent

---

## 🔗 URL Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/register` | GET/POST | Registration form |
| `/payment` | GET | Display QR code payment page |
| `/payment-confirm` | POST | Confirm parent's payment claim |
| `/admin` | GET | Admin panel to verify payments |
| `/admin/verify-payment` | POST | Owner verifies and sends ticket |
| `/verify` | GET/POST | Entry verification at event |

---

## 🚀 Setup Instructions

### 1. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 2. Run the App:
```bash
python app.py
```

### 3. Access:
- **Parent Registration**: `http://localhost:5000/register`
- **Admin Panel**: `http://localhost:5000/admin`

---

## 📱 WhatsApp Integration

Uses **CallMeBot** free API to send WhatsApp messages.

### Messages Sent:

**To Owner** (8591367049):
```
🔔 *New Payment Notification* 🔔

Ticket: EVT-2026-123456
Child: [Child Name]
Parent: [Parent Name]
Phone: [Parent Phone]
Amount: ₹100

Parent claims to have paid. Please verify payment and send the ticket.
```

**To Parent** (after verification):
```
✅ *Payment Verified!*

Ticket Number: EVT-2026-123456
Child: [Child Name]

Your annual day entry pass is confirmed!

📎 Download your ticket from the registration link and save it.
📱 Show this ticket at the entrance on event day.
👥 Allowed people: 3

See you at the Annual Day! 🎉
```

---

## 💡 Key Features

✅ **Simple Flow**: No complex payment gateway integration  
✅ **Manual Verification**: Owner controls when ticket is released  
✅ **WhatsApp Notifications**: Automatic messages to owner and parent  
✅ **QR Code Display**: Parent scans owner's UPI QR code  
✅ **Admin Panel**: Easy interface to manage payments  
✅ **PDF Tickets**: Downloadable tickets with QR codes  

---

## ⚙️ Configuration

Update owner's WhatsApp number in `app.py`:
```python
OWNER_WHATSAPP = "8591367049"
```

---

## 📝 Notes

- One pass (1 ticket) is FREE
- Additional passes cost ₹100 each
- Ticket numbers are auto-generated
- QR code on ticket is for entry verification
- Free WhatsApp API has rate limits; consider upgrading for production

