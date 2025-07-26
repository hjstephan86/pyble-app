# Bible Reader FastAPI Application

A FastAPI web application for reading bible texts across multiple translations with a web interface.

## Project Structure

```
pyble-app/
├── requirements.txt   # Python dependencies
├── src/
│   ├── main.py            # FastAPI application entry point
│   ├── models.py          # Pydantic data models
│   └── bible_base.py      # Abstract bible base class
│   ├── bible_manager.py   # Bible manager class
│   ├── elberfelder1905.py # Elberfelder 1905 German translation
│   ├── schlachter1951.py  # Schlachter 1951 German translation
│   ├── world.py           # World English Bible translation
│   ├── texts/             # Bible text files directory
│   │   ├── elberfelder1905.txt
│   │   ├── schlachter1951.txt
│   │   ├── world.txt
├── templates/
│   ├── index.html         # Web interface
├── static/                # Static files (create if needed)
```

## Bible Translation Classes

- **Elberfelder 1905**: Elberfelder 1905 German Bible translation
- **WorldEnglishBible**: World English Bible (World) translation  
- **Schlachter1951**: Schlachter 1951 German Bible translation

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Create Directory Structure

```bash
mkdir -p src/texts
mkdir -p templates
mkdir -p static
```

### 3. Add Bible Text Files

Place your Bible text files in the `src/texts/` directory:

- `src/texts/elberfelder1905.txt` - Elberfelder 1905 German Bible
- `src/texts/world.txt` - World English Bible
- `src/texts/schlachter1951.txt` - Schlachter 1951 German Bible

**Expected text format:**
```
0#1. Mose#1#1#In the beginning God created the heavens and the earth.
0#1. Mose#1#2#Now the earth was formless and empty. Darkness was on the surface of the deep. God's Spirit was hovering over the surface of the waters.
```

For German translations:
```
0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.
0#1. Mose#1#2#Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.
```

### 4. Run the Application

```bash
python3 -m src.main
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Access the Application

- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc


## Unit Tests and Cyclomatic Complexity

Run unit tests with code coverage
```
python -m pytest tests/ --cov=src
```

Analyze cyclomatic complexity
```
radon cc src/ > cc.txt
```
## Requirements Upgrade

List outdated requirements
```
pip list --outdated
```

Install outdated requirements
```
pip list --outdated | awk 'NR > 2 {print $1}' | xargs pip install --upgrade
```

Freeze all requirements
```
pip freeze > requirements.txt
```

## API Endpoints

### Web Interface
- `GET /` - Main Bible reader interface

### API Endpoints
- `GET /api/translations` - List available translations
- `GET /api/{translation}/books` - Get books for a translation
- `GET /api/{translation}/{book}` - Get entire book
- `GET /api/{translation}/{book}/{chapter}` - Get chapter with verses
- `GET /api/{translation}/{book}/{chapter}/{verse}` - Get specific verse
- `GET /api/{translation}/{book}/chapters` - List chapters in a book

## Features

### Backend Features
- **Modular Design**: Separate modules for each Bible translation
- **Abstract Base Class**: Consistent interface across translations
- **Flexible Parsing**: Each translation can have custom parsing logic
- **FastAPI Integration**: Automatic API documentation with Swagger
- **Error Handling**: Proper HTTP status codes and error messages

### Frontend Features
- **Modern UI**: Beautiful, responsive web interface
- **Translation Selection**: Switch between different Bible translations
- **Book Navigation**: Browse books with chapter counts
- **Chapter Reading**: Read full chapters with verse numbers
- **Chapter Navigation**: Previous/Next chapter buttons
- **Mobile Responsive**: Works on desktop and mobile devices

## Extending the Application

### Adding New Translations

1. Create a new Python file (e.g., `kjv.py`)
2. Inherit from the `Bible` base class
3. Implement the `load_text()` method
4. Add the class to `bible_manager.py` mappings
5. Place the text file in `src/texts/`

Example:
```python
from bible_base import Bible

class KJV(Bible):
    def __init__(self):
        super().__init__("KJV")
    
    def load_text(self, file_path: str) -> None:
        # Custom parsing logic here
        pass
```

### Custom Text Formats

Each Bible class can implement custom parsing logic in the `load_text()` method to handle different text formats, encodings, or structures.

## Data Structure

The application uses a nested hash map structure as requested:

```
bibles: Dict[str, Bible]
├── Bible.books: Dict[str, Dict[int, Dict[int, str]]]
    ├── book_name (str) → chapters
    ├── chapter_number (int) → verses  
    └── verse_number (int) → verse_text (str)
```

## Development

### Running in Development Mode
```bash
uvicorn main:app --reload
```

### Testing API Endpoints
Use the automatic Swagger documentation at `/docs` or tools like curl:

```bash
# Get translations
curl http://localhost:8000/api/translations

# Get books for Luther1912
curl http://localhost:8000/api/Elberfelder1905/books

# Get Genesis chapter 1 from WEB
curl http://localhost:8000/api/WEB/Genesis/1
```