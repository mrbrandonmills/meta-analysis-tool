# Quick Start Guide

Get up and running with the Meta-Analysis Research Platform in 10 minutes!

## Prerequisites

- Python 3.11+
- Anthropic API key ([Get one here](https://console.anthropic.com/))
- Optional: Docker & Docker Compose

## Option 1: Docker (Easiest)

### 1. Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd meta-analysis-tool

# Copy environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or your preferred editor
```

Add your key:
```
ANTHROPIC_API_KEY=sk-ant-...your-key-here
```

### 2. Start Services

```bash
# Start everything
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

### 3. Test It

```bash
# Health check
curl http://localhost:8000/health

# Create a meta-analysis
curl -X POST http://localhost:8000/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "Does mindfulness reduce anxiety?",
    "topic": "Mindfulness and Anxiety",
    "databases": ["pubmed"]
  }'
```

### 4. Use the Web Interface

Open your browser to: http://localhost:3000

## Option 2: Local Development

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
export ANTHROPIC_API_KEY=sk-ant-...your-key-here
# On Windows: set ANTHROPIC_API_KEY=sk-ant-...your-key-here

# Create necessary directories
mkdir -p data/chroma temp downloads
```

### 2. Run Backend

```bash
# From backend directory
python -m app.main

# You should see:
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. Frontend Setup (Optional)

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Set environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev

# Opens at http://localhost:3000
```

## Your First Meta-Analysis

### Using cURL

```bash
# 1. Create a meta-analysis
curl -X POST http://localhost:8000/api/v1/meta-analysis/create \
  -H "Content-Type: application/json" \
  -d '{
    "research_question": "What is the effectiveness of cognitive behavioral therapy for depression in adults?",
    "topic": "CBT for Depression",
    "inclusion_criteria": [
      "Randomized controlled trial",
      "Adult population",
      "CBT intervention",
      "Depression outcome"
    ],
    "exclusion_criteria": [
      "Non-English",
      "Qualitative studies"
    ],
    "databases": ["pubmed"]
  }' | json_pp

# Save the "id" from the response!

# 2. Execute the analysis (replace {id} with your actual ID)
curl -X POST http://localhost:8000/api/v1/meta-analysis/execute/{id} | json_pp

# 3. Ask questions
curl -X POST http://localhost:8000/api/v1/meta-analysis/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many studies did you find and why were some excluded?"
  }' | json_pp

# 4. Get audit trail
curl http://localhost:8000/api/v1/meta-analysis/audit/{id} | json_pp
```

### Using Python

```python
import requests

API_URL = "http://localhost:8000"

# Create meta-analysis
response = requests.post(f"{API_URL}/api/v1/meta-analysis/create", json={
    "research_question": "Does mindfulness reduce anxiety?",
    "topic": "Mindfulness and Anxiety",
    "databases": ["pubmed"]
})

analysis = response.json()
analysis_id = analysis["id"]
print(f"Created analysis: {analysis_id}")

# Execute it
response = requests.post(f"{API_URL}/api/v1/meta-analysis/execute/{analysis_id}")
results = response.json()
print(f"Found {results['search_results']['total_found']} studies")

# Ask a question
response = requests.post(f"{API_URL}/api/v1/meta-analysis/ask", json={
    "question": "How did you search for studies?"
})
answer = response.json()
print(f"Answer: {answer['answer']}")
```

### Using the Web Interface

1. Go to http://localhost:3000
2. Enter your research question
3. Click "Create Meta-Analysis"
4. Ask questions in the Q&A section
5. Explore the results!

## Common Issues

### "Connection refused" error

**Problem**: Backend isn't running

**Solution**:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, start it:
cd backend
python -m app.main
```

### "API key not found" error

**Problem**: Environment variable not set

**Solution**:
```bash
# Set it in your terminal
export ANTHROPIC_API_KEY=your-key-here

# Or add to .env file
echo "ANTHROPIC_API_KEY=your-key-here" >> .env
```

### "Module not found" error

**Problem**: Dependencies not installed

**Solution**:
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### PubMed search returns empty results

**Problem**: Network issues or rate limiting

**Solution**:
- Check internet connection
- Try again (might be temporary)
- For development, mock data can be used

## What's Next?

Now that you're up and running:

1. **Read the [Demo Guide](DEMO.md)** - Learn how to demonstrate the platform
2. **Explore the [Architecture](../ARCHITECTURE.md)** - Understand how it works
3. **Try Different Research Questions** - See how the system handles various topics
4. **Check the Audit Trails** - See the decision-making process
5. **Ask the Q&A Agent Questions** - Test the explainability

## API Endpoints Quick Reference

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Check if server is running |
| `/api/v1/meta-analysis/create` | POST | Create new meta-analysis |
| `/api/v1/meta-analysis/execute/{id}` | POST | Execute the workflow |
| `/api/v1/meta-analysis/ask` | POST | Ask questions about results |
| `/api/v1/meta-analysis/audit/{id}` | GET | Get complete audit trail |
| `/api/v1/agents/available` | GET | List available agents |

## Getting Help

- **Issues**: Create an issue on GitHub
- **Questions**: Check the [documentation](../README.md)
- **Discussions**: Join our community discussions

## Development Mode

If you're developing new features:

```bash
# Backend with auto-reload
cd backend
uvicorn app.main:app --reload --log-level debug

# Frontend with auto-reload
cd frontend
npm run dev

# Run tests
cd backend
pytest

# Check code style
black app/
flake8 app/
```

Happy researching! 🎉
