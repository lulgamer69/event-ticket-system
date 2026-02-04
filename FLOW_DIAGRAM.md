# 📊 Payment Flow Diagram

```
PARENT SIDE:
═══════════

1. Parent registers child
   ↓
   /register (POST)
   ↓
2. System creates:
   - Ticket number (EVT-2026-XXXXX)
   - PDF ticket with QR code
   - Database entry (payment_status = PENDING)
   ↓
3. Redirected to payment page
   ↓
   /payment (GET with: ticket, phone, amount)
   ↓
4. Parent sees:
   - QR Code (owner's UPI)
   - Amount: ₹100
   - Clear instructions
   ↓
5. Parent scans QR → pays via UPI
   ↓
6. Parent clicks "✅ Payment Done"
   ↓
   /payment-confirm (POST)
   ↓
7. System updates:
   - payment_status = AWAITING_VERIFICATION
   - Sends notification to owner
   ↓
8. Parent sees success message:
   "Payment received. Waiting for verification..."
   ↓
9. (WAIT) Owner verifies payment...
   ↓
10. Parent receives WhatsApp with confirmed ticket
    + Download link
    + Instructions for event day


OWNER SIDE:
═══════════

(Step 6-7) Receives WhatsApp notification:
            🔔 *New Payment Notification*
            Ticket: EVT-2026-XXXXX
            Child: [Name]
            Parent: [Name]
            Phone: [Number]
            Amount: ₹100
   ↓
(Step 9) Opens /admin dashboard
         - Sees pending payments list
         - Shows: Child name, parent, ticket, phone
   ↓
(Step 10) Clicks "✅ Verify & Send Ticket"
          ↓
          /admin/verify-payment (POST JSON)
          ↓
          System updates:
          - payment_status = VERIFIED
          - Downloads ticket PDF from tickets/EVT-2026-XXXXX.pdf
          - Sends WhatsApp to parent:
            ✅ *Payment Verified!*
            Ticket: EVT-2026-XXXXX
            Child: [Name]
            [Download instructions + event details]
   ↓
Parent downloads ticket PDF
Parent shows at event entrance


ENTRY DAY:
═════════

Parent arrives at event
↓
Shows ticket QR code to verification person
↓
Person scans QR → system looks up ticket
↓
Ticket marked as "ATTENDED" 
↓
Entry granted for specified number of people (usually 3)


DATABASE STATUS FLOW:
════════════════════

PENDING (at registration, amount > 0)
   ↓
AWAITING_VERIFICATION (after parent clicks Payment Done)
   ↓
VERIFIED (after owner clicks Verify & Send Ticket)
   ↓
[Ticket used at event entrance]

For FREE registrations (amount = 0):
PENDING → [directly granted ticket at registration]

```

## 🔐 Security Notes

1. **Ticket Numbers**: Random 6-digit codes (EVT-2026-XXXXXX)
2. **One-Time Use**: Ticket QR is scanned once at entry
3. **Owner Verification**: Manual payment check prevents fraud
4. **WhatsApp Validation**: Owner confirms receipt before sending ticket
5. **Database Lock**: Prevents duplicate registrations by roll number

## ⏱️ Timeline

1. Parent registers → Instant ticket PDF generated (not sent yet)
2. Parent pays → Notification sent to owner immediately
3. Owner verifies → WhatsApp sent to parent within minutes
4. Parent downloads → Can use anytime before event date
5. Event day → Scan QR code for entry

