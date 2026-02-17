# 🚀 DEPLOY TO RENDER - Complete Guide

**For Complete Beginners - Step by Step**

---

## 📋 What You Need Before Starting

1. ✅ GitHub account (free) - https://github.com
2. ✅ Render account (free) - https://render.com
3. ✅ Google Gemini API key (free) - https://aistudio.google.com
4. ✅ Telegram Bot Token - from @BotFather
5. ✅ Your Telegram Chat ID: **548324624** ✅

---

## STEP 1: Get Your Free Google Gemini API Key (5 minutes)

**This is REQUIRED for the AI to work!**

1. Go to: https://aistudio.google.com/
2. Click "Sign in" (use your Google account)
3. Click "Get API Key" button
4. Click "Create API Key"
5. **COPY THE KEY** (starts with something like "AIza...")
6. Save it somewhere safe!

**Cost:** FREE forever (1,500 requests/day)

---

## STEP 2: Create Your Telegram Bot (5 minutes)

**You already have your Chat ID (548324624), now get the Bot Token:**

1. Open Telegram
2. Search for: **@BotFather**
3. Start a chat
4. Send: `/newbot`
5. Name: `Job Hunter Bot` (or whatever you want)
6. Username: `your_job_hunter_bot` (must end in "bot")
7. **COPY THE TOKEN** (looks like: `1234567890:ABC-DEFghiJKLmnoPQRstuVWXyz`)
8. Save it!

---

## STEP 3: Upload Files to GitHub (10 minutes)

**Option A: Use GitHub Website (Easier for Beginners)**

1. Go to: https://github.com
2. Click "Sign up" (if you don't have account)
3. Click the "+" icon → "New repository"
4. Repository name: `job-hunter-app`
5. Make it **Public**
6. Click "Create repository"

7. Now **upload your files:**
   - Click "uploading an existing file"
   - Drag and drop ALL these files:
     - `app.py`
     - `scrapers.py`
     - `requirements.txt`
     - `Procfile`
     - `templates/dashboard.html` (upload to templates folder)
   
8. Click "Commit changes"

**Done! Your code is on GitHub!**

---

**Option B: Use Git Command Line (If You Know Git)**

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/job-hunter-app.git
git push -u origin main
```

---

## STEP 4: Deploy to Render (10 minutes)

**Now the exciting part - make it live!**

1. Go to: https://render.com
2. Click "Sign up" → "Sign up with GitHub"
3. Authorize Render to access your GitHub

4. Click "New +" → "Web Service"

5. Find your repository:
   - It should show `your-username/job-hunter-app`
   - Click "Connect"

6. **Configure the service:**
   - **Name:** `job-hunter` (or whatever you want)
   - **Region:** Choose closest to you
   - **Branch:** `main`
   - **Root Directory:** (leave blank)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`

7. **Plan:** Select **FREE** ✅

8. **Environment Variables** (IMPORTANT!):
   Click "Add Environment Variable" and add these:

   ```
   Key: GEMINI_API_KEY
   Value: [Paste your Gemini API key from Step 1]
   
   Key: TELEGRAM_BOT_TOKEN  
   Value: [Paste your Telegram bot token from Step 2]
   
   Key: TELEGRAM_CHAT_ID
   Value: 548324624
   ```

9. Click "Create Web Service"

---

## STEP 5: Wait for Deployment (5-10 minutes)

You'll see:
- "Build in progress..." ⏳
- Then: "Build successful" ✅
- Then: "Deploy live" ✅

**Your app is now LIVE 24/7!** 🎉

---

## STEP 6: Access Your Dashboard

Once deployed, you'll get a URL like:
```
https://job-hunter.onrender.com
```

**Visit this URL to see your dashboard!**

You should see:
- Stats (jobs found this week)
- Recent jobs list
- Live updates

---

## STEP 7: Test Telegram Notifications

The app automatically scans every 30 minutes.

To test immediately:
1. Wait 30 minutes for first scan
2. OR restart the service (Render dashboard → Manual Deploy → Deploy)

You should get Telegram messages like:
```
🔥 NEW JOB MATCH (85/100)

Discord Manager for NFT Project
💰 Rate: $30-45/hr
📍 Upwork
✅ Payment Verified

Why it matches: Perfect match for Discord/Web3 experience

Apply: https://upwork.com/...
```

---

## ✅ SUCCESS CHECKLIST

- [ ] Gemini API key obtained
- [ ] Telegram bot created
- [ ] Chat ID confirmed (548324624)
- [ ] Files uploaded to GitHub
- [ ] Render web service created
- [ ] Environment variables set
- [ ] App deployed successfully
- [ ] Dashboard accessible
- [ ] Received test Telegram message

---

## 🔧 How It Works

**Every 30 minutes, your app:**
1. ✅ Scrapes Upwork RSS feeds for community manager jobs
2. ✅ Scrapes We Work Remotely for remote jobs
3. ✅ Scrapes CryptoJobsList for Web3 jobs
4. ✅ Uses Gemini AI to analyze each job
5. ✅ Filters out scams and low-quality jobs
6. ✅ Sends Telegram alerts for jobs $25+/hr
7. ✅ Saves all jobs to dashboard

**What gets filtered OUT:**
- ❌ Jobs below $15/hr
- ❌ Customer support (email/phone)
- ❌ No payment verification
- ❌ Vague descriptions
- ❌ Scam indicators

**What gets HIGH PRIORITY alerts:**
- ✅ $25-40+/hr
- ✅ Discord Manager roles
- ✅ Community Manager roles
- ✅ Web3/NFT/DAO projects
- ✅ Payment verified clients

---

## 📱 Using Your Dashboard

**Dashboard URL:** https://your-app-name.onrender.com

**Features:**
- See all jobs found this week
- View high priority jobs
- Check how many scams filtered
- Review job details before applying
- Click job titles to apply directly

**Auto-refreshes every 5 minutes**

---

## 🐛 Troubleshooting

### "Build Failed"
→ Check you uploaded ALL files
→ Make sure `requirements.txt` and `Procfile` exist
→ Check Render logs for specific error

### "No Jobs Showing"
→ Wait 30 minutes for first scan
→ Check Render logs to see if scrapers are working
→ Keywords might be too specific (this is rare)

### "No Telegram Messages"
→ Double-check TELEGRAM_BOT_TOKEN is correct
→ Verify TELEGRAM_CHAT_ID is 548324624
→ Make sure you clicked "Start" on your bot in Telegram
→ Check Render logs for Telegram errors

### "App Sleeping"
→ Render free tier sleeps after 15 min inactivity
→ It wakes up when someone visits the URL
→ Set up a free monitor (UptimeRobot.com) to ping it every 5 min

---

## 💡 Pro Tips

### Keep It Awake (Free)
1. Go to: https://uptimerobot.com
2. Create free account
3. Add monitor:
   - Type: HTTP(s)
   - URL: Your Render app URL
   - Interval: 5 minutes
4. This keeps your app awake 24/7!

### Customize Check Interval
In Render environment variables, add:
```
Key: CHECK_INTERVAL
Value: 30
```
(Value is in minutes. 30 = check every 30 minutes)

### View Logs
Render Dashboard → Your Service → Logs

You'll see:
- When jobs are found
- AI analysis results
- Telegram notifications sent
- Any errors

---

## 🎯 What Jobs You'll Get

Based on REAL Upwork data analysis:

**High Priority ($25-40+/hr):**
- Discord Manager positions
- Web3 Community Manager
- DAO Community roles
- Gaming Community Manager

**Medium Priority ($20-25/hr):**
- Community Engagement Specialist
- Social Media + Community roles
- Virtual Assistant (Discord focus)

**Filtered Out:**
- E-commerce customer support
- Generic email support
- Jobs below $15/hr
- Scam postings

---

## 📊 Expected Results

**Based on your profile (Discord/Web3/6 years exp):**

- **Jobs per week:** 20-50 new opportunities
- **High priority:** 5-10 excellent matches
- **Scams filtered:** 10-20 low-quality jobs
- **Platforms:** Upwork (most), WWR, CryptoJobs
- **Telegram alerts:** 1-3 per day for top jobs

---

## 🚀 You're Done!

Your job hunter is now:
- ✅ Running 24/7 on Render (FREE)
- ✅ Using Google Gemini AI (FREE)
- ✅ Sending Telegram alerts
- ✅ Filtering scams automatically
- ✅ Focusing on $25-40/hr Discord/Community roles
- ✅ Protecting your 86 Upwork connects

**Total Cost: $0/month** 🎉

---

## 🆘 Need Help?

If something isn't working:
1. Check Render logs first
2. Verify all environment variables are set
3. Make sure Gemini API key is valid
4. Test Telegram bot manually

**Common fixes solve 90% of issues!**

---

## 🎊 Congratulations!

You now have a professional AI-powered job hunting assistant running 24/7 for FREE!

**Check your Telegram regularly and happy job hunting!** 💼🎯
