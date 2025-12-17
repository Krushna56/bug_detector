# AI Security Testing Agent 🔒🤖

An AI-powered autonomous security testing agent that performs automated vulnerability detection and penetration testing to improve system security.

## ⚡ Features

- **Automated Security Scanning**: Static (SAST) and dynamic (DAST) analysis
- **AI-Powered Analysis**: Uses LLMs to prioritize vulnerabilities and generate fixes
- **Multiple Scanner Support**: Semgrep, OWASP ZAP, dependency scanning
- **RAG System**: Retrieves security knowledge from OWASP, CVE, CWE databases
- **Auto-Patch Generation**: AI generates code fixes for vulnerabilities
- **REST API**: FastAPI-based backend with automatic documentation
- **SQLite Database**: Lightweight, no external database required

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Node.js 18+ (for frontend)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/Krushna56/bug_detector.git
   cd bug_detector
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your OpenAI API key:

   ```env
   OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend**

   ```bash
   cd backend/orchestrator
   python -m uvicorn app.main:app --reload
   ```

5. **Access the API**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

## 📁 Project Structure

```
bug_detector/
├── backend/
│   ├── orchestrator/          # Main FastAPI application
│   │   └── app/
│   │       ├── api/           # API routes
│   │       ├── core/          # Configuration
│   │       ├── db/            # Database models
│   │       ├── services/      # Business logic
│   │       └── utils/         # Helper functions
│   ├── scanners/              # Security scanners
│   │   ├── semgrep/          # Static analysis
│   │   ├── zap/              # Dynamic analysis
│   │   └── dependency/       # Dependency scanning
│   ├── llm/                   # LLM integration
│   └── rag/                   # RAG system
├── frontend/                  # React UI (coming soon)
├── data/                      # SQLite DB & vector store
├── .env                       # Environment variables (create from .env.example)
└── requirements.txt           # Python dependencies
```

## 🔧 Configuration

All configuration is done via environment variables in `.env`:

| Variable            | Description               | Default                            |
| ------------------- | ------------------------- | ---------------------------------- |
| `DATABASE_URL`      | SQLite database path      | `sqlite:///./data/bug_detector.db` |
| `OPENAI_API_KEY`    | OpenAI API key            | Required for AI features           |
| `DEFAULT_LLM_MODEL` | LLM model to use          | `gpt-4o-mini`                      |
| `SEMGREP_TIMEOUT`   | Scanner timeout (seconds) | `300`                              |
| `DEBUG`             | Enable debug mode         | `true`                             |

## 📖 API Usage

### Trigger a Security Scan

```bash
curl -X POST http://localhost:8000/api/webhook/pr \
  -H "Content-Type: application/json" \
  -d '{
    "repo": "owner/repo",
    "pr_number": 123,
    "commit_sha": "abc123def",
    "artifact_url": "https://example.com/sarif-results.json",
    "scan_type": "semgrep"
  }'
```

### List Scans

```bash
curl "http://localhost:8000/api/scans?repo=owner/repo&limit=10"
```

### Get Scan Details

```bash
curl "http://localhost:8000/api/scans/{scan_id}"
```

### Get Findings

```bash
curl "http://localhost:8000/api/findings/{scan_id}"
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api/test_scans.py
```

## 🛡️ Security Considerations

> **⚠️ IMPORTANT**: Only test systems you own or have explicit written permission to test. Unauthorized penetration testing is illegal.

- Never commit `.env` file (already in `.gitignore`)
- Change `SECRET_KEY` in production
- Use strong API keys
- Enable rate limiting for production
- Implement proper authentication before deployment
- Review all scan results before taking action

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development Roadmap

- [x] Phase 1: Foundation & Security Fixes
  - [x] Fix requirements.txt
  - [x] Remove hardcoded credentials
  - [x] Switch to SQLite
  - [x] Update API routes with dependency injection
- [ ] Phase 2: LLM Integration
  - [ ] Implement LLM router
  - [ ] Add prompt templates
  - [ ] Integrate OpenAI/Anthropic
- [ ] Phase 3: RAG System
  - [ ] Set up ChromaDB
  - [ ] Implement document ingestion
  - [ ] Add semantic search
- [ ] Phase 4: AI Services
  - [ ] Vulnerability prioritization
  - [ ] Patch generation
  - [ ] Explanation generation
- [ ] Phase 5: Frontend
  - [ ] React dashboard
  - [ ] Scan visualization
  - [ ] Finding viewer

## 🐛 Known Issues

- Database migrations not yet implemented (using `create_all()` for now)
- LLM router is empty (needs implementation)
- Vector store is empty (needs implementation)
- No authentication/authorization yet
- Frontend not yet built

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Semgrep](https://semgrep.dev/) for static analysis
- [OWASP ZAP](https://www.zaproxy.org/) for dynamic testing
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [LangChain](https://python.langchain.com/) for LLM orchestration

## 📧 Contact

Krushna - [@Krushna56](https://github.com/Krushna56)

Project Link: [https://github.com/Krushna56/bug_detector](https://github.com/Krushna56/bug_detector)

---

**Built with ❤️ for better security**
