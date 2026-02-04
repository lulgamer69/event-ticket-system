# 🆘 Render Deployment - Troubleshooting

## 🔴 Common Deployment Issues & Fixes

### Issue 1: Build Failed - "Module not found"

**Error Message:**
```
ModuleNotFoundError: No module named 'flask'
```

**Cause**: Missing dependency in `requirements.txt`

**Fix**:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "Update requirements"
git push origin main
```

Then redeploy on Render.

---

### Issue 2: App Crashes After Deploy

**Error Message:**
```
H10 error code: App crashed
```

**Cause**: Usually `debug=True` or port binding issue

**Fix**: Verify `app.py` has:
```python
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

Then:
```bash
git add app.py
git commit -m "Fix production settings"
git push origin main
```

---

### Issue 3: Database Not Found

**Error Message:**
```
sqlite3.OperationalError: unable to open database file
```

**Cause**: `/tmp` directory resets on Render (SQLite doesn't persist)

**Solutions**:

**Option A: Use PostgreSQL** (Recommended)
1. In Render: Create PostgreSQL database
2. Update app.py to use PostgreSQL instead of SQLite
3. Add DATABASE_URL environment variable

**Option B: Accept Data Loss**
- Database resets on each redeploy
- Fine for testing, not for production

**Option C: Backup Before Deploy**
```bash
# Before pushing:
cp database.db database.backup.db
git add database.backup.db
```

---

### Issue 4: WhatsApp Messages Not Sending

**Symptom**: App works but WhatsApp messages don't arrive

**Cause**: Free API blocked or rate-limited

**Fix: Switch to Twilio**

1. Sign up at [twilio.com](https://twilio.com)
2. Get WhatsApp Sandbox credentials
3. Add environment variables in Render:
   ```
   TWILIO_ACCOUNT_SID=ACxxxxx
   TWILIO_AUTH_TOKEN=your_token
   ```
4. Update app.py:

```python
from twilio.rest import Client
import os

def send_whatsapp_message(phone, message):
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        print("WhatsApp API not configured")
        return False
    
    try:
        client = Client(account_sid, auth_token)
        msg = client.messages.create(
            from_="whatsapp:+14155238886",
            body=message,
            to=f"whatsapp:+91{phone}"
        )
        return msg.sid is not None
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False
```

---

### Issue 5: Static Files Not Loading

**Symptoms**:
- CSS not loading
- Images not showing
- 404 errors for static files

**Cause**: Flask can't find static folder

**Check**:
1. Verify folder structure:
   ```
   static/
     css/
       main.css
     images/
       upi_qr.png
   ```

2. Verify templates exist:
   ```
   templates/
     register.html
     payment.html
     admin.html
     verify.html
   ```

3. Rebuild and push:
   ```bash
   git add -A
   git commit -m "Ensure all static files included"
   git push origin main
   ```

---

### Issue 6: "No module named app"

**Error Message:**
```
No module named 'app'
```

**Cause**: `app.py` not found or Procfile path wrong

**Fix**:
1. Verify `app.py` exists in root directory
2. Check Procfile has: `web: gunicorn app:app`
3. Verify git push succeeded: `git log --oneline`

---

### Issue 7: Port Already in Use (Local Testing)

**Error Message:**
```
OSError: [Errno 48] Address already in use
```

**Cause**: Something using port 5000

**Fix**:
```bash
# Kill process using port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID [PID_NUMBER] /F

# Then restart:
python app.py
```

---

### Issue 8: Template Not Found Error

**Error Message:**
```
TemplateNotFound: register.html
```

**Cause**: Missing template file or wrong folder

**Fix**:
1. Check templates exist:
   ```
   templates/
     register.html
     payment.html
     verify.html
     admin.html
   ```

2. Ensure folder is named exactly `templates/` (lowercase)

3. Push to GitHub:
   ```bash
   git add templates/
   git commit -m "Add missing templates"
   git push origin main
   ```

---

### Issue 9: 502 Bad Gateway Error

**Symptom**: App deployed but shows 502 error

**Possible Causes**:
1. App crashes on startup
2. Port not binding correctly
3. Missing environment variable

**Check Logs**:
1. In Render dashboard, click "Logs"
2. Look for error messages
3. Fix and redeploy

**Common Fix**:
```python
# Ensure this is in app.py:
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

### Issue 10: Changes Not Reflecting After Push

**Symptom**: Code updated but old version still running

**Causes**:
1. Git push didn't complete
2. Render didn't redeploy
3. Browser cache

**Fix**:
```bash
# Verify push worked:
git log --oneline -5

# Force hard reset if needed:
git reset --hard origin/main

# Push again:
git push origin main

# Then:
# 1. Check Render logs
# 2. Click "Restart Service" in Render dashboard
# 3. Hard refresh browser (Ctrl+Shift+R)
```

---

## 🔧 Debug Checklist

When something fails:

- [ ] Check Render logs (Dashboard → Logs tab)
- [ ] Look for Python error messages
- [ ] Verify Procfile format (no extra spaces)
- [ ] Check `requirements.txt` is complete
- [ ] Verify app.py syntax: `python -m py_compile app.py`
- [ ] Test locally first: `python app.py`
- [ ] Verify git push succeeded: `git log`
- [ ] Check for environment variable issues
- [ ] Restart Render service

---

## 🚨 Emergency Rollback

If latest deploy breaks the app:

```bash
# Find last working commit:
git log --oneline

# Reset to that commit:
git reset --hard <commit-hash>

# Force push:
git push -f origin main
```

Then Render auto-redeploys to previous version.

---

## 📞 Get Help

1. **Render Status**: Check [status.render.com](https://status.render.com)
2. **View Logs**: Render dashboard → Logs tab
3. **Test Locally**: `python app.py`
4. **Check GitHub**: Verify files pushed
5. **Rebuild Service**: Render dashboard → Restart

---

## 🎯 Prevention Tips

1. **Test locally before pushing**
   ```bash
   python app.py  # Works? Then push
   ```

2. **Use meaningful commit messages**
   ```bash
   git commit -m "Fix payment confirmation" # Good
   git commit -m "fix" # Bad
   ```

3. **Never hardcode secrets**
   ```python
   # Bad:
   OWNER_WHATSAPP = "8591367049"
   
   # Good:
   OWNER_WHATSAPP = os.environ.get("OWNER_WHATSAPP")
   ```

4. **Keep requirements.txt updated**
   ```bash
   pip freeze > requirements.txt
   ```

5. **Test database operations**
   ```bash
   sqlite3 database.db ".tables"  # Check tables exist
   ```

---

## ✅ Success Indicators

✅ Render shows "Deploy successful"  
✅ Service shows "Live" status  
✅ No errors in logs  
✅ App responds at your Render URL  
✅ Forms submit successfully  

---

**Still stuck? Check the [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md) guide!**

