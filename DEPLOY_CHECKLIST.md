# ✅ Render Deployment Checklist

## Before Pushing to GitHub

- [ ] Test app locally: `python app.py`
- [ ] All templates exist in `templates/` folder
- [ ] All CSS/images exist in `static/` folder
- [ ] `upi_qr.png` image uploaded
- [ ] Database schema tested
- [ ] No hardcoded passwords in code
- [ ] `debug=False` is set in app.py (✅ DONE)

## Configuration Files Created

- [x] `Procfile` - Render startup command
- [x] `runtime.txt` - Python 3.11.7
- [x] `render.yaml` - Render configuration
- [x] `requirements.txt` - All dependencies
- [x] `.gitignore` - Exclude unnecessary files

## GitHub Setup

```bash
# 1. Initialize/update git
cd "C:\Users\Payal Goswami\Desktop\event-registration"
git init
git add .
git commit -m "Initial commit - QR code payment system ready for Render"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/event-registration.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username.

## Render.com Setup

**5-Step Deployment:**

1. **Login**: Go to [render.com](https://render.com)
2. **New Service**: Click "New" → "Web Service"
3. **Connect Repository**: 
   - Select "GitHub"
   - Authorize & select `event-registration` repo
4. **Configure**:
   - Name: `event-registration`
   - Environment: `Python 3`
   - Build Command: (auto-detected from Procfile)
   - Start Command: (auto-detected from Procfile)
5. **Deploy**: Click "Create Web Service"

**Expected Result:**
```
✅ Build successful
✅ App running at: https://event-registration.onrender.com
```

## Post-Deployment

- [ ] Test registration page: `https://yourdomain/register`
- [ ] Test admin panel: `https://yourdomain/admin`
- [ ] Test entry verification: `https://yourdomain/verify`
- [ ] Check logs for errors
- [ ] Test WhatsApp notifications
- [ ] Share parent registration link

## Environment Variables (Add in Render Dashboard)

Settings → Environment Variables:

```
PORT=5000
FLASK_ENV=production
```

Optional (if using Twilio):
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
```

## Database Strategy

**⚠️ SQLite won't persist on Render!**

Choose one:

### Option 1: Free (Limited)
- Use SQLite temporarily
- Backup database before redeploy
- Database resets on new deployment

### Option 2: PostgreSQL (Recommended)
```
1. In Render: Create PostgreSQL Database
2. Copy connection URL
3. Add to Environment Variables:
   DATABASE_URL=postgresql://...
4. Update app.py to use PostgreSQL
```

## Troubleshooting

### App won't deploy?
```
Check Render logs:
1. Open your service
2. Click "Logs"
3. Look for errors
4. Common: missing files, syntax errors
```

### App deployed but shows error?
```
Check application logs:
1. Render dashboard → Logs
2. Look for Python errors
3. Check if port 5000 is binding
```

### WhatsApp not working?
```
- Free API might be blocked
- Switch to Twilio (paid)
- Or test locally first
```

## Deployment Time

- First deploy: ~2-3 minutes
- Subsequent deploys: ~1-2 minutes (on git push)

## Live URLs

After deployment:

```
📝 Registration:
https://event-registration.onrender.com/register

👤 Admin Panel:
https://event-registration.onrender.com/admin

🔍 Entry Verification:
https://event-registration.onrender.com/verify
```

---

## 🎯 Quick Deploy Command

```bash
cd "C:\Users\Payal Goswami\Desktop\event-registration"

# Stage all changes
git add .

# Commit
git commit -m "Ready for production deployment"

# Push to GitHub (auto-triggers Render deploy)
git push origin main
```

**That's it!** Render automatically deploys when you push. ✨

---

## 📞 Need Help?

- **Render Issues**: Check Render logs in dashboard
- **App Issues**: Test locally first (`python app.py`)
- **GitHub Issues**: Verify repository is public
- **WhatsApp Issues**: Switch to Twilio API

---

**Status: ✅ All configuration files created!**
**Next: Push to GitHub → Deploy on Render**

