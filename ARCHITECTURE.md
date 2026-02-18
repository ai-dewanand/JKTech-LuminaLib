# LuminaLib Architecture

LuminaLib is a containerized FastAPI backend backed by PostgreSQL, with Redis + Celery for asynchronous AI summarization and a lightweight ML-based recommendation engine.

## Runtime Components

### API (FastAPI)
- Entry point: `app/main.py`
- Routers: `app/api/v1/*`
- Authentication: JWT issued on login; all non-auth routers are protected via a global dependency (`verify_token`).

### Database (PostgreSQL + SQLAlchemy)
- SQLAlchemy engine/session: `app/core/database.py` (reads `settings.DATABASE_URL`)
- Models: `app/models/*`
- Migrations: Alembic in `alembic/`

### Queue + Worker (Redis + Celery)
- Celery app and tasks: `app/workers/tasks.py`
- Broker/backend: `redis://redis:6379/0` (as configured in the task module)

### AI/LLM Layer
- LLM integration: `app/services/ai_service.py`
- Used by: Celery task `generate_summary(book_id, content)` to populate `books.summary` asynchronously.

## API Surface (Effective Paths)

Routes are mounted in `app/main.py` with prefixes. The effective paths are:

### Auth (unprotected)
- `POST /auth/signup` - Register a new user
- `POST /auth/login` - Login and receive JWT token
- `POST /auth/signout` - Sign out (invalidate token)

### Books (protected)
Mounted with prefix `/api`.
- `POST /api/books` - Upload book file & metadata (triggers async summary)
- `GET /api/books?skip=0&limit=10` - List books with pagination
- `PUT /api/books/{book_id}` - Update book details
- `DELETE /api/books/{book_id}` - Remove book and associated file
- `POST /api/books/{book_id}/borrow` - User borrows a book
- `POST /api/books/{book_id}/return` - User returns a book
- `POST /api/books/{book_id}/reviews` - Submit review (triggers async sentiment analysis)
- `GET /api/books/{book_id}/analysis` - Get GenAI-aggregated summary of all reviews

### Recommendations (protected)
Mounted with prefix `/recommendations`.
- `GET /recommendations/recommendations?user_id=...` - Get ML-based suggestions

## Core Flows

### 1) Signup/Login and Auth Enforcement
1. Client calls `POST /auth/signup` to create a user.
2. Client calls `POST /auth/login` and receives a JWT access token.
3. For all protected routes, the API expects an `Authorization: Bearer <token>` header.
4. Token validation is performed by `verify_token` (`app/api/v1/auth.py`) using `HTTPBearer` and `jose.jwt.decode`.

### 2) Book Upload + Asynchronous Summarization
1. Client uploads a file + metadata to `POST /api/books`.
2. `BookService.upload_book` (`app/services/book_service.py`):
   - stores the file in s3, if config is avaialble else local path `data/books/` 
   - extracts text from `.pdf` (PyPDF2) or `.docx` (python-docx).
   - enqueues a Celery task: `generate_summary.delay(book_id, extracted_text)`.
3. Celery worker runs `generate_summary` (`app/workers/tasks.py`):
   - calls `AIService.summarize(content)` (async executed via `asyncio.run`).
   - writes the resulting summary back to `books.summary`.

### 3) Borrow and Review
- Borrowing (`app/services/borrow_service.py`):
  - `POST /borrow/borrow` creates a `Borrow` row if the book is not currently borrowed.
  - `POST /borrow/return` marks `returned_at`.
- Reviewing (`app/services/review_service.py`):
  - `POST /reviews/reviews` creates a `Review` only if the user has borrowed the book at least once.

### 4) Recommendations
- Endpoint: `GET /recommendations/recommendations?user_id=...`
- Implementation: `app/services/recommendation_service.py`
  - Sentiment scoring: TextBlob polarity + rating.
  - Similarity: TF-IDF vectorization over `title/author/description/summary` + cosine similarity.
  - Output: ranked list of recommended books with a score and reason.

## Data Model (Current Tables)

Defined in `app/models/*` and created by Alembic migration `alembic/versions/*`.

- `books`: `id`, `title`, `author`, `description`, `file_path`, `summary`
- `users`: `id`, `name`, `email` (unique), `hashed_password`
- `borrows`: `id`, `user_id`, `book_id`, `borrowed_at`, `returned_at`
- `reviews`: `id`, `user_id`, `book_id`, `rating`, `comment`

## AI Service Details (How It Chooses an LLM)

`app/services/ai_service.py` provides `AIService.summarize(text)` via a `LLMAgent` that selects a backend based on environment:

- `LLM_CLIENT=openai`: uses `pydantic_ai` with `OpenAIModel(model, api_key=LLM_API_KEY)`.
- `LLM_CLIENT=azureai`: uses `AsyncAzureOpenAI(azure_endpoint, api_version, api_key)` with `pydantic_ai`.
- Any other value: calls a custom HTTP API (`https://apifreellm.com/api/v1/chat`) with `requests`.

Relevant env/config keys (see `app/core/config.py`):
- `DATABASE_URL`, `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`
- `LLM_CLIENT`, `LLM_API_KEY`
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_API_VERSION`
- `S3_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

Note: `ai_service.py` currently looks for `settings.LLM_MODEL` but `config.py` defines `AI_MODEL`. If you want the model name to be configurable, align these keys.

## Deployment / Local Development

Docker Compose (`docker-compose.yml`) runs:
- `api`: runs Alembic migrations, then starts Uvicorn
- `db`: Postgres
- `redis`: Redis
- `worker`: Celery worker

On startup, the API container command attempts `alembic upgrade head` and may autogenerate an initial migration if none exists.
