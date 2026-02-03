from flask import Flask, render_template, request, send_from_directory
import sqlite3, os, random, string
from datetime import date
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import qrcode
import razorpay
from dotenv import load_dotenv
from pathlib import Path

app = Flask(__name__)
app.secret_key = "secret"

# ================= ENV =================
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

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
            attended INTEGER DEFAULT 0,

            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ================= HELPERS =================
def generate_ticket():
    return "EVT-2026-" + "".join(random.choices(string.digits, k=6))

def generate_qr(ticket):
    os.makedirs("qr", exist_ok=True)
    path = f"qr/{ticket}.png"
    qrcode.make(ticket).save(path)
    return path

def generate_ticket_pdf(ticket, child, p1, p2, total_people):
    os.makedirs("tickets", exist_ok=True)
    qr_path = generate_qr(ticket)
    pdf_path = f"tickets/{ticket}.pdf"

    c = canvas.Canvas(pdf_path, pagesize=A4)
    w, h = A4

    c.setFont("Helvetica-Bold", 22)
    c.drawRightString(w - 40, h - 40, ticket)

    c.drawImage(qr_path, w - 220, h - 300, width=160, height=160)

    c.setFont("Helvetica", 10)
    c.drawRightString(w - 40, h - 310, ticket)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, h - 120, "Preschool Annual Day Entry Pass")

    c.setFont("Helvetica", 14)
    y = h - 180
    c.drawString(40, y, f"Student Name: {child}")
    y -= 30
    c.drawString(40, y, f"Parent 1: {p1}")
    y -= 30
    c.drawString(40, y, f"Parent 2: {p2}")
    y -= 30
    c.drawString(40, y, f"People Allowed: {total_people}")

    c.setFont("Helvetica-Oblique", 10)
    c.drawString(40, 40, "QR valid for one-time entry only.")

    c.showPage()
    c.save()
    return pdf_path

# ================= RAZORPAY =================
key_id = os.getenv("RAZORPAY_KEY_ID")
key_secret = os.getenv("RAZORPAY_KEY_SECRET")

razorpay_client = razorpay.Client(auth=(key_id, key_secret))

# ================= DATE LOCK =================
REGISTRATION_END_DATE = date(2026, 2, 10)

# ================= ROUTES =================
@app.route("/")
def home():
    return "App is live ✅"

@app.route("/register", methods=["GET", "POST"])
def register():
    if date.today() > REGISTRATION_END_DATE:
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
            return "<h2 style='color:red;'>❌ Roll number already registered</h2>"

        pass_count = int(f["pass_count"])
        total_people = 3 + (pass_count - 1)
        amount = max(0, pass_count - 1) * 100

        if amount > 0:
            order = razorpay_client.order.create({
                "amount": amount * 100,
                "currency": "INR",
                "payment_capture": 1
            })
            return render_template("payment.html", order=order, data=f, key_id=key_id)

        return complete_registration(f, amount, "FREE")

    return render_template("register.html")

@app.route("/payment-success", methods=["POST"])
def payment_success():
    f = request.form
    amount = max(0, int(f["pass_count"]) - 1) * 100
    return complete_registration(f, amount, "PAID")

def complete_registration(f, amount, status):
    ticket = generate_ticket()
    total_people = 3 + (int(f["pass_count"]) - 1)

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
        int(f["pass_count"]),
        total_people,
        amount,
        status,
        ticket
    ))
    conn.commit()
    conn.close()

    pdf = generate_ticket_pdf(
        ticket,
        f["child_name"],
        f["parent1_name"],
        f["parent2_name"],
        total_people
    )

    return f"""
    <h2>Registration Successful ✅</h2>
    <h1>{ticket}</h1>
    <a href='/{pdf}' target='_blank'>Download Ticket</a>
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

@app.route("/tickets/<path:filename>")
def download_ticket(filename):
    return send_from_directory("tickets", filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
