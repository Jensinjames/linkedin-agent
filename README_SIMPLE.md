# 🚀 LinkedIn Agent - Simplified Setup Guide

## ⚡ Quick Start (Minimal Dependencies)

This guide shows you how to run the LinkedIn Agent with **minimal external configuration** - no Apify account, no Supabase setup required!

### Option 1: Super Quick Start (30 seconds)

```bash
# Clone and setup
git clone <your-repo>
cd linkedin-agent

# One-command setup
make simple-setup

# Run a test
make simple-run
```

### Option 2: Manual Setup

```bash
# 1. Install Python dependencies (minimal set)
cd backend
pip install -r requirements_simple.txt

# 2. Run directly
python simple_main.py examples/input.json
```

### Option 3: Docker (Isolated)

```bash
# Build and run in Docker
cd infrastructure/docker
docker-compose -f docker-compose.simple.yml up --build
```

## 🎯 What's Different in the Simplified Version?

### ❌ Removed Dependencies
- **No Apify Account Needed** - Uses direct web scraping
- **No Supabase Setup** - Uses local file-based authentication  
- **No Redis Required** - Direct processing without queues
- **No External APIs** - Everything runs locally

### ✅ What You Get
- **Direct Web Scraping** - Built-in contact extraction
- **Local File Storage** - Results saved to `/app/data/`
- **Simple Authentication** - File-based user management
- **Immediate Results** - No complex setup required

## 📁 Files Overview

### New Simple Files
```
├── backend/
│   ├── simple_main.py                    # Main entry point (no external deps)
│   ├── requirements_simple.txt           # Minimal requirements
│   ├── Dockerfile.simple                 # Simple Docker setup
│   └── src/adapters/
│       ├── simple_local_adapter.py       # Local-only adapter
│       └── tools_simple.py               # Direct web scraping
├── infrastructure/docker/
│   └── docker-compose.simple.yml         # Simple Docker Compose
└── setup_simple.sh                       # One-command setup
```

## 🔧 Configuration

### Minimal Environment (.env)
```bash
# Only required for LLM features (optional)
OPENAI_API_KEY=your-key-here

# Everything else is optional!
LOG_LEVEL=INFO
```

### Default Users
The simplified version creates a default admin user:
- **Username:** `admin`
- **Password:** `admin123`
- ⚠️ **Change these in production!**

## 🚀 Usage Examples

### Command Line
```bash
# Process a single URL
echo '{"query": "https://example.com"}' | python simple_main.py

# Process from file  
python simple_main.py input.json

# With custom input
echo '{"query": "https://linkedin.com/company/openai"}' | python simple_main.py
```

### Results
Results are automatically saved to:
- **Console:** Immediate output
- **File:** `/app/data/jobs/job_<id>_<timestamp>.json`
- **Logs:** `/app/data/app.log`

## 🆚 Comparison: Full vs Simplified

| Feature | Full Version | Simplified Version |
|---------|-------------|-------------------|
| **Setup Time** | 30+ minutes | 2 minutes |
| **External Accounts** | Apify + Supabase | None |
| **Dependencies** | 15+ services | 3 packages |
| **Authentication** | Supabase JWT | Local files |
| **Data Storage** | PostgreSQL + Apify | Local JSON |
| **Web Scraping** | Apify Platform | Direct scraping |
| **Queue System** | Redis | Direct processing |
| **Production Ready** | ✅ Scalable | ⚠️ Single instance |

## 🔄 Migration Path

### Start Simple, Scale Later

1. **Start** with simplified version to test functionality
2. **Develop** your scraping logic and business rules
3. **Migrate** to full version when you need:
   - Multi-user authentication
   - Horizontal scaling
   - Advanced queue management
   - Production monitoring

### Easy Migration
```bash
# Keep both versions
make simple-run          # For development/testing
make dev                 # For full production features
```

## 🛠️ Development Workflow

### 1. Test Locally
```bash
cd backend
python simple_main.py examples/input.json
```

### 2. Check Results
```bash
cat data/jobs/job_*.json
tail -f data/app.log
```

### 3. Customize Scraping
Edit `src/tools_simple.py` to modify scraping logic:

```python
def scrape_contact_details(self, url: str):
    # Add your custom extraction logic here
    # No external API limits!
```

## 🚨 Limitations of Simplified Version

- **Single Instance:** No horizontal scaling
- **File-based Auth:** Not suitable for multiple users
- **No Queue System:** Processes one request at a time
- **Basic Scraping:** Simple web scraping vs advanced Apify tools
- **No Monitoring:** Basic logging only

## 🎯 When to Use Each Version

### Use Simplified Version When:
- Testing/prototyping
- Personal projects
- Learning the system
- Minimal setup requirements
- Single user scenarios

### Use Full Version When:
- Production deployments
- Multiple users
- High-volume processing
- Advanced monitoring needed
- Team collaboration required

## 📞 Support

### Simplified Version Issues
1. Check logs: `cat backend/data/app.log`
2. Test connection: `curl -I https://example.com`
3. Verify Python: `python --version` (3.8+)

### Getting Help
- 🐛 **Issues:** Use GitHub issues
- 💬 **Questions:** Start with simplified version
- 📈 **Scaling:** Migrate to full version

---

**🎉 Enjoy your simplified LinkedIn Agent setup!**

The simplified version gets you up and running in minutes instead of hours, perfect for testing and development!
