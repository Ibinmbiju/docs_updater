# 📚 Documentation Update Assistant

A modern AI-powered tool for managing and updating documentation with GitHub-style diff visualization and intelligent suggestions.

## ✨ Features

- 🤖 **AI-Powered Suggestions**: Generate context-aware documentation improvements using OpenAI GPT-4
- 📊 **GitHub-Style Diffs**: Visual comparison of changes with unified and split-view modes
- 🔍 **Intelligent Search**: Full-text search across all documents and sections
- 📱 **Modern Web Interface**: Responsive Next.js frontend with real-time updates
- 🔄 **Workflow Management**: Approve/reject suggestions with status tracking
- 📈 **Analytics Dashboard**: Overview statistics and progress tracking

## 🏗️ Architecture

### Backend (FastAPI)
- **Port**: 8000
- **Tech Stack**: Python, FastAPI, OpenAI API, Pydantic
- **Features**: Document processing, AI suggestions, diff generation

### Frontend (Next.js)
- **Port**: 3000  
- **Tech Stack**: TypeScript, Next.js 14, Tailwind CSS, React Query
- **Features**: Modern UI, real-time updates, responsive design

## 🚀 Quick Start

### 1. Start Backend
```bash
cd doc-update-assistant/backend
python -m uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend
```bash
cd doc-update-assistant/frontend
npm run dev
```

### 3. Access Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 4. Load Documents
1. Open http://localhost:3000
2. Click **"Load All OpenAI Agents Docs (138 files)"**
3. Start generating suggestions and reviewing changes

## 🔑 Configuration

### OpenAI API Key (Required for AI features)
```bash
# Edit backend/.env file
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### Get API Key
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create account → API Keys → Create new secret key
3. Add to `.env` file in backend directory

## 📁 Project Structure

```
docs_updater/
├── README.md                           # This file
├── QUICK_START.md                      # Quick setup guide
├── SETUP_GUIDE.md                     # Detailed configuration
├── doc-update-assistant/
│   ├── backend/                        # FastAPI backend
│   │   ├── src/app/                   # Application code
│   │   ├── data/                      # OpenAI Agents docs (138 files)
│   │   ├── requirements.txt           # Python dependencies
│   │   └── .env                       # Configuration file
│   ├── frontend/                       # Next.js frontend
│   │   ├── src/                       # Application code
│   │   ├── package.json               # Node dependencies
│   │   └── .env.local                 # Frontend config
│   └── docker-compose.yml             # Docker setup
└── docs/                               # Additional documentation
    ├── AUTO_LOAD_FIXED.md            # Auto-loading feature info
    ├── COMPLETE_TESTING_GUIDE.md     # Comprehensive testing
    ├── FINAL_TESTING_INSTRUCTIONS.md # Quick testing steps
    ├── FRONTEND_DESIGN_DOCUMENT.md   # Frontend architecture
    └── INTEGRATION_COMPLETE.md       # Integration details
```

## 🧪 Testing

### Quick Health Check
```bash
# Test backend
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

### Full Functionality Test
1. **Load documents**: Use "Load All" button
2. **Search content**: Try searching for "Agent"
3. **Generate suggestions**: Enter improvement requests
4. **Review diffs**: Click on suggestions to see changes
5. **Manage workflow**: Approve/reject suggestions

## 📖 Usage Workflow

### 1. Document Management
- **Auto-load**: Documents load automatically on startup
- **Manual load**: Use file paths for custom documents
- **Browse**: View documents with syntax highlighting

### 2. Search & Discovery
- **Global search**: Find content across all documents
- **Filtered results**: Section-level results with context
- **Content types**: Code, markdown, and text sections

### 3. AI Suggestions
- **Generate**: Describe desired improvements
- **Review**: Examine AI reasoning and confidence scores
- **Visualize**: GitHub-style diffs with line-by-line changes

### 4. Workflow Management
- **Approve**: Mark good suggestions for implementation
- **Reject**: Dismiss unwanted changes
- **Track**: Monitor progress with status indicators

## 🔧 Development

### Backend Dependencies
```bash
cd doc-update-assistant/backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd doc-update-assistant/frontend
npm install
```

### Environment Variables
```bash
# Backend (.env)
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4
DEBUG=False

# Frontend (.env.local)
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## 📊 Sample Data

The project includes **138 OpenAI Agents Python documentation files** with:
- **1,639+ sections** of content
- **Code examples** in Python
- **API documentation** and guides
- **Multi-language support** (English/Japanese)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Test thoroughly
5. Submit pull request

## 📝 License

This project is provided as-is for documentation management and improvement workflows.

## 🆘 Support

### Quick Troubleshooting
- **Documents won't load**: Check `data/` folder exists
- **No AI suggestions**: Verify OpenAI API key in `.env`
- **Frontend errors**: Ensure backend is running on port 8000
- **Search no results**: Load documents first

### Documentation
- `QUICK_START.md` - Get running in 5 minutes
- `SETUP_GUIDE.md` - Detailed configuration guide
- `COMPLETE_TESTING_GUIDE.md` - Comprehensive testing steps

---

**Ready to transform your documentation workflow!** 🚀