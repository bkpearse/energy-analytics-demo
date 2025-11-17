#!/bin/bash
# Quick setup script for local development

echo "🚀 Setting up AI Analytics Chat..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
echo "✓ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

# Check for .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo "✓ .env file exists"
fi

# Generate user password hash
echo ""
echo "👤 Creating admin user..."
read -p "Admin username [admin]: " username
username=${username:-admin}

read -sp "Admin password: " password
echo ""
read -sp "Confirm password: " password_confirm
echo ""

if [ "$password" != "$password_confirm" ]; then
    echo "❌ Passwords don't match"
    exit 1
fi

# Generate hash
hash=$(python3 -c "import bcrypt; print(bcrypt.hashpw('$password'.encode(), bcrypt.gensalt()).decode())")

# Update users.yaml
cat > config/users.yaml << EOF
credentials:
  usernames:
    $username:
      email: admin@company.com
      name: Admin User
      password: $hash
      role: admin

roles:
  admin:
    description: Full access to all data and system configuration
    can_view_sensitive: true
    can_export: true
    can_view_all_reps: true
    can_view_commissions: true
    max_query_rows: 10000

  analyst:
    description: Analytics team members with broad data access
    can_view_sensitive: true
    can_export: true
    can_view_all_reps: true
    can_view_commissions: true
    max_query_rows: 5000

  manager:
    description: Sales managers who can view team performance
    can_view_sensitive: false
    can_export: true
    can_view_all_reps: true
    can_view_commissions: false
    max_query_rows: 1000

  sales_rep:
    description: Individual sales reps who can only view their own data
    can_view_sensitive: false
    can_export: false
    can_view_all_reps: false
    can_view_commissions: true
    max_query_rows: 500
EOF

echo "✓ Admin user '$username' created"
echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Run: ./run_app.sh (or: streamlit run app/main.py)"
echo "3. Open browser to http://localhost:8501"
echo "4. Login with username: $username"
