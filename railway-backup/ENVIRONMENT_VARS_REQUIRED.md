# Environment Variables Configuration

## Required Variables for meta-analysis-tool Production

Based on railway.json configuration:

### Core Settings
- `PYTHONUNBUFFERED=1`
- `PORT=${{PORT}}` (Railway auto-assigns)
- `DEBUG=false`
- `LOG_LEVEL=INFO`

### Database & Cache
- `DATABASE_URL=${{DATABASE_URL}}` (PostgreSQL connection string)
- `REDIS_URL=${{REDIS_URL}}` (Redis connection string)

### Security
- `SECRET_KEY=${{SECRET_KEY}}` (JWT signing key)
- `ALLOWED_ORIGINS=https://meta-analysis-tool.vercel.app,https://meta-analysis-tool-brandons-projects-c4dfa14a.vercel.app`

### API Keys
- `ANTHROPIC_API_KEY=${{ANTHROPIC_API_KEY}}` ⚠️ REQUIRED
- `OPENAI_API_KEY=${{OPENAI_API_KEY}}` (Optional)
- `PUBMED_API_KEY=${{PUBMED_API_KEY}}` (Optional but recommended)
- `PUBMED_EMAIL=${{PUBMED_EMAIL}}` (Optional but recommended)

### Monitoring (Optional)
- `SENTRY_DSN=${{SENTRY_DSN}}`

