# ============================================
# SillyMD Backend - Development Guide
# ============================================

## Project Status

This is a complete backend system for SillyMD Skills platform with the following components implemented:

### ✅ Completed Modules

1. **User Authentication System**
   - JWT-based authentication
   - User registration and login
   - Role-based access control (user, vendor, admin)
   - Token refresh mechanism

2. **Skills Management System**
   - CRUD operations for skills
   - Skill categories (tech, product, design, marketing, ops)
   - Free vs Commercial skill types
   - Version control support
   - Tag system
   - Digital signatures for commercial skills

3. **AI Review System**
   - Three difficulty levels (easy, medium, hard)
   - Automatic skill approval based on scores
   - Format, safety, and quality checks
   - Review queue management

4. **Crawler System**
   - GitHub repository search
   - Automatic skill creation
   - Fake user generation for crawled content
   - Configurable crawl intervals and limits

5. **Search Service**
   - Meilisearch integration
   - Full-text search
   - Category and type filtering

6. **Cache Service**
   - Redis-based caching
   - Pattern-based invalidation
   - TTL management

### 🔧 Technical Stack

- **FastAPI** - Modern async web framework
- **PostgreSQL** - Primary database with async support
- **Redis** - Caching and message queue
- **Meilisearch** - Fast full-text search
- **Celery** - Background tasks
- **Docker** - Containerization

### 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py          # API dependencies (auth, db)
│   │   └── v1/
│   │       ├── auth.py      # Authentication endpoints
│   │       ├── skills.py    # Skills CRUD endpoints
│   │       └── __init__.py  # API router
│   ├── core/
│   │   ├── config.py        # Configuration
│   │   ├── logging_config.py
│   │   └── security.py      # JWT, hashing, signatures
│   ├── db/
│   │   ├── base.py          # CRUD base class
│   │   └── session.py       # Database session
│   ├── middleware/
│   │   └── rate_limit.py    # Rate limiting
│   ├── models/
│   │   ├── user.py          # User model
│   │   ├── skill.py         # Skill, SkillVersion, Tag models
│   │   └── review.py        # Review model
│   ├── schemas/
│   │   ├── user.py          # User schemas
│   │   └── skill.py         # Skill schemas
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── skill_service.py
│   │   ├── ai_review_service.py
│   │   ├── crawler_service.py
│   │   ├── search_service.py
│   │   └── cache_manager.py
│   ├── tasks/
│   │   ├── celery_app.py    # Celery configuration
│   │   └── review_tasks.py  # Async review tasks
│   └── main.py              # FastAPI application
├── db/
│   └── init/
│       └── 01-init.sql      # Database initialization
├── tests/                   # (to be implemented)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image
├── docker-compose.yml       # Multi-container setup
├── deploy.sh                # Deployment script
├── start.sh                 # Quick start script
└── .env.example             # Environment variables template

```

### 🚀 Quick Start

#### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Start database services
docker-compose up -d postgres redis meilisearch

# Run migrations (if using Alembic)
# alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Docker Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### 📡 API Endpoints

#### Authentication

```
POST /api/v1/auth/register  - Register new user
POST /api/v1/auth/login     - Login user
POST /api/v1/auth/refresh   - Refresh access token
GET  /api/v1/auth/me        - Get current user
```

#### Skills

```
POST   /api/v1/skills        - Create skill (vendor only)
GET    /api/v1/skills        - List skills with filters
GET    /api/v1/skills/{id}   - Get skill detail
PUT    /api/v1/skills/{id}   - Update skill (author/admin)
DELETE /api/v1/skills/{id}   - Delete skill (author/admin)
```

### 🔐 Security Features

- **JWT Authentication** - Secure token-based auth
- **Password Hashing** - bcrypt with salt
- **Rate Limiting** - Prevent abuse
- **CORS Configuration** - Control cross-origin access
- **Digital Signatures** - For commercial skill verification

### 📝 Pending Tasks

- [ ] Complete transaction system (payments, withdrawals)
- [ ] Add comprehensive unit tests
- [ ] Add integration tests
- [ ] Implement team collaboration features
- [ ] Add WebSocket notifications
- [ ] Complete admin panel API
- [ ] Add more crawler sources (Gitee, NPM, PyPI)

### 🏗️ Database Schema

Key tables:
- `users` - User accounts with roles
- `skills` - Main skills table
- `skill_versions` - Skill version history
- `skill_tags` - Many-to-many relationship
- `tags` - Tag definitions
- `reviews` - AI and manual reviews
- `licenses` - Commercial skill licenses
- `point_transactions` - Points system

### 🔧 Configuration

Edit `.env` to configure:

- Database connection
- Redis connection
- JWT secret and expiration
- AI API keys
- Meilisearch URL
- Crawler settings
- Review difficulty

### 📦 Deployment

```bash
# Deploy to server
chmod +x deploy.sh
./deploy.sh
```

The deploy script will:
1. Test SSH connection
2. Create deployment package
3. Upload to server
4. Build and start Docker containers
5. Run database migrations

### 📚 API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
