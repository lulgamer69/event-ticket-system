# 🗺️ Complete Route Map

## User Routes (Public)

### 1. `/register` - Registration Page
```
METHOD: GET / POST
PUBLIC: Yes

GET: Shows registration form
POST: Creates new registration, generates ticket

Form Fields:
- Child Roll Number (UNIQUE)
- Child Name
- Class Section
- Parent 1 Name
- Parent 2 Name
- Phone Number
- Number of Passes (1, 2, 3, 4...)

Response:
✓ If Free (1 pass): Shows success, no payment
✓ If Paid (2+ passes): Redirects to /payment
✗ If Roll exists: Shows error
```

### 2. `/payment` - Payment Page
```
METHOD: GET
PUBLIC: Yes
REQUIRES: ticket, phone, amount (query params)

Shows:
- Ticket number
- Amount to pay (₹100 per extra pass)
- QR Code image
- Payment instructions
- "Payment Done" button

Styling:
- Step-by-step instructions
- QR code display
- Success message about WhatsApp verification
```

### 3. `/payment-confirm` - Payment Confirmation
```
METHOD: POST
PUBLIC: Yes
REQUIRES: ticket_number, phone (form data)

Actions:
1. Records parent's payment claim
2. Updates DB: payment_status = "AWAITING_VERIFICATION"
3. Sends WhatsApp notification to owner
4. Returns success message to parent

Parent sees:
✅ Payment Received
⏳ Waiting for owner verification
📱 WhatsApp will be sent to: +91 {phone}
```

### 4. `/verify` - Entry Verification
```
METHOD: GET / POST
PUBLIC: Yes

GET: Shows verification form
POST: Validates ticket QR code

Form Input:
- Ticket Number

Response:
✓ Valid & Unused: Shows entry allowed, marks as attended
✗ Already Used: Shows "Ticket already used"
✗ Invalid: Shows "Invalid ticket"
```

### 5. `/tickets/<filename>` - Download Ticket
```
METHOD: GET
PUBLIC: Yes
REQUIRES: filename (e.g., "EVT-2026-123456.pdf")

Returns: PDF file of ticket for download
```

---

## Admin Routes (Protected in Production)

### 6. `/admin` - Admin Dashboard
```
METHOD: GET
PUBLIC: Currently (add auth in production!)

Shows:
- List of all payments
- Status filters: All / Pending / Verified
- For each payment:
  - Child name & roll
  - Parent name & phone
  - Amount
  - Ticket number
  - Current status badge
  - Action button: "Verify & Send Ticket"

Styling:
- Filter buttons (All/Pending/Verified)
- Color-coded status badges
- Green "Verify" button for pending
```

### 7. `/admin/verify-payment` - Verify & Send
```
METHOD: POST (JSON)
PUBLIC: Currently (add auth in production!)
REQUIRES: {
  "payment_id": "1",
  "phone": "9876543210",
  "ticket": "EVT-2026-123456"
}

Actions:
1. Looks up registration by ticket
2. Updates DB: payment_status = "VERIFIED"
3. Sends WhatsApp to parent with ticket details
4. Returns JSON: {"success": true, "message": "..."}

Owner sees:
✅ Ticket sent to parent WhatsApp!
```

---

## Internal Routes (Not for Direct Access)

### 8. `/` - Home
```
METHOD: GET
Returns: "App is live ✅"
Purpose: Health check
```

---

## Data Flow Map

```
REQUEST FLOW:

GET /register
  ↓
render_template("register.html")
  ↓
User submits form
  ↓
POST /register
  ↓
insert into database
  ↓
generate_ticket_pdf()
  ↓
if amount > 0:
  redirect /payment?ticket=X&phone=Y&amount=Z
else:
  return success page


GET /payment?ticket=...&phone=...&amount=...
  ↓
render_template("payment.html", ...)
  ↓
User scans QR & pays
  ↓
User clicks "Payment Done"
  ↓
POST /payment-confirm
  ↓
update payment_status = "AWAITING_VERIFICATION"
  ↓
send_whatsapp_message(OWNER_WHATSAPP, message)
  ↓
return success HTML page


Owner receives WhatsApp:
"🔔 New Payment Notification"
  ↓
Owner opens GET /admin
  ↓
render_template("admin.html", payments=...)
  ↓
Owner clicks "Verify & Send Ticket"
  ↓
POST /admin/verify-payment
  ↓
update payment_status = "VERIFIED"
  ↓
send_whatsapp_message(phone, message)
  ↓
return JSON {"success": true}


Parent receives WhatsApp:
"✅ Payment Verified!"
  ↓
Parent clicks link
  ↓
GET /tickets/EVT-2026-XXXXX.pdf
  ↓
download_ticket()
  ↓
send_from_directory("tickets", filename)
  ↓
.pdf file downloaded


At Event Day:
  ↓
GET /verify
  ↓
render_template("verify.html")
  ↓
Staff enters ticket number
  ↓
POST /verify
  ↓
get_record(ticket)
  ↓
update attended = 1
  ↓
return "Entry Allowed ✅"
```

---

## URL Quick Reference

| Purpose | URL | Method | Who |
|---------|-----|--------|-----|
| Register | `/register` | GET/POST | Parent |
| Pay | `/payment` | GET | Parent |
| Confirm Payment | `/payment-confirm` | POST | Parent |
| Download Ticket | `/tickets/EVT-2026-XXXXX.pdf` | GET | Parent |
| Check Entry | `/verify` | GET/POST | Staff |
| **Admin Panel** | **/admin** | GET | Owner |
| **Verify Payment** | **/admin/verify-payment** | POST | Owner |

---

## Database Status Transitions

```
Registration Created:
payment_status = "PENDING" or "FREE"

After Payment Click:
payment_status = "PENDING" → "AWAITING_VERIFICATION"

After Owner Verification:
payment_status = "AWAITING_VERIFICATION" → "VERIFIED"

At Event Entry:
attended = 0 → 1 (one-time use)
```

---

## Key Parameters

### Query Parameters (URL)
```
/payment?ticket=EVT-2026-123456&phone=9876543210&amount=100
```

### Form Data (POST)
```
ticket_number: EVT-2026-123456
phone: 9876543210
```

### JSON Data (Admin Verify)
```
{
  "payment_id": "1",
  "phone": "9876543210",
  "ticket": "EVT-2026-123456"
}
```

---

## Error Handling

```
Registration Errors:
❌ Roll number already registered
❌ Invalid form data

Payment Errors:
❌ Invalid ticket number
❌ Ticket not found

Entry Errors:
❌ Invalid ticket
❌ Ticket already used
```

---

## Template Files Used

```
/register
  → templates/register.html

/payment
  → templates/payment.html

/verify
  → templates/verify.html

/admin
  → templates/admin.html

closed.html (when registration closed)
  → templates/closed.html
```

---

**All routes are operational and ready for testing!**

