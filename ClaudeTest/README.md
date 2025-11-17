# AI-Powered Analytics Chat for Energy B2B Sales

An intelligent analytics platform that enables business users to query sales and commission data using natural language. Built with Claude AI and Streamlit - **no database required** for quick demos and showcasing.

## 🎯 Overview

This system allows non-technical users to ask questions in plain English and receive instant answers with visualizations. Perfect for:
- **Showcasing AI capabilities** to stakeholders
- **Reducing analytics team bottlenecks**
- **Democratizing data access** across your organization

## ✨ Features

- **Natural Language Querying**: Ask questions in plain English
- **Intelligent Visualizations**: Automatic chart selection (bar, line, pie, scatter)
- **Role-Based Access Control**: 4 permission levels
- **Mock Data Included**: Energy B2B sales data ready to go
- **No Database Setup**: Uses in-memory pandas DataFrames
- **Export Capabilities**: Download results as CSV
- **Secure**: Read-only queries, authentication, row-level security

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Anthropic API key ([get one here](https://console.anthropic.com/))

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd ClaudeTest

# Run setup script (creates venv, installs deps, creates admin user)
./setup.sh
```

### 2. Add Your API Key
Edit `.env` and add your Anthropic API key:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

### 3. Run the App
```bash
./run_app.sh
# Or: streamlit run app/main.py
```

### 4. Open Browser
Navigate to `http://localhost:8501` and login with the admin credentials you created.

## 💡 Try These Questions

- "Show top 10 sales reps by revenue this month"
- "What's our total pipeline value by deal stage?"
- "Show commission payments in the last quarter"
- "Which products generate the most revenue?"
- "Show sales trends over the last 6 months"
- "List all open deals over $50,000"

## 📊 Mock Data Included

The system comes pre-loaded with realistic energy B2B sales data:
- **30 customers** with varying energy consumption
- **8 sales reps** across 4 teams
- **80 deals** at different pipeline stages
- **6 energy products/services**
- **Commission tracking** and payment history
- **200+ activities** (calls, meetings, emails)

Perfect for demonstrations without needing to connect to real systems!

## 🏗️ Architecture

```
User Question
     ↓
Claude API (Text-to-SQL)
     ↓
SQL Query
     ↓
PandasSQL (In-Memory)
     ↓
Results + Auto-Visualization
```

## 📁 Project Structure

```
ClaudeTest/
├── app/
│   ├── main.py              # Streamlit UI
│   ├── database.py          # In-memory SQL execution
│   ├── mock_data.py         # Sample data generation
│   ├── llm.py               # Claude API integration
│   ├── visualizations.py   # Plotly charts
│   └── auth.py              # Security & permissions
├── config/
│   └── users.yaml           # User accounts & roles
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml.example # Secrets template
├── setup.sh                 # Quick setup script
├── run_app.sh              # Launch script
├── requirements.txt         # Python dependencies
└── .env.example            # Environment variables template
```

## 🔐 User Roles

### Admin
- Full access, can view all data and export

### Analyst
- Broad access for analytics work, can export

### Manager
- Team performance visibility, limited sensitive data

### Sales Rep
- Own data only, automatic filtering applied

## 🚀 Deploy to Streamlit Cloud

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit: AI Analytics Chat"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repo
4. Main file: `app/main.py`
5. Add secrets:
   - `ANTHROPIC_API_KEY` = your API key
   - `APP_SECRET_KEY` = any random string
   - `ENVIRONMENT` = "production"
6. Deploy!

Your app will be live at: `https://your-app-name.streamlit.app`

## 💰 Cost Estimation

- **Claude API**: ~$0.003 per query
- **Streamlit Cloud**: Free tier available
- **No database costs**: Uses in-memory data

For 1,000 queries/month: ~$3

## 🔧 Configuration

### Environment Variables (.env)
```bash
ANTHROPIC_API_KEY=your_key_here  # Required
APP_SECRET_KEY=random_string     # For session management
ENVIRONMENT=development          # or production
```

### User Management (config/users.yaml)
Add users and configure roles. Passwords are bcrypt hashed.

## 🛠️ Development

### Add More Sample Data
Edit `app/mock_data.py` to customize the mock data for your industry.

### Customize Prompts
Edit `app/llm.py` to refine SQL generation for your use cases.

### Add New Visualizations
Edit `app/visualizations.py` to add custom chart types.

## 🐛 Troubleshooting

### "Module not found" errors
```bash
pip install -r requirements.txt
```

### "Invalid API key"
Check your `.env` file and ensure `ANTHROPIC_API_KEY` is set correctly.

### Questions generate incorrect SQL
The mock data uses SQLite syntax via pandasql. Some advanced PostgreSQL features may not work. Stick to standard SQL.

## 📈 Next Steps

### For Production Use
1. Replace `app/database.py` with real database connection
2. Add proper database (PostgreSQL, MySQL, etc.)
3. Implement data pipeline from your CRM/ERP
4. Add query caching for performance
5. Set up monitoring and logging

### For Enhanced Demo
1. Add more industry-specific mock data
2. Create saved "favorite" queries
3. Add scheduled reports
4. Integrate with Slack/Teams

## 🤝 Contributing

This is a showcase/demo project. Feel free to fork and customize for your needs!

## 📄 License

[Add your license]

## 📞 Support

For questions:
1. Check the troubleshooting section
2. Review the code comments
3. Check Streamlit and Anthropic docs

---

**Built with ❤️ using Claude AI, Streamlit, and Python**
