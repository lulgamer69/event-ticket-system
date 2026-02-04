# 🚀 Deploy to Render

## Step 1: Push Code to GitHub

```bash
cd "C:\Users\Payal Goswami\Desktop\event-registration"

git add .
git commit -m "Initial commit - QR code payment system"
git push origin main
```

## Step 2: Connect to Render

1. Go to [render.com](https://render.com)
2. Sign up / Log in
3. Click **"New"** → **"Web Service"**
4. Select **"Deploy existing repository"**
5. Connect your GitHub account
6. Select your repository

## Step 3: Configure Deployment

| Setting | Value |
|---------|-------|
| **Name** | event-registration |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app` |
| **Instance Type** | Free |

## Step 4: Environment Variables

Add these in Render dashboard (Settings → Environment):

```
PORT=5000
FLASK_ENV=production
```

## Step 5: Deploy

Click **"Create Web Service"**

Render will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Run `gunicorn app:app`
4. Assign a URL like `event-registration.onrender.com`

---

## 📋 What We Created for Render

✅ **Procfile** - Tells Render how to run the app  
✅ **render.yaml** - Render-specific configuration  
✅ **runtime.txt** - Python version specification  
✅ **Updated app.py** - Removed debug mode, added port binding  
✅ **requirements.txt** - All dependencies  

---

## 🔧 After Deployment

### Your Live URLs:

```
Registration Page:
https://event-registration.onrender.com/register

Admin Panel:
https://event-registration.onrender.com/admin

Entry Verification:
https://event-registration.onrender.com/verify
```

### Database Persistence

**⚠️ Important**: SQLite database resets on redeploy!

**Solutions:**
1. **Use PostgreSQL** (recommended for production)
2. **Use MongoDB** with Atlas
3. **Backup database** before deployment

### Add PostgreSQL (Recommended)

1. In Render dashboard, create new **PostgreSQL Database**
2. Copy connection string
3. Update `app.py` to use PostgreSQL:

```python
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    conn.row_factory = psycopg2.extras.RealDictRow
    return conn
```

---

## 📱 WhatsApp API Issues on Render

The free CallMeBot API might be blocked in production.

**Switch to Twilio:**

1. Sign up at [twilio.com](https://twilio.com)
2. Get WhatsApp sandbox number
3. Add to Render environment variables:

```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE=+1234567890
```

4. Update `app.py`:

```python
from twilio.rest import Client

def send_whatsapp_message(phone, message):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_="whatsapp:+14155238886",
        body=message,
        to=f"whatsapp:+91{phone}"
    )
    return True
```

---

## 🔗 Domain Setup (Optional)

To use custom domain like `register.yourschool.com`:

1. In Render dashboard: Settings → Custom Domain
2. Add your domain
3. Update DNS records to point to Render
4. SSL certificate auto-generated

---

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `Procfile` exists
- [ ] `requirements.txt` complete
- [ ] `runtime.txt` set to Python 3.11
- [ ] `app.py` doesn't have `debug=True`
- [ ] All static files in `static/` folder
- [ ] All templates in `templates/` folder
- [ ] `qr/` and `tickets/` folders exist
- [ ] `upi_qr.png` uploaded to `static/images/`
- [ ] Owner WhatsApp number set correctly
- [ ] Render account created
- [ ] GitHub repository connected
- [ ] Environment variables set

---

## 🚨 Troubleshooting

### Deployment Failed?

Check Render logs:
1. Go to your service
2. Click "Logs" tab
3. Look for error messages

Common issues:
- **Missing dependencies**: Update `requirements.txt`
- **Python version mismatch**: Check `runtime.txt`
- **Port binding**: Ensure `host="0.0.0.0"` in app.py
- **Database error**: SQLite won't persist, use PostgreSQL

### App Running but Shows Error?

1. Check "Logs" tab in Render
2. View application error output
3. Verify environment variables
4. Test locally first: `python app.py`

### WhatsApp Not Working?

1. Free API might be blocked on Render
2. Switch to Twilio (paid but reliable)
3. Check `TWILIO_ACCOUNT_SID` environment variable

---

## 📊 Render Plans

| Feature | Free | Paid |
|---------|------|------|
| Cost | $0/month | From $7/month |
| Uptime | 50% | 99.9% |
| Sleep | After 15 min inactivity | No sleep |
| Builds | Limited | Unlimited |
| Databases | Limited | Full support |

---

## 📝 Final Notes

- **Auto-deploy**: Every push to GitHub auto-deploys
- **Restart app**: Click "Restart service" in Render
- **View logs**: Real-time logs in Render dashboard
- **Free tier**: Sufficient for testing/small events
- **Database**: Use PostgreSQL for production data

---

## 🎉 You're Live!

Your app is now accessible at:
```
https://event-registration.onrender.com
```

Share registration link with parents! 🚀

