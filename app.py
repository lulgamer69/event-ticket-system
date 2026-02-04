from flask import Flask, render_template, request, send_from_directory, jsonify, redirect, url_for
import sqlite3, os, random, string
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import smtplib
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
import qrcode

app = Flask(__name__)
app.secret_key = "secret"

# Setup ticket storage path - persistent on Render, local in development
TICKET_FOLDER = "/var/data/tickets" if os.path.exists("/var/data") else "tickets"
os.makedirs(TICKET_FOLDER, exist_ok=True)

OWNER_WHATSAPP = "8591367049"
OWNER_MESSAGE_API = "https://api.callmebot.com/whatsapp.php"  # Free WhatsApp API

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            child_roll TEXT UNIQUE,
            child_name TEXT,
            class_section TEXT,

            parent1_name TEXT,
            parent2_name TEXT,
            phone TEXT,

            pass_count INTEGER,
            total_people INTEGER,
            amount_paid INTEGER,
            payment_status TEXT,

            ticket_number TEXT UNIQUE,
            payment_screenshot TEXT,
            attended INTEGER DEFAULT 0,

            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= WHATSAPP HELPER =================
def send_whatsapp_message(phone, message, pdf_path=None):
    """Queue WhatsApp message for manual sending"""
    try:
        if not phone.startswith("+"):
            phone = "+91" + phone
        
        # Log to file for display in admin panel
        os.makedirs("logs", exist_ok=True)
        with open("logs/whatsapp_queue.txt", "a", encoding="utf-8") as f:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n[{timestamp}]\nTO: {phone}\n{message}\n{'='*60}\n")
        
        print(f"✅ Message queued for {phone}")
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

# ================= EMAIL HELPER =================
def send_email_with_ticket(email, child_name, ticket_number, pdf_path):
    """Send ticket PDF via email"""
    try:
        # Email configuration
        sender_email = os.environ.get("EMAIL_SENDER", "your_email@gmail.com")
        sender_password = os.environ.get("EMAIL_PASSWORD", "your_app_password")
        
        if not sender_email or sender_password == "your_app_password":
            print("❌ Email not configured")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = f'Annual Day Entry Pass - {ticket_number}'
        
        # Email body
        body = f"""Hello {child_name},

Your Annual Day entry pass has been verified and is ready!

Ticket Number: {ticket_number}

Please find your ticket PDF attached. Show this at the entrance on event day.

Important:
- This ticket is for ONE-TIME entry only
- Keep it safe and don't share it
- Arrive a few minutes early

See you at the Annual Day! 🎉

Best regards,
Dumblebdor Kindergarten"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        if os.path.exists(pdf_path):
            with open(pdf_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename= {ticket_number}.pdf')
                msg.attach(part)
        
        # Send email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Ticket emailed to {email}")
        return True
        
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False

# ================= HELPERS =================
def generate_ticket():
    return "EVT-2026-" + "".join(random.choices(string.digits, k=6))

def generate_qr(ticket):
    os.makedirs("qr", exist_ok=True)
    path = f"qr/{ticket}.png"
    qrcode.make(ticket).save(path)
    return path

def generate_ticket_pdf(ticket, child, p1, p2, total_people, roll_no="", class_section="", guest3=""):
    os.makedirs(TICKET_FOLDER, exist_ok=True)
    qr_path = generate_qr(ticket)
    pdf_path = f"{TICKET_FOLDER}/{ticket}.pdf"

    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4

    # TOP HEADER IMAGE (full width)
    header_image = "static/images/header.png"
    if os.path.exists(header_image):
        c.drawImage(header_image, 0, h - 200, width=w, height=200)

    # Content starts below header
    # LEFT SIDE - DETAILS
    left_x = 50
    y = h - 280
    line_space = 26

    c.setFont("Helvetica", 14)
    
    c.drawString(left_x, y, f"Roll no : {roll_no}")
    y -= line_space
    c.drawString(left_x, y, f"Student Name : {child}")
    y -= line_space
    c.drawString(left_x, y, f"Class: {class_section}")
    y -= line_space
    c.drawString(left_x, y, f"Guest 1: {p1}")
    y -= line_space
    c.drawString(left_x, y, f"Guest 2: {p2}")
    y -= line_space
    c.drawString(left_x, y, f"Guest 3: {guest3}")
    y -= line_space
    c.drawString(left_x, y, f"No. of Extra pass : {max(0, total_people - 3)}")

    # Blank space, then event details
    y -= 35
    c.setFont("Helvetica", 12)
    c.drawString(left_x, y, f"Date: 9th February, 2026")
    y -= line_space
    c.drawString(left_x, y, f"Time: 6:00pm.")
    y -= line_space
    c.drawString(left_x, y, f"Venue:")
    y -= line_space
    c.drawString(left_x, y, f"Lata Mangeshkar Natyagruha,")
    y -= 20
    c.drawString(left_x, y, f"Mahajan Wadi, Mira Road East,")
    y -= 20
    c.drawString(left_x, y, f"Mira Bhayandar, Maharashtra")
    y -= 20
    c.drawString(left_x, y, f"401107.")

    # RIGHT SIDE - QR CODE (positioned lower, beside address)
    qr_x = w - 220
    qr_y = h - 480

    # QR Code
    c.drawImage(qr_path, qr_x, qr_y, width=150, height=150)

    # TICKET NUMBER below QR
    c.setFont("Helvetica", 11)
    c.drawCentredString(qr_x + 75, qr_y - 25, "TICKET NUMBER")
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(qr_x + 75, qr_y - 45, ticket)

    # BOTTOM - WARNING MESSAGE
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(w / 2, 35, "QR valid for one-time entry only.")

    c.showPage()
    c.save()
    return pdf_path

# ================= ROUTES =================
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if date.today() > date(2026, 2, 10):
        return render_template("closed.html")

    if request.method == "POST":
        f = request.form

        conn = get_db()
        exists = conn.execute(
            "SELECT 1 FROM registrations WHERE child_roll=?",
            (f["child_roll"],)
        ).fetchone()
        conn.close()

        if exists:
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Registration Error - Dumblebdor Kindergarten</title>
                <style>
                    * {
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }
                    
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        padding: 20px;
                    }
                    
                    .container {
                        background: white;
                        border-radius: 20px;
                        padding: 60px 40px;
                        text-align: center;
                        max-width: 500px;
                        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                        animation: slideUp 0.6s ease-out;
                    }
                    
                    @keyframes slideUp {
                        from {
                            opacity: 0;
                            transform: translateY(40px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }
                    
                    .icon {
                        font-size: 80px;
                        margin-bottom: 20px;
                        animation: shake 0.6s ease-in-out;
                        display: inline-block;
                    }
                    
                    @keyframes shake {
                        0%, 100% { transform: translateX(0); }
                        25% { transform: translateX(-10px); }
                        75% { transform: translateX(10px); }
                    }
                    
                    h1 {
                        color: #333;
                        font-size: 32px;
                        margin-bottom: 15px;
                        font-weight: 700;
                    }
                    
                    .error-msg {
                        color: #e74c3c;
                        font-size: 18px;
                        margin-bottom: 30px;
                        line-height: 1.6;
                    }
                    
                    .roll-number {
                        background: #f8f9fa;
                        padding: 15px;
                        border-radius: 10px;
                        margin-bottom: 30px;
                        color: #555;
                        font-weight: 600;
                        border-left: 4px solid #e74c3c;
                    }
                    
                    .action-buttons {
                        display: flex;
                        gap: 12px;
                        justify-content: center;
                        flex-wrap: wrap;
                    }
                    
                    .btn {
                        padding: 12px 30px;
                        border: none;
                        border-radius: 10px;
                        font-size: 16px;
                        font-weight: 600;
                        cursor: pointer;
                        transition: all 0.3s ease;
                        text-decoration: none;
                        display: inline-block;
                    }
                    
                    .btn-primary {
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    
                    .btn-primary:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
                    }
                    
                    .btn-secondary {
                        background: #ecf0f1;
                        color: #333;
                    }
                    
                    .btn-secondary:hover {
                        background: #bdc3c7;
                        transform: translateY(-2px);
                    }
                    
                    .info-text {
                        color: #7f8c8d;
                        font-size: 14px;
                        margin-top: 25px;
                        padding-top: 20px;
                        border-top: 1px solid #ecf0f1;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">⚠️</div>
                    <h1>Registration Already Exists</h1>
                    <p class="error-msg">This roll number has already been registered for the event.</p>
                    <div class="roll-number">
                        Roll Number: <strong>Already Registered</strong>
                    </div>
                    <p style="color: #555; margin-bottom: 25px;">Please contact the school office if you believe this is an error.</p>
                    
                    <div class="action-buttons">
                        <a href="/" class="btn btn-primary">← Back to Home</a>
                        <a href="/register" class="btn btn-secondary">Try Another Roll</a>
                    </div>
                    
                    <p class="info-text">📞 Contact: 8591367049</p>
                </div>
            </body>
            </html>
            """

        pass_count = int(f["pass_count"])
        total_people = 3 + (pass_count - 1)
        amount = max(0, pass_count - 1) * 100

        ticket = generate_ticket()

        conn = get_db()
        conn.execute("""
            INSERT INTO registrations
            (child_roll, child_name, class_section,
             parent1_name, parent2_name, phone,
             pass_count, total_people,
             amount_paid, payment_status,
             ticket_number, attended, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, DATE('now'))
        """, (
            f["child_roll"],
            f["child_name"],
            f["class_section"],
            f["parent1_name"],
            f["parent2_name"],
            f["phone"],
            pass_count,
            total_people,
            amount,
            "PENDING" if amount > 0 else "FREE",
            ticket
        ))
        conn.commit()
        conn.close()

        generate_ticket_pdf(
            ticket,
            f["child_name"],
            f["parent1_name"],
            f["parent2_name"],
            total_people,
            f["child_roll"],
            f["class_section"],
            f.get("guest_name_3", "")
        )

        if amount > 0:
            return redirect(url_for('payment', ticket=ticket, phone=f["phone"], amount=amount))

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Registration Successful - Dumblebdor Kindergarten</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                
                .container {{
                    background: white;
                    border-radius: 20px;
                    padding: 60px 40px;
                    text-align: center;
                    max-width: 600px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
                    animation: slideUp 0.6s ease-out;
                }}
                
                @keyframes slideUp {{
                    from {{
                        opacity: 0;
                        transform: translateY(40px);
                    }}
                    to {{
                        opacity: 1;
                        transform: translateY(0);
                    }}
                }}
                
                .icon {{
                    font-size: 100px;
                    margin-bottom: 20px;
                    display: inline-block;
                    animation: bounce 1s ease-in-out infinite;
                }}
                
                @keyframes bounce {{
                    0%, 100% {{ transform: translateY(0); }}
                    50% {{ transform: translateY(-15px); }}
                }}
                
                h1 {{
                    color: #27ae60;
                    font-size: 36px;
                    margin-bottom: 15px;
                    font-weight: 700;
                }}
                
                .subtitle {{
                    color: #555;
                    font-size: 18px;
                    margin-bottom: 10px;
                    line-height: 1.6;
                }}
                
                .ticket-info {{
                    background: linear-gradient(135deg, #f0f9f6 0%, #e8f8f5 100%);
                    padding: 25px;
                    border-radius: 12px;
                    margin: 30px 0;
                    border-left: 5px solid #27ae60;
                }}
                
                .ticket-label {{
                    color: #7f8c8d;
                    font-size: 13px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 8px;
                }}
                
                .ticket-number {{
                    color: #27ae60;
                    font-size: 32px;
                    font-weight: 700;
                    font-family: 'Courier New', monospace;
                }}
                
                .details {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 12px;
                    margin: 25px 0;
                    text-align: left;
                }}
                
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    color: #555;
                    border-bottom: 1px solid #ecf0f1;
                }}
                
                .detail-row:last-child {{
                    border-bottom: none;
                }}
                
                .detail-label {{
                    font-weight: 600;
                    color: #333;
                }}
                
                .detail-value {{
                    color: #27ae60;
                }}
                
                .action-buttons {{
                    display: flex;
                    gap: 15px;
                    justify-content: center;
                    flex-wrap: wrap;
                    margin: 35px 0;
                }}
                
                .btn {{
                    padding: 14px 35px;
                    border: none;
                    border-radius: 10px;
                    font-size: 16px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    text-decoration: none;
                    display: inline-block;
                }}
                
                .btn-primary {{
                    background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
                    color: white;
                }}
                
                .btn-primary:hover {{
                    transform: translateY(-3px);
                    box-shadow: 0 15px 30px rgba(46, 204, 113, 0.3);
                }}
                
                .btn-secondary {{
                    background: #ecf0f1;
                    color: #333;
                }}
                
                .btn-secondary:hover {{
                    background: #bdc3c7;
                    transform: translateY(-3px);
                }}
                
                .info-box {{
                    background: #fff3cd;
                    border-left: 4px solid #ffc107;
                    padding: 15px;
                    border-radius: 8px;
                    margin-top: 25px;
                    color: #856404;
                    font-size: 14px;
                }}
                
                .success-badge {{
                    display: inline-block;
                    background: #27ae60;
                    color: white;
                    padding: 8px 16px;
                    border-radius: 25px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-bottom: 20px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-badge">✓ FREE REGISTRATION</div>
                <div class="icon">🎉</div>
                <h1>Registration Successful!</h1>
                <p class="subtitle">Your registration has been confirmed for the Annual Day event.</p>
                
                <div class="ticket-info">
                    <div class="ticket-label">Your Ticket Number</div>
                    <div class="ticket-number">{ticket}</div>
                </div>
                
                <div class="details">
                    <div class="detail-row">
                        <span class="detail-label">Student Name:</span>
                        <span class="detail-value">{f["child_name"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Roll Number:</span>
                        <span class="detail-value">{f["child_roll"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Class:</span>
                        <span class="detail-value">{f["class_section"]}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Total People:</span>
                        <span class="detail-value">{total_people}</span>
                    </div>
                </div>
                
                <div class="action-buttons">
                    <a href="/tickets/{ticket}.pdf" class="btn btn-primary" download="Ticket_{ticket}.pdf">⬇️ Download Ticket (PDF)</a>
                    <a href="/" class="btn btn-secondary">← Back to Home</a>
                </div>
            </div>
        </body>
        </html>
        """

    return render_template("register.html")

# ================= PAYMENT =================
@app.route("/payment")
def payment():
    ticket = request.args.get("ticket", "")
    phone = request.args.get("phone", "")
    amount = request.args.get("amount", "0")
    
    return render_template("payment.html", ticket=ticket, phone=phone, amount=amount)

@app.route("/generate-upi-qr")
def generate_upi_qr():
    """Generate UPI QR code with dynamic amount"""
    ticket = request.args.get("ticket", "test")
    amount = request.args.get("amount", "100")
    
    # UPI deep link with dynamic amount
    upi_link = f"upi://pay?pa=prapti250305@okicici&pn=Preschool&am={amount}&tr={ticket}&tn=Annual%20Day%20Pass"
    
    # Generate QR code
    qr_img = qrcode.make(upi_link)
    
    # Save temporarily
    qr_path = f"qr/upi_{ticket}.png"
    qr_img.save(qr_path)
    
    return send_from_directory("qr", f"upi_{ticket}.png")

@app.route("/payment-confirm", methods=["POST"])
def payment_confirm():
    ticket_number = request.form.get("ticket_number")
    phone = request.form.get("phone")
    screenshot_file = request.files.get("payment_screenshot")
    
    # Get registration details
    conn = get_db()
    reg = conn.execute(
        "SELECT * FROM registrations WHERE ticket_number=?",
        (ticket_number,)
    ).fetchone()
    
    if not reg:
        conn.close()
        return "❌ Invalid ticket number", 404
    
    screenshot_filename = None
    
    # Handle screenshot upload
    if screenshot_file and screenshot_file.filename:
        os.makedirs("uploads/screenshots", exist_ok=True)
        # Save with ticket number as filename
        ext = screenshot_file.filename.rsplit('.', 1)[1].lower() if '.' in screenshot_file.filename else 'jpg'
        screenshot_filename = f"{ticket_number}_payment.{ext}"
        screenshot_path = f"uploads/screenshots/{screenshot_filename}"
        screenshot_file.save(screenshot_path)
    
    # Update payment status with screenshot filename
    conn.execute(
        "UPDATE registrations SET payment_status=?, payment_screenshot=? WHERE ticket_number=?",
        ("AWAITING_VERIFICATION", screenshot_filename, ticket_number)
    )
    conn.commit()
    conn.close()
    
    # Send notification to owner
    owner_message = f"""
🔔 *New Payment Notification* 🔔

Ticket: {ticket_number}
Child: {reg['child_name']}
Parent: {reg['parent1_name']}
Phone: {phone}
Amount: ₹{reg['amount_paid']}

Parent claims to have paid. Please verify payment and send the ticket.
"""
    
    send_whatsapp_message(OWNER_WHATSAPP, owner_message)
    
    # Show success message to parent
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment Submitted - Dumblebdor Kindergarten</title>
        <link rel="stylesheet" href="{ url_for('static', filename='css/main.css') }">
        <style>
            .success-box {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 8px; text-align: center; }}
            .success-box h1 {{ color: #28a745; margin-top: 0; }}
            .download-btn {{ background: #007bff; color: white; padding: 12px 30px; border: none; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: bold; text-decoration: none; display: inline-block; margin-top: 20px; }}
            .download-btn:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h1>✅ Payment Received</h1>
        </div>
        <div class="content">
            <div class="success-box">
                <h1>Thank You for Payment!</h1>
                <p style="font-size: 16px;">
                    <strong>Your payment has been recorded.</strong>
                </p>
                <p style="font-size: 16px; margin: 20px 0;">
                    ⏳ The preschool owner will verify your payment and send the ticket to your WhatsApp number.
                </p>
                <p style="font-size: 14px; margin: 20px 0; padding: 15px; background: white; border-radius: 5px;">
                    <strong>WhatsApp Number:</strong><br>
                    +91 {phone}
                </p>
                <p style="font-size: 13px; color: #666;">
                    📱 Keep an eye on your WhatsApp for the official ticket.<br>
                    Do not share your ticket with anyone.
                </p>
            </div>
        </div>
    </div>
    </body>
    </html>
    """

# ================= VERIFY =================
@app.route("/verify", methods=["GET", "POST"])
def verify():
    record = None
    error = None

    if request.method == "POST":
        ticket = request.form.get("ticket_number")

        if ticket:
            record, status = get_record(ticket)

            if status == "USED":
                error = "❌ Ticket already used – Entry denied"
                record = None
            elif status == "INVALID":
                error = "❌ Invalid ticket – Entry denied"
                record = None

    return render_template("verify.html", record=record, error=error)

def get_record(ticket):
    conn = get_db()
    r = conn.execute(
        "SELECT * FROM registrations WHERE ticket_number=?",
        (ticket,)
    ).fetchone()

    if not r:
        conn.close()
        return None, "INVALID"

    if r["attended"] == 1:
        conn.close()
        return None, "USED"

    conn.execute(
        "UPDATE registrations SET attended=1 WHERE ticket_number=?",
        (ticket,)
    )
    conn.commit()
    conn.close()
    return r, "OK"

@app.route("/tickets/<filename>")
def serve_ticket(filename):
    """Serve ticket PDFs directly for viewing/opening in browser"""
    return send_from_directory(TICKET_FOLDER, filename)

@app.route("/view-screenshot/<ticket_number>")
def view_screenshot(ticket_number):
    """View payment screenshot"""
    conn = get_db()
    reg = conn.execute(
        "SELECT payment_screenshot FROM registrations WHERE ticket_number=?",
        (ticket_number,)
    ).fetchone()
    conn.close()
    
    if not reg or not reg['payment_screenshot']:
        return "❌ Screenshot not found", 404
    
    screenshot_path = f"uploads/screenshots/{reg['payment_screenshot']}"
    if not os.path.exists(screenshot_path):
        return "❌ Screenshot file not found", 404
    
    return send_from_directory("uploads/screenshots", reg['payment_screenshot'])

@app.route("/preview-ticket/<ticket_number>")
def preview_ticket(ticket_number):
    """Preview ticket PDF with download button"""
    pdf_path = f"{TICKET_FOLDER}/{ticket_number}.pdf"
    if not os.path.exists(pdf_path):
        return "❌ Ticket not found", 404
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Preview Ticket - {ticket_number}</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 900px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 2px solid #007bff; padding-bottom: 15px; }}
            .header h2 {{ margin: 0; color: #333; }}
            .btn {{ background: #007bff; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; text-decoration: none; display: inline-block; }}
            .btn:hover {{ background: #0056b3; }}
            .btn-close {{ background: #6c757d; }}
            .btn-close:hover {{ background: #5a6268; }}
            .pdf-container {{ width: 100%; height: 600px; border: 1px solid #ddd; border-radius: 5px; overflow: hidden; }}
            .pdf-container iframe {{ width: 100%; height: 100%; border: none; }}
            .button-group {{ margin-top: 20px; text-align: center; }}
            .button-group a {{ margin-right: 10px; }}
        </style>
    </head>
    <body>
    <div class="container">
        <div class="header">
            <h2>📄 Ticket Preview: {ticket_number}</h2>
            <a href="/admin" class="btn btn-close">← Back to Admin</a>
        </div>
        
        <div class="pdf-container">
            <iframe src="/tickets/{ticket_number}.pdf" type="application/pdf"></iframe>
        </div>
        
        <div class="button-group">
            <a href="/tickets/{ticket_number}.pdf" class="btn" download="ticket_{ticket_number}.pdf">⬇️ Download Ticket (PDF)</a>
        </div>
    </div>
    </body>
    </html>
    """

# ================= ADMIN PANEL =================
@app.route("/admin")
def admin():
    conn = get_db()
    payments = conn.execute("""
        SELECT * FROM registrations 
        WHERE payment_status IN ('AWAITING_VERIFICATION', 'VERIFIED')
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    
    # Read pending WhatsApp messages
    pending_messages = []
    if os.path.exists("logs/whatsapp_queue.txt"):
        with open("logs/whatsapp_queue.txt", "r", encoding="utf-8") as f:
            pending_messages = f.read()
    
    return render_template("admin.html", payments=payments, pending_messages=pending_messages)

@app.route("/admin/verify-payment", methods=["POST"])
def admin_verify_payment():
    data = request.get_json()
    ticket = data.get("ticket")
    phone = data.get("phone")
    
    # Get registration and ticket details
    conn = get_db()
    reg = conn.execute(
        "SELECT * FROM registrations WHERE ticket_number=?",
        (ticket,)
    ).fetchone()
    
    if not reg:
        conn.close()
        return jsonify({"success": False, "message": "Ticket not found"}), 404
    
    # Update payment status to VERIFIED
    conn.execute(
        "UPDATE registrations SET payment_status=? WHERE ticket_number=?",
        ("VERIFIED", ticket)
    )
    conn.commit()
    conn.close()
    
    # Check if PDF exists
    pdf_path = f"{TICKET_FOLDER}/{ticket}.pdf"
    pdf_exists = os.path.exists(pdf_path)
    
    # Get the proper URL (use request host)
    base_url = request.host_url.rstrip('/')
    if '127.0.0.1' in base_url:
        base_url = 'http://192.168.1.9:5000'
    
    # Message for OWNER
    owner_message = f"""✅ *Payment Verified & Confirmed* ✅

Ticket: {ticket}
Child: {reg['child_name']}
Parent: {reg['parent1_name']}
Phone: {phone}
Amount: ₹{reg['amount_paid']}

👉 *Download Ticket PDF:*
{base_url}/tickets/{ticket}.pdf

📱 Send this link to parent or directly forward the PDF.
✅ Status: VERIFIED & READY"""
    
    # Message for PARENT
    parent_message = f"""✅ *Payment Verified!*

Ticket Number: {ticket}
Child: {reg['child_name']}

Your annual day entry pass is confirmed!

📱 Show this ticket at the entrance on event day.
👥 Allowed people: {reg['total_people']}

See you at the Annual Day! 🎉"""
    
    if pdf_exists:
        download_url = f"{base_url}/tickets/{ticket}.pdf"
        parent_message += f"\n\n📥 *Download Ticket:*\n{download_url}"
    
    # Send to Owner
    send_whatsapp_message(OWNER_WHATSAPP, owner_message, pdf_path if pdf_exists else None)
    
    # Send to Parent
    send_whatsapp_message(phone, parent_message, pdf_path if pdf_exists else None)
    
    # Also send email with PDF attachment
    if pdf_exists and reg['email']:
        send_email_with_ticket(reg['email'], reg['child_name'], ticket, pdf_path)
    
    return jsonify({"success": True, "message": "Ticket sent to owner and parent WhatsApp!"})

@app.route("/admin/clear-messages", methods=["POST"])
def clear_messages():
    try:
        if os.path.exists("logs/whatsapp_queue.txt"):
            os.remove("logs/whatsapp_queue.txt")
        return jsonify({"success": True})
    except:
        return jsonify({"success": False}), 500

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
