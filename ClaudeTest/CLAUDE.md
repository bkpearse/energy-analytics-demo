# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AI-Powered Analytics Chat for Energy B2B Sales (Demo Version)**

This is a natural language to SQL analytics platform that enables business users to query sales data without writing SQL. Built for **showcasing and demos** - uses in-memory mock data, no database required.

**Key Technologies:**
- **Backend**: Python 3.9+, PandasSQL (in-memory)
- **Frontend**: Streamlit
- **AI**: Claude API (Anthropic) for text-to-SQL
- **Data**: Mock/sample data in pandas DataFrames
- **Visualization**: Plotly

## Architecture

### System Flow
1. User asks question in natural language via Streamlit UI
2. Claude API converts question to SQL query
3. Query is validated for security
4. PandasSQL executes query against in-memory DataFrames
5. Results auto-visualized (bar/line/pie/scatter/table)
6. User can export (if authorized)

### Data Layer
- **No database required**: All data in `app/mock_data.py`
- **In-memory execution**: PandasSQL library
- **Realistic sample data**: Energy B2B sales scenario
- **Perfect for demos**: No setup, no credentials, just run

## Directory Structure

```
app/
  main.py              # Streamlit UI and main application
  database.py          # In-memory query execution (PandasSQL)
  mock_data.py         # Sample data generation
  llm.py               # Claude API integration for SQL generation
  visualizations.py    # Plotly chart generation
  auth.py              # Authentication and authorization

config/
  users.yaml           # User accounts and role permissions

.streamlit/
  config.toml          # Streamlit app configuration
  secrets.toml.example # Template for secrets

setup.sh               # Interactive setup script
run_app.sh            # Application launcher
```

## Common Commands

### Quick Start
```bash
# One-time setup (creates venv, installs deps, creates admin)
./setup.sh

# Run the app
./run_app.sh
# Or: streamlit run app/main.py
```

### Development
```bash
# Install/update dependencies
pip install -r requirements.txt

# Run with auto-reload
streamlit run app/main.py --server.runOnSave true

# Generate password hash for users.yaml
python -c "import bcrypt; print(bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode())"
```

### Deployment
```bash
# See DEPLOY.md for full instructions

# Quick deploy to Streamlit Cloud:
# 1. Push to GitHub
# 2. Connect repo at share.streamlit.io
# 3. Add ANTHROPIC_API_KEY to secrets
# 4. Deploy!
```

## Core Components

### 1. Mock Data (`app/mock_data.py`)

**Generates realistic sample data** for energy B2B sales:
- 30 customers with energy consumption data
- 8 sales reps across 4 teams
- 80 deals at various pipeline stages
- 6 energy products
- Commission tracking
- 200+ activities

**Key function**: `generate_mock_data()` returns dict of pandas DataFrames

**Views**:
- `sales_pipeline`: Current pipeline with status
- `monthly_sales_performance`: Aggregated metrics by rep/month

**To customize**: Edit the data generation logic in this file

### 2. Database Layer (`app/database.py`)

**DatabaseManager class** handles in-memory SQL:
- `execute_query(sql)` - Runs SQL via PandasSQL, returns DataFrame
- `get_schema_info()` - Returns table/column metadata for Claude
- `validate_query(sql)` - Security check (read-only)
- `test_connection()` - Health check

**Important**: Uses PandasSQL which supports SQLite syntax. Some PostgreSQL features may not work. Stick to standard SQL.

### 3. LLM Integration (`app/llm.py`)

**SQLGenerator class** interfaces with Claude:
- `generate_sql(question)` - Converts natural language to SQL
- Returns: SQL, explanation, suggested viz type, columns
- Model: `claude-sonnet-4-5-20250929`

**System prompt**:
- Includes full schema context dynamically
- Instructs JSON response format
- Guides visualization selection

**To customize**: Edit system prompt for industry-specific knowledge

### 4. Visualization (`app/visualizations.py`)

**Visualizer class** creates Plotly charts:
- `create_visualization(df, viz_type, columns)` - Main method
- Auto-detects appropriate columns if not specified
- Types: table, bar, line, pie, scatter
- Formats numbers and dates for display

### 5. Authentication (`app/auth.py`)

**AuthManager class** handles security:
- Loads users from `config/users.yaml`
- Bcrypt password verification
- Role-based permissions (admin, analyst, manager, sales_rep)
- Row-level security filters (WIP - simplified for demo)

### 6. Main App (`app/main.py`)

**Streamlit UI**:
- Login page
- Sidebar with examples and user info
- Chat interface with history
- Results with auto-visualization
- SQL query viewer (expandable)
- Export button (permission-based)

**Session state**:
- `authenticated`, `username`, `user_info`
- `chat_history` - Conversation history
- `sql_generator` - Cached instance

## Development Patterns

### Adding New Mock Data Fields

1. Edit `app/mock_data.py`
2. Add columns to relevant DataFrames
3. Schema auto-updates (dynamically fetched)
4. Claude will automatically see new fields

### Modifying SQL Generation

1. Edit `app/llm.py` - `SQLGenerator.generate_sql()`
2. Update system prompt with domain knowledge
3. Modify table descriptions in `build_schema_context()`
4. Test with various questions

### Customizing Visualizations

1. Edit `app/visualizations.py`
2. Add new viz type to `create_visualization()`
3. Update Claude prompt to suggest when appropriate

### Adding New Users/Roles

1. Generate password hash:
   ```bash
   python -c "import bcrypt; print(bcrypt.hashpw('password'.encode(), bcrypt.gensalt()).decode())"
   ```
2. Edit `config/users.yaml`
3. Add user entry with hashed password
4. Assign role (admin/analyst/manager/sales_rep)

## Configuration

### Environment Variables

**Local (.env)**:
```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Required
APP_SECRET_KEY=random_string     # For sessions
ENVIRONMENT=development
```

**Streamlit Cloud (.streamlit/secrets.toml)**:
```toml
ANTHROPIC_API_KEY = "sk-ant-xxxxx"
APP_SECRET_KEY = "random_string"
ENVIRONMENT = "production"
```

### User Configuration (config/users.yaml)

```yaml
credentials:
  usernames:
    username:
      email: user@company.com
      name: Full Name
      password: $2b$12$hashed...  # bcrypt hash
      role: admin  # or analyst, manager, sales_rep

roles:
  admin:
    can_view_sensitive: true
    can_export: true
    max_query_rows: 10000
```

## Deployment

### Recommended: Streamlit Cloud

**Pros**: Free tier, easy setup, automatic HTTPS, great for demos
**Steps**: See DEPLOY.md

1. Push to GitHub
2. Connect at share.streamlit.io
3. Add secrets (ANTHROPIC_API_KEY)
4. Deploy

### Alternatives

- **Heroku**: See DEPLOY.md
- **Railway**: See DEPLOY.md
- **Docker**: See DEPLOY.md
- **Own server**: See DEPLOY.md

## Testing

### Manual Test Checklist

**Basic Functionality**:
- [ ] Login with valid credentials
- [ ] Query: "Show total revenue" returns results
- [ ] Query: "Sales by rep" shows bar chart
- [ ] Export CSV button visible for admin

**SQL Generation**:
- [ ] Aggregations: "Sum of deal values"
- [ ] Filtering: "Deals over $50,000"
- [ ] Time-based: "Sales last month"
- [ ] Joins: "Customers with most deals"
- [ ] Grouping: "Revenue by team"

**Security**:
- [ ] Cannot run UPDATE/DELETE/DROP
- [ ] Invalid login fails
- [ ] Logout works

**Visualizations**:
- [ ] Bar chart for categories
- [ ] Line chart for time series
- [ ] Table for detailed data
- [ ] Export downloads CSV

## Troubleshooting

### "PandasSQL error"
- Query uses PostgreSQL syntax not supported by SQLite
- Simplify to standard SQL (no CTEs with multiple refs, no DISTINCT ON, etc.)
- Check query in sqlite3 online tool

### "Module anthropic not found"
- Run: `pip install -r requirements.txt`
- Activate venv: `source venv/bin/activate`

### "Invalid API key"
- Check `.env` has correct key
- No extra spaces/quotes around key value
- Verify key at console.anthropic.com

### "Incorrect SQL generated"
- Edit system prompt in `app/llm.py`
- Add more table context in `build_schema_context()`
- Provide example queries in prompt
- Rephrase question

### "Slow query performance"
- Claude API call is main bottleneck (1-3 seconds)
- This is expected for text-to-SQL
- Consider caching common queries (not implemented)

## Cost & Performance

### API Costs
- **Claude API**: ~$0.003 per query
- **1,000 queries**: ~$3/month
- **10,000 queries**: ~$30/month

### Performance Notes
- Mock data fits in memory (~MB)
- PandasSQL is slower than real DB but fine for demo
- Claude API latency: 1-3 seconds
- Total query time: 1-5 seconds

### Optimization Tips
- SQLGenerator is cached (@st.cache_resource)
- Chat history in session state
- Consider caching query results for common questions

## Limitations (Demo Version)

1. **SQLite syntax only**: PandasSQL uses SQLite, not PostgreSQL
2. **No data persistence**: Data resets on app restart (by design)
3. **Limited SQL features**: No advanced window functions, CTEs have limits
4. **No query caching**: Each question hits Claude API
5. **Session-based history**: Refresh clears chat history

## Migration to Production

To convert this to production with real database:

1. **Replace** `app/database.py` with real DB connection (PostgreSQL/MySQL)
2. **Remove** `app/mock_data.py`
3. **Add** data pipeline from CRM/ERP
4. **Update** `app/llm.py` system prompt for PostgreSQL
5. **Add** query result caching (Redis)
6. **Implement** proper row-level security in DB layer
7. **Add** audit logging of all queries
8. **Set up** monitoring and alerting

## Important Notes

- **Demo-focused**: Optimized for showcasing, not production
- **No sensitive data**: All mock data is fake
- **Cost-effective**: ~$3/month for 1,000 queries
- **Easy deployment**: Streamlit Cloud free tier works great
- **No database setup**: Perfect for quick demos
- **Customizable**: Easy to adapt mock data to different industries

## Support Resources

- **README.md**: User-facing documentation
- **DEPLOY.md**: Deployment instructions
- **Streamlit docs**: https://docs.streamlit.io
- **Anthropic docs**: https://docs.anthropic.com
- **PandasSQL docs**: https://github.com/yhat/pandasql
