# Deployment Guide

## Quick Deploy to Streamlit Cloud (Recommended)

Streamlit Cloud is perfect for this app - free tier available, easy setup, no infrastructure management.

### Step 1: Push to GitHub

```bash
# Initialize git if not already done
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: AI Analytics Chat with mock data"

# Create main branch
git branch -M main

# Add your GitHub remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. **Sign up** at [share.streamlit.io](https://share.streamlit.io) with your GitHub account

2. **Click "New app"**

3. **Configure deployment:**
   - Repository: `YOUR_USERNAME/YOUR_REPO`
   - Branch: `main`
   - Main file path: `app/main.py`

4. **Add secrets** (click "Advanced settings" → "Secrets"):
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   APP_SECRET_KEY = "any-random-string-for-sessions"
   ENVIRONMENT = "production"
   ```

5. **Click "Deploy!"**

Your app will be live at: `https://YOUR_APP_NAME.streamlit.app`

### Step 3: Create Demo User

After deployment, you'll need to update `config/users.yaml` with a hashed password:

```bash
# Generate password hash locally
python3 -c "import bcrypt; print(bcrypt.hashpw('demo123'.encode(), bcrypt.gensalt()).decode())"

# Copy the hash and update config/users.yaml in your repo
# Commit and push the change
```

---

## Alternative: Deploy to Heroku

### Prerequisites
- Heroku account
- Heroku CLI installed

### Files Needed

Create `Procfile`:
```
web: streamlit run app/main.py --server.port=$PORT --server.address=0.0.0.0
```

Create `runtime.txt`:
```
python-3.11.0
```

### Deploy Steps

```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=sk-ant-xxxxx
heroku config:set APP_SECRET_KEY=random-string
heroku config:set ENVIRONMENT=production

# Deploy
git push heroku main

# Open app
heroku open
```

---

## Alternative: Deploy to Railway

### Steps

1. Go to [railway.app](https://railway.app)
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your repo
4. Set environment variables:
   - `ANTHROPIC_API_KEY`
   - `APP_SECRET_KEY`
   - `ENVIRONMENT=production`
5. Railway will auto-detect Streamlit and deploy

---

## Alternative: Deploy to Your Own Server

### Using Docker

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:
```bash
docker build -t analytics-chat .
docker run -p 8501:8501 \
  -e ANTHROPIC_API_KEY=sk-ant-xxxxx \
  -e APP_SECRET_KEY=random-string \
  analytics-chat
```

### Using systemd (Linux Server)

Create `/etc/systemd/system/analytics-chat.service`:
```ini
[Unit]
Description=AI Analytics Chat
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/analytics-chat
Environment="PATH=/var/www/analytics-chat/venv/bin"
EnvironmentFile=/var/www/analytics-chat/.env
ExecStart=/var/www/analytics-chat/venv/bin/streamlit run app/main.py

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable analytics-chat
sudo systemctl start analytics-chat
```

---

## Production Considerations

### Security Checklist
- [ ] HTTPS enabled (Streamlit Cloud handles this automatically)
- [ ] Secrets not in code/repo (use environment variables)
- [ ] Strong password hashes in users.yaml
- [ ] API key rotated regularly
- [ ] Monitor API usage/costs

### Performance
- [ ] Set appropriate Streamlit caching
- [ ] Monitor Claude API rate limits
- [ ] Consider query result caching for common questions

### Monitoring
- [ ] Set up error logging
- [ ] Monitor API costs (Anthropic console)
- [ ] Track user engagement
- [ ] Set up uptime monitoring

---

## Troubleshooting Deployment

### "Module not found" on deployment
- Check `requirements.txt` is up to date
- Ensure Python version compatibility

### "Invalid API key" after deployment
- Verify secrets are set correctly in deployment platform
- Check for whitespace/newlines in API key

### App crashes on startup
- Check deployment logs
- Verify all environment variables are set
- Test locally first with production settings

### Slow performance
- Claude API calls are the main bottleneck (~1-3 seconds)
- Consider caching SQL generator initialization
- Use Streamlit's @st.cache_data for query results

---

## Cost Breakdown

### Streamlit Cloud (Recommended for Demo)
- **Free tier**: 1 private app, unlimited public apps
- **Paid tier**: $20/month for 3 private apps

### Heroku
- **Free tier**: Limited hours/month (sleeps after 30min idle)
- **Hobby tier**: $7/month (no sleep)
- **Professional**: $25/month

### Railway
- **Free tier**: $5 credit/month
- **Pay-as-you-go**: ~$5-10/month for this app

### Claude API
- **Cost per query**: ~$0.003
- **1,000 queries/month**: ~$3
- **10,000 queries/month**: ~$30

---

## Next Steps After Deployment

1. **Share the URL** with stakeholders
2. **Create demo accounts** for different roles
3. **Gather feedback** on query accuracy
4. **Customize mock data** for your industry
5. **Plan production database** integration if moving forward
