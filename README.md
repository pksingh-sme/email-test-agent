# Email QA Agentic Platform

A multi-agent system that automates email marketing QA by fetching email proofs from Email on Acid, running deterministic QA checks, performing LLM-based judgment checks, evaluating brand compliance, prioritizing issues, generating fixes, and producing final QA reports.

## Features

- **Deterministic QA Engine**: Automated checks for common email issues
- **Multi-Agent System**: LLM-powered agents for advanced analysis
- **Brand Compliance**: Ensures emails follow brand guidelines
- **Risk Scoring**: Quantifies email quality risks
- **Fix Suggestions**: Actionable recommendations for improvements
- **Web Dashboard**: User-friendly interface for viewing results

## Architecture

The system is built with a 3-layer design:

1. **Data & Retrieval Layer**
   - Email on Acid API connector
   - HTML extraction service
   - Asset extraction (images, links, metadata)

2. **QA Engine Layer (Deterministic)**
   - Missing ALT text detection
   - Broken link checking
   - Subject line validation
   - Template metadata verification
   - And more...

3. **Agentic LLM Layer (Judgment + Reasoning)**
   - Supervisor Agent (orchestration)
   - Compliance Agent (brand guidelines)
   - Copy/Tone Agent (clarity & tone)
   - Accessibility Agent (WCAG-based review)
   - Risk Scoring Agent
   - Fix Suggestion Agent

## Prerequisites

- Python 3.9+
- Node.js 16+
- Email on Acid API credentials
- OpenAI API key (for LLM agents)

## Setup

### Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. Run the backend:
   ```bash
   python main.py
   ```

### Frontend

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

- `GET /api/v1/emails` - List email proofs
- `GET /api/v1/emails/{id}` - Get email details
- `POST /api/v1/emails/{id}/qa` - Run QA analysis
- `GET /api/v1/reports/{id}` - Get saved report

## Project Structure

```
email-review-agent/
├── backend/
│   ├── agents/              # Multi-agent system
│   ├── api/                 # FastAPI endpoints
│   ├── connectors/          # Email on Acid integration
│   ├── config/              # Configuration files
│   ├── agent_prompts/       # LLM agent prompts
│   ├── deterministic_tests.py # Deterministic QA engine
│   ├── agent_orchestrator.py # Agent coordination
│   ├── main.py             # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile          # Containerization
└── frontend/
    ├── pages/              # Next.js pages
    ├── components/         # React components
    ├── styles/             # CSS and Tailwind
    └── public/             # Static assets
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

This project is licensed under the MIT License.