# Document Update Assistant

A fast, intelligent document update assistant that provides AI-powered suggestions with GitHub-style diff visualization and embedding-based semantic search.

## Features

- 🚀 **Ultra-fast AI suggestions** using GPT-3.5-turbo with optimized embedding search
- 📚 **Redis-powered semantic search** with vectorized similarity matching and caching
- 🎨 **GitHub-style diff viewer** with red/green highlighting for changes
- 🔄 **Carousel navigation** for browsing multiple suggestions
- 📱 **Responsive design** with fixed-height scrollable containers
- 🐳 **Containerized deployment** with Docker and Docker Compose
- ⚡ **Lightning-fast startup** with Redis-based embedding storage

## Quick Start with Docker

### Prerequisites

- Docker and Docker Compose installed
- OpenAI API key

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd doc-update-assistant
```

### 2. Set Environment Variables

Create a `.env` file in the root directory:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
ENVIRONMENT=production
LOG_LEVEL=info
NODE_ENV=production
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### 3. Launch the Application

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode
docker-compose up --build -d
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Redis**: localhost:6379 (for development)

### 4. Upload Documents

1. Open http://localhost:3000
2. Upload your documents through the web interface
3. Start getting AI-powered suggestions with semantic search

## Development Setup

### Backend (FastAPI)

```bash
cd backend
poetry install
poetry run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

## Architecture

### Backend (`/backend`)
- **FastAPI** with async support
- **OpenAI GPT-3.5-turbo** for fast suggestions
- **Redis-powered embedding storage** with vectorized operations
- **25-second timeout** configuration to prevent frontend timeouts
- **Advanced caching system** for embeddings and queries
- **Concurrent document processing** for faster startup

### Frontend (`/frontend`)
- **Next.js 14** with TypeScript
- **React Query** for state management
- **Tailwind CSS** for styling
- **GitHub-style diff viewer** with unified/split views
- **Carousel navigation** for suggestions
- **30-second timeout** for API calls

## Docker Services

### Redis Service
- **Port**: 6379
- **Image**: redis:7-alpine
- **Memory**: 512MB limit with LRU eviction
- **Persistence**: Append-only file for data durability
- **Health Check**: Redis ping command

### Backend Service
- **Port**: 8000
- **Health Check**: `/health` endpoint
- **Volumes**: `./backend/data` and `./backend/documents`
- **Environment**: Production-optimized with security headers
- **Depends On**: Redis service health

### Frontend Service
- **Port**: 3000
- **Depends On**: Redis and Backend service health
- **Build**: Standalone Next.js output for optimal performance
- **Proxy**: API calls routed to backend service

## Environment Configuration

### Required Environment Variables

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-...                    # Your OpenAI API key

# Backend Configuration
ENVIRONMENT=production                    # production | development
LOG_LEVEL=info                           # debug | info | warning | error

# Frontend Configuration
NODE_ENV=production                      # production | development
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000  # Backend API URL

# Redis Configuration
REDIS_URL=redis://localhost:6379/0      # Redis connection URL
```

### Optional Configuration

```bash
# Database (if using persistent storage)
DATABASE_URL=sqlite:///app/data/app.db

# CORS (if needed for custom domains)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Logging
LOG_FORMAT=json                         # json | text
```

## Deployment to GitHub

### What to Push

✅ **Include in Git:**
- All source code (`/frontend`, `/backend`)
- Configuration files (`docker-compose.yml`, `Dockerfile`s)
- Documentation (`README.md`)
- Package files (`package.json`, `pyproject.toml`)

❌ **Never Push (in .gitignore):**
- Environment files (`.env`, `.env.local`)
- API keys and secrets
- Node modules (`node_modules/`)
- Python cache (`__pycache__/`)
- Build outputs (`.next/`, `dist/`)
- Data directories (`/backend/data/`, `/backend/documents/`)

### GitHub Deployment Steps

1. **Create Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Document Update Assistant"
   git branch -M main
   git remote add origin https://github.com/yourusername/doc-update-assistant.git
   git push -u origin main
   ```

2. **Set Up GitHub Actions (Optional)**
   Create `.github/workflows/docker-build.yml` for automated builds:
   ```yaml
   name: Docker Build and Test
   on: [push, pull_request]
   jobs:
     build:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Build with Docker Compose
           run: docker-compose build
   ```

3. **Deploy to Production**
   - Use GitHub Actions with your cloud provider
   - Set `OPENAI_API_KEY` in GitHub Secrets
   - Configure production environment variables

## Performance Optimizations

- **GPT-3.5-turbo** instead of GPT-4 for 3x faster responses
- **Redis-powered embedding storage** with instant in-memory access
- **Vectorized similarity search** with numpy operations
- **Query embedding caching** to avoid redundant API calls
- **Concurrent document processing** for faster startup
- **25-second backend timeout** to stay under frontend limits
- **Next.js standalone output** for minimal Docker images
- **Connection pooling** for Redis with health checks

## Troubleshooting

### Common Issues

1. **Timeout Errors**
   - Backend has 25s timeout, frontend has 30s
   - Check OpenAI API key and rate limits

2. **CORS Issues**
   - Ensure `NEXT_PUBLIC_API_BASE_URL` is correct
   - Check Docker network configuration

3. **Build Failures**
   - Verify all dependencies in `package.json` and `pyproject.toml`
   - Check Docker build logs

4. **Redis Connection Issues**
   - Ensure Redis service is running and healthy
   - Check Redis URL configuration
   - Verify network connectivity between services

### Health Checks

```bash
# Check backend health
curl http://localhost:8000/health

# Check frontend health
curl http://localhost:3000

# Check Redis health
redis-cli ping

# View container logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs redis
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Docker Compose
5. Submit a pull request

## License

MIT License - see LICENSE file for details.