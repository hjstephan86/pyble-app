# models.py - Data Models (JPA Entity equivalent)

from sqlalchemy import Column, Integer, String, Text, Index
from pydantic import BaseModel, Field
from database import Base
from typing import List, Optional
from enum import Enum

# ============================================================================
# SQLAlchemy Models (equivalent to @Entity in Spring Boot)
# ============================================================================

class BibleVerse(Base):
    """
    Bible verse entity - equivalent to @Entity in JPA
    """
    __tablename__ = "bible_verses"
    
    id = Column(Integer, primary_key=True, index=True)
    book = Column(String(50), index=True, nullable=False)
    chapter = Column(Integer, index=True, nullable=False)
    verse = Column(Integer, index=True, nullable=False)
    text = Column(Text, nullable=False)
    translation = Column(String(20), default="KJV", index=True)
    
    # Create composite indexes for efficient queries
    __table_args__ = (
        Index('idx_book_chapter_verse', 'book', 'chapter', 'verse'),
        Index('idx_translation_book', 'translation', 'book'),
    )
    
    def __repr__(self):
        return f"<BibleVerse({self.book} {self.chapter}:{self.verse})>"

# ============================================================================
# Pydantic Models (equivalent to DTOs in Spring Boot)
# ============================================================================

class Translation(str, Enum):
    """Available Bible translations"""
    KJV = "KJV"
    NIV = "NIV"
    ESV = "ESV"
    LUTHER1912 = "LUTHER1912"
    ELBERFELDER1905 = "ELBERFELDER1905"

class Testament(str, Enum):
    """Bible testaments"""
    OLD = "OLD"
    NEW = "NEW"

# Request/Response Models

class BibleVerseCreate(BaseModel):
    """
    DTO for creating a new Bible verse
    Equivalent to @RequestBody in Spring Boot
    """
    book: str = Field(..., min_length=1, max_length=50, description="Bible book name")
    chapter: int = Field(..., ge=1, le=150, description="Chapter number")
    verse: int = Field(..., ge=1, le=200, description="Verse number")
    text: str = Field(..., min_length=1, description="Verse text")
    translation: Translation = Field(default=Translation.KJV, description="Bible translation")
    
    class Config:
        schema_extra = {
            "example": {
                "book": "John",
                "chapter": 3,
                "verse": 16,
                "text": "For God so loved the world...",
                "translation": "NIV"
            }
        }

class BibleVerseResponse(BaseModel):
    """
    DTO for Bible verse response
    Equivalent to ResponseEntity in Spring Boot
    """
    id: int
    book: str
    chapter: int
    verse: int
    text: str
    translation: str
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models
        schema_extra = {
            "example": {
                "id": 1,
                "book": "John",
                "chapter": 3,
                "verse": 16,
                "text": "For God so loved the world that he gave his one and only Son...",
                "translation": "NIV"
            }
        }

class BibleVerseUpdate(BaseModel):
    """DTO for updating a Bible verse"""
    text: Optional[str] = Field(None, min_length=1, description="Updated verse text")
    translation: Optional[Translation] = Field(None, description="Updated translation")

class BibleBook(BaseModel):
    """Bible book information"""
    name: str = Field(..., description="Book name")
    abbreviation: str = Field(..., description="Book abbreviation")
    testament: Testament = Field(..., description="Old or New Testament")
    chapters: int = Field(..., ge=1, description="Number of chapters")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Genesis",
                "abbreviation": "Gen",
                "testament": "OLD",
                "chapters": 50
            }
        }

class ChapterResponse(BaseModel):
    """Response for a complete chapter"""
    book: str
    chapter: int
    translation: str
    verses: List[BibleVerseResponse]
    verse_count: int

class SearchRequest(BaseModel):
    """Search request parameters"""
    query: str = Field(..., min_length=3, description="Search term")
    translation: Optional[Translation] = Field(Translation.KJV, description="Bible translation")
    book: Optional[str] = Field(None, description="Limit search to specific book")
    testament: Optional[Testament] = Field(None, description="Limit search to testament")

class SearchResult(BaseModel):
    """Individual search result"""
    verse: BibleVerseResponse
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    context: Optional[str] = Field(None, description="Context around the match")

class SearchResponse(BaseModel):
    """Search results response"""
    query: str
    translation: str
    results: List[SearchResult]
    total_count: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
    
    class Config:
        schema_extra = {
            "example": {
                "query": "love",
                "translation": "NIV",
                "results": [
                    {
                        "verse": {
                            "id": 1,
                            "book": "John",
                            "chapter": 3,
                            "verse": 16,
                            "text": "For God so loved the world...",
                            "translation": "NIV"
                        },
                        "relevance_score": 0.95,
                        "context": "For God so loved the world that he gave..."
                    }
                ],
                "total_count": 1,
                "page": 1,
                "per_page": 20,
                "has_next": False,
                "has_prev": False
            }
        }

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: bool = True
    message: str
    details: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "error": True,
                "message": "Verse not found",
                "details": "No verse found for John 3:999"
            }
        }

# ============================================================================
# Bible Books Data (Single Source of Truth)
# ============================================================================

BIBLE_BOOKS_DATA = [
    # Old Testament
    BibleBook(name="Genesis", abbreviation="Gen", testament=Testament.OLD, chapters=50),
    BibleBook(name="Exodus", abbreviation="Exo", testament=Testament.OLD, chapters=40),
    BibleBook(name="Leviticus", abbreviation="Lev", testament=Testament.OLD, chapters=27),
    BibleBook(name="Numbers", abbreviation="Num", testament=Testament.OLD, chapters=36),
    BibleBook(name="Deuteronomy", abbreviation="Deu", testament=Testament.OLD, chapters=34),
    BibleBook(name="Joshua", abbreviation="Jos", testament=Testament.OLD, chapters=24),
    BibleBook(name="Judges", abbreviation="Jdg", testament=Testament.OLD, chapters=21),
    BibleBook(name="Ruth", abbreviation="Rut", testament=Testament.OLD, chapters=4),
    BibleBook(name="1 Samuel", abbreviation="1Sa", testament=Testament.OLD, chapters=31),
    BibleBook(name="2 Samuel", abbreviation="2Sa", testament=Testament.OLD, chapters=24),
    BibleBook(name="1 Kings", abbreviation="1Ki", testament=Testament.OLD, chapters=22),
    BibleBook(name="2 Kings", abbreviation="2Ki", testament=Testament.OLD, chapters=25),
    BibleBook(name="1 Chronicles", abbreviation="1Ch", testament=Testament.OLD, chapters=29),
    BibleBook(name="2 Chronicles", abbreviation="2Ch", testament=Testament.OLD, chapters=36),
    BibleBook(name="Ezra", abbreviation="Ezr", testament=Testament.OLD, chapters=10),
    BibleBook(name="Nehemiah", abbreviation="Neh", testament=Testament.OLD, chapters=13),
    BibleBook(name="Esther", abbreviation="Est", testament=Testament.OLD, chapters=10),
    BibleBook(name="Job", abbreviation="Job", testament=Testament.OLD, chapters=42),
    BibleBook(name="Psalm", abbreviation="Psa", testament=Testament.OLD, chapters=150),
    BibleBook(name="Proverbs", abbreviation="Pro", testament=Testament.OLD, chapters=31),
    # New Testament
    BibleBook(name="Matthew", abbreviation="Mat", testament=Testament.NEW, chapters=28),
    BibleBook(name="Mark", abbreviation="Mar", testament=Testament.NEW, chapters=16),
    BibleBook(name="Luke", abbreviation="Luk", testament=Testament.NEW, chapters=24),
    BibleBook(name="John", abbreviation="Joh", testament=Testament.NEW, chapters=21),
    BibleBook(name="Acts", abbreviation="Act", testament=Testament.NEW, chapters=28),
    BibleBook(name="Romans", abbreviation="Rom", testament=Testament.NEW, chapters=16),
    BibleBook(name="1 Corinthians", abbreviation="1Co", testament=Testament.NEW, chapters=16),
    BibleBook(name="2 Corinthians", abbreviation="2Co", testament=Testament.NEW, chapters=13),
    BibleBook(name="Galatians", abbreviation="Gal", testament=Testament.NEW, chapters=6),
    BibleBook(name="Ephesians", abbreviation="Eph", testament=Testament.NEW, chapters=6),
    BibleBook(name="Philippians", abbreviation="Phi", testament=Testament.NEW, chapters=4),
    BibleBook(name="Colossians", abbreviation="Col", testament=Testament.NEW, chapters=4),
    BibleBook(name="1 Thessalonians", abbreviation="1Th", testament=Testament.NEW, chapters=5),
    BibleBook(name="2 Thessalonians", abbreviation="2Th", testament=Testament.NEW, chapters=3),
    BibleBook(name="1 Timothy", abbreviation="1Ti", testament=Testament.NEW, chapters=6),
    BibleBook(name="2 Timothy", abbreviation="2Ti", testament=Testament.NEW, chapters=4),
    BibleBook(name="Titus", abbreviation="Tit", testament=Testament.NEW, chapters=3),
    BibleBook(name="Philemon", abbreviation="Phm", testament=Testament.NEW, chapters=1),
    BibleBook(name="Hebrews", abbreviation="Heb", testament=Testament.NEW, chapters=13),
    BibleBook(name="James", abbreviation="Jam", testament=Testament.NEW, chapters=5),
    BibleBook(name="1 Peter", abbreviation="1Pe", testament=Testament.NEW, chapters=5),
    BibleBook(name="2 Peter", abbreviation="2Pe", testament=Testament.NEW, chapters=3),
    BibleBook(name="1 John", abbreviation="1Jo", testament=Testament.NEW, chapters=5),
    BibleBook(name="2 John", abbreviation="2Jo", testament=Testament.NEW, chapters=1),
    BibleBook(name="3 John", abbreviation="3Jo", testament=Testament.NEW, chapters=1),
    BibleBook(name="Jude", abbreviation="Jud", testament=Testament.NEW, chapters=1),
    BibleBook(name="Revelation", abbreviation="Rev", testament=Testament.NEW, chapters=22),
]

# Utility functions for Bible books
def get_books_by_testament(testament: Testament) -> List[BibleBook]:
    """Get all books from a specific testament"""
    return [book for book in BIBLE_BOOKS_DATA if book.testament == testament]

def get_book_by_name(name: str) -> Optional[BibleBook]:
    """Find a book by name (case-insensitive)"""
    name_lower = name.lower()
    return next((book for book in BIBLE_BOOKS_DATA if book.name.lower() == name_lower), None)

def get_all_book_names() -> List[str]:
    """Get list of all book names"""
    return [book.name for book in BIBLE_BOOKS_DATA]