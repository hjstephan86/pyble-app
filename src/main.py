from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
from src.models import VerseResponse, ChapterResponse, BookResponse, BibleListResponse
from src.bible_manager import BibleManager

templates = Jinja2Templates(directory="templates")
bible_manager = BibleManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load bible texts on startup"""
    await bible_manager.load_bibles()
    yield
    print("Shutting down...")

app = FastAPI(
    title="Bible API",
    description="REST API for reading bible texts across different translations",
    version="1.0.0",
    lifespan=lifespan
)

# Web Interface Routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main HTML interface"""
    translations = bible_manager.get_translation_names()
    return templates.TemplateResponse("index.html", {
        "request": request,
        "translations": translations
    })

# API Endpoints
@app.get("/api/translations", response_model=BibleListResponse)
async def list_translations():
    """Get list of available Bible translations"""
    return BibleListResponse(translations=bible_manager.get_translation_names())

@app.get("/api/{translation}/books")
async def get_books(translation: str):
    """Get list of books for a specific translation"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    books = []
    for book_name in bible.get_book_names():
        books.append({
            "name": book_name,
            "chapters": bible.get_chapter_count(book_name)
        })
    
    return {"translation": translation, "books": books}

@app.get("/api/{translation}/{book}")
async def get_book(translation: str, book: str):
    """Get entire book with all chapters and verses"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    book_data = bible.get_book(book)
    if book_data is None:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found in {translation}")
    
    return BookResponse(
        book=book,
        chapters=book_data,
        translation=translation
    )

@app.get("/api/{translation}/{book}/{chapter:int}")
async def get_chapter(translation: str, book: str, chapter: int):
    """Get specific chapter with all verses"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    chapter_data = bible.get_chapter(book, chapter)
    if chapter_data is None:
        raise HTTPException(status_code=404, detail=f"Chapter {chapter} not found in {book} ({translation})")
    
    return ChapterResponse(
        book=book,
        chapter=chapter,
        verses=chapter_data,
        translation=translation
    )

@app.get("/api/{translation}/{book}/{chapter:int}/{verse:int}")
async def get_verse(translation: str, book: str, chapter: int, verse: int):
    """Get specific verse"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    verse_text = bible.get_verse(book, chapter, verse)
    if verse_text is None:
        raise HTTPException(status_code=404, detail=f"Verse {verse} not found in {book} {chapter} ({translation})")
    
    return VerseResponse(
        book=book,
        chapter=chapter,
        verse=verse,
        text=verse_text,
        translation=translation
    )

@app.get("/api/{translation}/{book}/chapters")
async def get_chapter_list(translation: str, book: str):
    """Get list of chapters in a book"""
    bible = bible_manager.get_bible(translation)
    if not bible:
        raise HTTPException(status_code=404, detail=f"Translation '{translation}' not found")
    
    if book not in bible.books:
        raise HTTPException(status_code=404, detail=f"Book '{book}' not found in {translation}")
    
    chapters = []
    for chapter_num in sorted(bible.books[book].keys()):
        chapters.append({
            "chapter": chapter_num,
            "verses": bible.get_verse_count(book, chapter_num)
        })
    
    return {"translation": translation, "book": book, "chapters": chapters}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)