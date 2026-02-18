# LuminaLib

LuminaLib is an intelligent library system that manages book files, synthesizes reader sentiment, and provides personalized recommendations using Gen AI or LLM.

---

## Features
- **Authentication**: Secure JWT-based user authentication.
- **Book Management**: Upload, update, and delete book files and metadata.
- **Intelligence**: Summarize book content and analyze user reviews.
- **Recommendations**: Personalized book suggestions based on user preferences.

---

## Prerequisites
- Docker
- Docker Compose

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/ai-dewanand/JKTech-LuminaLib.git
cd JKTech-LuminaLib
```

### 2. Create a `.env` File
Create a `.env` file in the root directory with the following variables:
```
# Database Configuration
DATABASE_URL=postgresql://user:password@db:5432/luminalib

# JWT Configuration
SECRET_KEY=CHANGE_THIS_TO_A_STRONG_RANDOM_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/LLM Configuration (Options = openai,azureai,custom)
AI_MODEL=gpt-4o
LLM_CLIENT=custom
LLM_API_KEY=

# AZURE_OPENAI_API_KEY=
# AZURE_OPENAI_ENDPOINT=
# AZURE_API_VERSION=
# ENABLE_AGENT=

## S3 Configuration
# S3_BUCKET_NAME=
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
```
#### Note: If you want to generate custom LLM API key, you can use: [https://apifreellm.com](https://apifreellm.com)

### 3. Build and Run the Application
```bash
docker-compose up --build
```

### 4. Access the Application
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### Run Test Cases 
```bash
pytest -v
```

## Project Structure
```
LuminaLib-JKTech/
├── ARCHITECTURE.md
├── Dockerfile
├── README.md
├── alembic.ini
├── docker-compose.yml
├── requirements.txt
│
├── alembic/                          # Database migrations
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 87b06190008f_initial_migration.py
│
├── app/
│   ├── main.py                       # FastAPI application entry point
│   │
│   ├── api/v1/                       # API endpoints (v1)
│   │   ├── auth.py
│   │   ├── books.py
│   │   ├── borrow.py
│   │   ├── recommendations.py
│   │   └── reviews.py
│   │
│   ├── core/                         # Core configurations
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── logging.py
│   │   └── security.py
│   │
│   ├── models/                       # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── book.py
│   │   ├── borrow.py
│   │   ├── review.py
│   │   └── user.py
│   │
│   ├── repositories/                 # Data access layer
│   │   ├── borrow_repository.py
│   │   ├── review_repository.py
│   │   └── user_repository.py
│   │
│   ├── schemas/                      # Pydantic schemas
│   │   ├── book_schema.py
│   │   ├── borrow_schema.py
│   │   ├── review_schema.py
│   │   ├── token_schema.py
│   │   └── user_schema.py
│   │
│   ├── services/                     # Business logic layer
│   │   ├── ai_service.py
│   │   ├── auth_service.py
│   │   ├── book_service.py
│   │   ├── borrow_service.py
│   │   ├── recommendation_service.py
│   │   └── review_service.py
│   │
│   └── workers/                      # Background tasks
│       └── tasks.py
│
├── data/
│   └── books/                        # Book data storage
│
├── tests/                            # Test files
```

## Developer Contact Details
Email = ai.dewanand@gmail.com