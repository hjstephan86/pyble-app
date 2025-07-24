# Python Bible Application 📖

Stop Docker Image\
`sudo docker stop $(sudo docker ps -aq --filter ancestor=pyble-app) && sudo docker rm $(sudo docker ps -aq --filter ancestor=pyble-app)`

Remove Docker Image\
`sudo docker rmi pyble-app`

Build Docker Image\
`sudo docker build -t pyble-app .`

Start Docker Image\
`sudo docker run -p 8080:8080 pyble-app`

A modern Bible application built with **FastAPI** (Python) that follows **Spring Boot architecture patterns**. This application demonstrates how to transform a Java Spring Boot application into a Python equivalent while maintaining the same architectural principles.

## 🌟 Features

- **REST API** with automatic Swagger documentation
- **Single source of truth** for Bible book names from data layer to UI
- **Multiple Bible translations** support
- **Advanced search functionality** with relevance scoring
- **Complete CRUD operations** for Bible verses
- **Web-based user interface** with modern design
- **Spring Boot equivalent patterns** (Controllers, Services, Models, Dependency Injection)
- **Database integration** with SQLAlchemy ORM
- **Pagination and filtering** support
- **Special verse features** (Random verse, Verse of the day)

## 🏗️ Architecture

This application follows **Spring Boot architectural patterns** using Python equivalents:

| Spring Boot | Python FastAPI | Description |
|-------------|----------------|-------------|
| `@SpringBootApplication` | `FastAPI()` app | Application entry point |
| `@RestController` | `APIRouter()` | REST endpoints |
| `@Service` | Service classes | Business logic layer |
| `@Entity` | SQLAlchemy models | Data models |
| `@Autowired` | `Depends()` | Dependency injection |
| `application.properties` | Pydantic Settings | Configuration |
| JPA Repository | SQLAlchemy queries | Data access |
| Maven `pom.xml` | `requirements.txt` | Dependency management |

## 📁 Project Structure

```
pyble-app/
├── src/
│   ├── __init__.py  <-- NEU hinzugefügt
│   ├── main.py
│   ├── controllers.py
│   ├── database.py
│   ├── config.py
│   ├── models.py
│   └── services.py
├── templates/
│   └── index.html
├── Dockerfile
└── ...weitere Dateien
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

```bash
python main.py
```

### 3. Access the Application

- **Web Interface**: http://localhost:8080/
- **API Documentation**: http://localhost:8080/swagger
- **Alternative Docs**: http://localhost:8080/redoc
- **Health Check**: http://localhost:8080/health

## 📊 API Endpoints

### Bible Books (Single Source of Truth)
- `GET /api/v1/books` - Get all Bible books
- `GET /api/v1/books/{testament}` - Get books by testament (OLD/NEW)
- `GET /api/v1/books/info/{book_name}` - Get book information

### Verses (CRUD Operations)
- `GET /api/v1/verse/{book}/{chapter}/{verse}` - Get specific verse
- `POST /api/v1/verse` - Create new verse
- `PUT /api/v1/verse/{verse_id}` - Update verse
- `DELETE /api/v1/verse/{verse_id}` - Delete verse

### Chapters
- `GET /api/v1/chapter/{book}/{chapter}` - Get complete chapter

### Search
- `GET /api/v1/search` - Search Bible text with pagination
- `GET /api/v1/search/reference` - Search by reference (e.g., "John 3:16")

### Special Verses
- `GET /api/v1/verse/random` - Get random verse
- `GET /api/v1/verse/today` - Get verse of the day

### Statistics
- `GET /api/v1/stats` - Database statistics
- `GET /api/v1/translations` - Available translations

## 🔧 Configuration

Configuration is handled through `config.py` using Pydantic Settings (equivalent to Spring Boot's `application.properties`):

```python
# Environment variables or defaults
DATABASE_URL=sqlite:///./bible.db
DEBUG=True
API_V1_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8080
```

### Different Environments

```bash
# Development (default)
ENVIRONMENT=development python main.py

# Production
ENVIRONMENT=production python main.py

# Testing
ENVIRONMENT=test python main.py
```

## 💾 Database

The application uses **SQLite** by default (no setup required), but can be configured for PostgreSQL or MySQL:

### PostgreSQL Setup
```bash
pip install psycopg2-binary
# Set DATABASE_URL=postgresql://user:password@localhost/bible_db
```

### MySQL Setup
```bash
pip install pymysql
# Set DATABASE_URL=mysql+pymysql://user:password@localhost/bible_db
```

### Sample Data

The application automatically creates sample verses for testing. To add your own data, use the POST endpoint:

```bash
curl -X POST "http://localhost:8080/api/v1/verse" \
     -H "Content-Type: application/json" \
     -d '{
       "book": "John",
       "chapter": 3,
       "verse": 16,
       "text": "For God so loved the world...",
       "translation": "NIV"
     }'
```
