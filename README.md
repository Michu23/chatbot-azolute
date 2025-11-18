# Azolute AI Chatbot SaaS Platform

A comprehensive AI-powered chatbot SaaS platform with RAG capabilities, lead generation, and white-label widget embedding.

## Features

- **User Management**: Complete authentication system with JWT, email verification, password reset
- **Onboarding Wizard**: 4-step guided setup for new users
- **Dashboard**: Analytics and insights (conversations, messages, leads, model usage)
- **Bot Management**: Customize appearance, branding, and behavior
- **Conversations**: Full chat history with agent reply capability
- **Lead Management**: Capture and export leads with n8n integrations
- **Knowledge Base**: RAG-powered responses using vector search (pgvector)
- **Embeddable Widget**: Customizable chat widget for any website
- **n8n Integration**: Webhook support for CRM, WhatsApp, email automation

## Tech Stack

### Backend
- **FastAPI** - High-performance Python web framework
- **PostgreSQL** - Database with pgvector extension for RAG
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **JWT** - Authentication
- **OpenAI/Anthropic** - LLM integration
- **LangChain** - RAG pipeline

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Shadcn/ui** - Component library
- **React Query** - Data fetching
- **Zustand** - State management

## Project Structure

```
.
├── backend/          # FastAPI backend
│   ├── app/
│   │   ├── api/     # API routes
│   │   ├── core/    # Config, security, database
│   │   ├── models/  # SQLAlchemy models
│   │   ├── schemas/ # Pydantic schemas
│   │   ├── services/# Business logic
│   │   └── utils/   # Utilities
│   ├── alembic/     # Database migrations
│   └── requirements.txt
│
├── frontend/         # Next.js frontend
│   ├── app/         # App router pages
│   ├── components/  # React components
│   ├── lib/         # Utilities
│   ├── hooks/       # Custom hooks
│   └── types/       # TypeScript types
│
├── widget/          # Embeddable chat widget
│   └── src/
│
└── docker-compose.yml
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+
- Python 3.11+

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd chatbot-azolute
```

2. Set up environment variables
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Start with Docker Compose
```bash
docker-compose up -d
```

4. Run database migrations
```bash
docker-compose exec backend alembic upgrade head
```

5. Access the application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/azolute
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# OpenAI
OPENAI_API_KEY=sk-...

# n8n Webhooks (optional)
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/...
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WIDGET_URL=http://localhost:3000/widget
```

## Database Schema

Key tables:
- `users` - User accounts
- `organizations` - Multi-tenant organizations
- `bots` - Bot configurations
- `chat_sessions` - Conversation sessions
- `chat_messages` - Individual messages
- `leads` - Captured lead information
- `knowledge_sources` - URLs, PDFs, FAQs
- `document_chunks` - Vector embeddings for RAG

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Code Formatting
```bash
# Backend
cd backend
black .
isort .

# Frontend
cd frontend
npm run lint
npm run format
```

## Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for production deployment instructions.

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, please open a GitHub issue or contact support@azolute.com
