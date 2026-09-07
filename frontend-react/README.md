# ResumeTailor

A full-stack AI-powered resume optimization platform.

## Tech Stack

### Frontend
- **Framework**: React 18
- **Build Tool**: Vite
- **Routing**: React Router v6
- **Styling**: Tailwind CSS v3
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.12)
- **Database**: SQLite (via SQLAlchemy ORM)
- **Authentication**: JWT (JSON Web Tokens) with bcrypt password hashing
- **AI Integration**: OpenAI API (GPT-4)
- **PDF Generation**: Jinja2 templating with `pdflatex` (and a web fallback)

### Architecture Highlights
- Fully responsive Single Page Application (SPA) dashboard layout.
- JWT automatically handled via Axios interceptors.
- Backend uses FastAPI `BackgroundTasks` for automatic cleanup of temporary `.tex` and `.pdf` files.
- Fallback mock logic allowing development testing without active OpenAI API keys.
