from flask import Flask, render_template, jsonify, request
import os
import json
import sqlite3
from datetime import datetime, timedelta
import threading
import time
import requests
import google.generativeai as genai
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Configuration from environment variables (set in Render)
CONFIG = {
    'gemini_api_key': os.environ.get('GEMINI_API_KEY', ''),
    'telegram_bot_token': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
    'telegram_chat_id': os.environ.get('TELEGRAM_CHAT_ID', '548324624'),
    'min_hourly_rate': 15,  # Based on real data analysis
    'priority_rate': 25,    # Instant alerts for $25+
    'check_interval_minutes': 30,  # Check every 30 minutes
}

# Configure Gemini AI
if CONFIG['gemini_api_key']:
    genai.configure(api_key=CONFIG['gemini_api_key'])
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')

# Database setup
def init_db():
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jobs
                 (id TEXT PRIMARY KEY,
                  title TEXT,
                  platform TEXT,
                  url TEXT,
                  description TEXT,
                  rate TEXT,
                  client_verified INTEGER,
                  client_spent TEXT,
                  proposals INTEGER,
                  posted_date TEXT,
                  score INTEGER,
                  priority TEXT,
                  red_flags TEXT,
                  why_match TEXT,
                  notified INTEGER DEFAULT 0,
                  created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS stats
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  date TEXT,
                  total_found INTEGER,
                  high_priority INTEGER,
                  medium_priority INTEGER,
                  scams_filtered INTEGER,
                  connects_saved INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# Job Analysis with Gemini AI
def analyze_job(job):
    """Use Gemini to analyze if job is good match and detect scams"""
    
    prompt = f"""Analyze this job posting for a Discord/Web3 Community Manager with 6 years experience.

JOB:
Title: {job['title']}
Description: {job['description'][:500]}
Rate: {job['rate']}
Platform: {job['platform']}
Client: {"Payment Verified" if job.get('client_verified') else "Not Verified"}
Client Spent: {job.get('client_spent', 'Unknown')}
Proposals: {job.get('proposals', 'Unknown')}

PROFILE:
- 6 years experience
- Discord Architect
- Web3 Community Manager
- Virtual Assistant
- Minimum acceptable rate: $15/hr
- Target rate: $25-40/hr

ANALYZE FOR:
1. Is this a Discord/Community Manager role? (NOT customer support/email support)
2. Rate quality ($15-20=ok, $20-30=good, $30+=excellent, under $15=skip)
3. Scam indicators (vague description, no payment verification, unrealistic pay, asks for money)
4. Client quality (payment verified, spending history, proposal count)
5. Job type match (Discord, Web3, Gaming, Community vs generic VA/support)

Return ONLY valid JSON:
{{
    "score": 0-100,
    "priority": "high" or "medium" or "low" or "skip",
    "is_scam": true or false,
    "why_match": "brief reason why good/bad match",
    "red_flags": ["flag1", "flag2"] or [],
    "job_type": "Community Manager" or "Customer Support" or "Other"
}}"""

    try:
        if not CONFIG['gemini_api_key']:
            # Fallback scoring if no API key
            return basic_scoring(job)
        
        response = gemini_model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean response
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        
        analysis = json.loads(text)
        return analysis
    except Exception as e:
        print(f"AI analysis error: {e}")
        return basic_scoring(job)

def basic_scoring(job):
    """Fallback scoring without AI"""
    score = 50
    priority = "medium"
    red_flags = []
    
    # Rate check
    rate_str = job.get('rate', '').lower()
    if any(x in rate_str for x in ['$30', '$35', '$40', '$45', '$50']):
        score += 20
        priority = "high"
    elif any(x in rate_str for x in ['$25', '$28']):
        score += 10
    elif any(x in rate_str for x in ['$10', '$8', '$6', '$5', '$3']):
        score -= 30
        red_flags.append("Very low pay")
    
    # Title keywords
    title = job.get('title', '').lower()
    if any(x in title for x in ['discord', 'community manager', 'web3']):
        score += 20
    if 'customer support' in title:
        score -= 15
    
    # Client verification
    if job.get('client_verified'):
        score += 15
    else:
        red_flags.append("No payment verification")
    
    # Determine priority
    if score >= 70:
        priority = "high"
    elif score >= 50:
        priority = "medium"
    else:
        priority = "skip"
    
    return {
        "score": max(0, min(100, score)),
        "priority": priority,
        "is_scam": score < 30,
        "why_match": "Basic scoring applied",
        "red_flags": red_flags,
        "job_type": "Unknown"
    }

# Send Telegram notification
def send_telegram(message):
    """Send notification to Telegram"""
    if not CONFIG['telegram_bot_token'] or not CONFIG['telegram_chat_id']:
        print("Telegram not configured")
        return False
    
    url = f"https://api.telegram.org/bot{CONFIG['telegram_bot_token']}/sendMessage"
    data = {
        "chat_id": CONFIG['telegram_chat_id'],
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Telegram error: {e}")
        return False

# Format job alert for Telegram
def format_alert(job, analysis):
    """Format job for Telegram notification"""
    
    priority_emoji = {
        "high": "🔥",
        "medium": "⭐",
        "low": "💡"
    }
    
    emoji = priority_emoji.get(analysis['priority'], "💼")
    
    message = f"""{emoji} *NEW JOB MATCH* ({analysis['score']}/100)

*{job['title']}*
💰 Rate: {job['rate']}
📍 Platform: {job['platform']}
{"✅ Payment Verified" if job.get('client_verified') else "⚠️ Not Verified"}

*Why it matches:*
{analysis['why_match']}

*Job Type:* {analysis.get('job_type', 'N/A')}
"""

    if analysis['red_flags']:
        message += f"\n⚠️ *Red flags:* {', '.join(analysis['red_flags'][:2])}"
    
    message += f"\n\n*Apply:* {job['url']}"
    
    return message

# Save job to database
def save_job(job, analysis):
    """Save job to database"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    try:
        c.execute('''INSERT OR IGNORE INTO jobs 
                     (id, title, platform, url, description, rate, 
                      client_verified, client_spent, proposals, posted_date,
                      score, priority, red_flags, why_match, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (job['id'], job['title'], job['platform'], job['url'],
                   job['description'][:500], job['rate'],
                   1 if job.get('client_verified') else 0,
                   job.get('client_spent', 'Unknown'),
                   job.get('proposals', 0),
                   job.get('posted_date', 'Unknown'),
                   analysis['score'], analysis['priority'],
                   json.dumps(analysis['red_flags']), analysis['why_match'],
                   datetime.now().isoformat()))
        conn.commit()
        return True
    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        conn.close()

# Process new job
def process_job(job):
    """Main job processing pipeline"""
    
    # Check if already processed
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    c.execute("SELECT id FROM jobs WHERE id = ?", (job['id'],))
    if c.fetchone():
        conn.close()
        return
    conn.close()
    
    print(f"Analyzing: {job['title'][:50]}...")
    
    # Analyze with AI
    analysis = analyze_job(job)
    
    # Save to database
    save_job(job, analysis)
    
    # Send notification based on priority
    if analysis['priority'] == 'high' and not analysis['is_scam']:
        message = format_alert(job, analysis)
        if send_telegram(message):
            print(f"✅ High priority alert sent: {job['title'][:30]}")
            # Mark as notified
            conn = sqlite3.connect('jobs.db')
            c = conn.cursor()
            c.execute("UPDATE jobs SET notified = 1 WHERE id = ?", (job['id'],))
            conn.commit()
            conn.close()
    elif analysis['priority'] == 'skip':
        print(f"⏭️  Skipped (low score): {job['title'][:30]}")
    else:
        print(f"📝 Saved for review: {job['title'][:30]}")

# Job monitoring function
def monitor_jobs():
    """Main monitoring function - called periodically"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🔍 Scanning for jobs...")
    
    jobs_found = 0
    
    try:
        # Import scrapers (will create these next)
        from scrapers import scrape_upwork, scrape_weworkremotely, scrape_cryptojobs
        
        # Scrape Upwork
        try:
            upwork_jobs = scrape_upwork()
            for job in upwork_jobs:
                process_job(job)
                jobs_found += 1
        except Exception as e:
            print(f"Upwork scraper error: {e}")
        
        # Scrape We Work Remotely
        try:
            wwr_jobs = scrape_weworkremotely()
            for job in wwr_jobs:
                process_job(job)
                jobs_found += 1
        except Exception as e:
            print(f"WWR scraper error: {e}")
        
        # Scrape CryptoJobsList
        try:
            crypto_jobs = scrape_cryptojobs()
            for job in crypto_jobs:
                process_job(job)
                jobs_found += 1
        except Exception as e:
            print(f"CryptoJobs scraper error: {e}")
        
        print(f"✅ Scan complete. Found {jobs_found} new jobs.\n")
        
    except Exception as e:
        print(f"Monitor error: {e}")

# Flask routes
@app.route('/')
def dashboard():
    """Main dashboard"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    # Get stats
    c.execute("SELECT COUNT(*) FROM jobs WHERE created_at >= date('now', '-7 days')")
    total_week = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM jobs WHERE priority = 'high' AND created_at >= date('now', '-7 days')")
    high_priority = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM jobs WHERE score < 40")
    scams_filtered = c.fetchone()[0]
    
    # Get recent jobs
    c.execute("""SELECT title, platform, rate, score, priority, created_at, url 
                 FROM jobs 
                 WHERE priority != 'skip'
                 ORDER BY created_at DESC 
                 LIMIT 20""")
    recent_jobs = c.fetchall()
    
    conn.close()
    
    return render_template('dashboard.html',
                          total_week=total_week,
                          high_priority=high_priority,
                          scams_filtered=scams_filtered,
                          recent_jobs=recent_jobs)

@app.route('/api/jobs')
def api_jobs():
    """API endpoint for jobs"""
    priority = request.args.get('priority', 'all')
    
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    if priority == 'all':
        c.execute("""SELECT * FROM jobs WHERE priority != 'skip' 
                     ORDER BY created_at DESC LIMIT 50""")
    else:
        c.execute("""SELECT * FROM jobs WHERE priority = ? 
                     ORDER BY created_at DESC LIMIT 50""", (priority,))
    
    jobs = c.fetchall()
    conn.close()
    
    return jsonify({
        'jobs': [dict(zip([d[0] for d in c.description], job)) for job in jobs]
    })

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics"""
    conn = sqlite3.connect('jobs.db')
    c = conn.cursor()
    
    # Last 7 days stats
    c.execute("""SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN priority = 'high' THEN 1 ELSE 0 END) as high,
                    SUM(CASE WHEN priority = 'medium' THEN 1 ELSE 0 END) as medium,
                    SUM(CASE WHEN score < 40 THEN 1 ELSE 0 END) as scams
                 FROM jobs 
                 WHERE created_at >= date('now', '-7 days')""")
    
    stats = c.fetchone()
    conn.close()
    
    return jsonify({
        'total': stats[0],
        'high_priority': stats[1],
        'medium_priority': stats[2],
        'scams_filtered': stats[3]
    })

@app.route('/health')
def health():
    """Health check for Render"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(func=monitor_jobs, trigger="interval", minutes=CONFIG['check_interval_minutes'])
scheduler.start()

# Run initial scan on startup
monitor_jobs()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
