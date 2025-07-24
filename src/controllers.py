# controllers.py - REST Controllers (@RestController equivalent)

from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from services import BibleService
from models import (
    BibleVerseResponse, BibleVerseCreate, BibleVerseUpdate,
    ChapterResponse, SearchResponse, BibleBook, 
    Translation, Testament, ErrorResponse
)
from config import settings

# Router (equivalent to @RestController in Spring Boot)
bible_router = APIRouter()

# ============================================================================
# Dependency Injection (Spring Boot @Autowired equivalent)
# ============================================================================

def get_bible_service(db: Session = Depends(get_db)) -> BibleService:
    """Dependency injection for BibleService"""
    return BibleService(db)

# ============================================================================
# Bible Books Endpoints
# ============================================================================

@bible_router.get(
    "/books", 
    response_model=List[BibleBook],
    summary="Get all Bible books",
    description="Returns all Bible books with their metadata. Single source of truth from data layer."
)
async def get_all_books(service: BibleService = Depends(get_bible_service)):
    """
    Get all Bible books - @GetMapping equivalent
    Returns the single source of truth for Bible books from the data layer.
    """
    return service.get_all_books()

@bible_router.get(
    "/books/{testament}", 
    response_model=List[BibleBook],
    summary="Get books by testament",
    description="Returns books filtered by Old or New Testament"
)
async def get_books_by_testament(
    testament: Testament = Path(..., description="Testament (OLD or NEW)"),
    service: BibleService = Depends(get_bible_service)
):
    """Get books filtered by testament - @GetMapping with @PathVariable equivalent"""
    return service.get_books_by_testament(testament)

@bible_router.get(
    "/books/info/{book_name}", 
    response_model=BibleBook,
    summary="Get book information",
    description="Get detailed information about a specific Bible book"
)
async def get_book_info(
    book_name: str = Path(..., description="Bible book name", example="Genesis"),
    service: BibleService = Depends(get_bible_service)
):
    """Get information about a specific book"""
    book = service.get_book_info(book_name)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Book '{book_name}' not found"
        )
    return book

# ============================================================================
# Verse Endpoints (CRUD Operations)
# ============================================================================

@bible_router.get(
    "/verse/{book}/{chapter}/{verse}", 
    response_model=BibleVerseResponse,
    summary="Get specific verse",
    description="Get a specific Bible verse by book, chapter, and verse number"
)
async def get_verse(
    book: str = Path(..., description="Bible book name", example="John"),
    chapter: int = Path(..., ge=1, description="Chapter number", example=3),
    verse: int = Path(..., ge=1, description="Verse number", example=16),
    translation: Translation = Query(Translation.KJV, description="Bible translation"),
    service: BibleService = Depends(get_bible_service)
):
    """
    Get specific verse - @GetMapping with @PathVariable equivalent
    Equivalent to Spring Boot: @GetMapping("/verse/{book}/{chapter}/{verse}")
    """
    result = service.get_verse(book, chapter, verse, translation.value)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Verse not found: {book} {chapter}:{verse} ({translation.value})"
        )
    return result

@bible_router.post(
    "/verse", 
    response_model=BibleVerseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new verse",
    description="Create a new Bible verse entry"
)
async def create_verse(
    verse_data: BibleVerseCreate,
    service: BibleService = Depends(get_bible_service)
):
    """
    Create new verse - @PostMapping with @RequestBody equivalent
    Equivalent to Spring Boot: @PostMapping("/verse")
    """
    try:
        return service.create_verse(verse_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@bible_router.put(
    "/verse/{verse_id}", 
    response_model=BibleVerseResponse,
    summary="Update verse",
    description="Update an existing Bible verse"
)
async def update_verse(
    verse_id: int = Path(..., ge=1, description="Verse ID"),
    update_data: BibleVerseUpdate = ...,
    service: BibleService = Depends(get_bible_service)
):
    """Update verse - @PutMapping equivalent"""
    result = service.update_verse(verse_id, update_data)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verse with ID {verse_id} not found"
        )
    return result

@bible_router.delete(
    "/verse/{verse_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete verse",
    description="Delete a Bible verse"
)
async def delete_verse(
    verse_id: int = Path(..., ge=1, description="Verse ID"),
    service: BibleService = Depends(get_bible_service)
):
    """Delete verse - @DeleteMapping equivalent"""
    success = service.delete_verse(verse_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Verse with ID {verse_id} not found"
        )

# ============================================================================
# Chapter Endpoints
# ============================================================================

@bible_router.get(
    "/chapter/{book}/{chapter}", 
    response_model=ChapterResponse,
    summary="Get complete chapter",
    description="Get all verses in a specific chapter"
)
async def get_chapter(
    book: str = Path(..., description="Bible book name", example="John"),
    chapter: int = Path(..., ge=1, description="Chapter number", example=3),
    translation: Translation = Query(Translation.KJV, description="Bible translation"),
    service: BibleService = Depends(get_bible_service)
):
    """
    Get all verses in chapter - @GetMapping equivalent
    Equivalent to Spring Boot: @GetMapping("/chapter/{book}/{chapter}")
    """
    result = service.get_chapter(book, chapter, translation.value)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Chapter not found: {book} {chapter} ({translation.value})"
        )
    return result

# ============================================================================
# Search Endpoints
# ============================================================================

@bible_router.get(
    "/search", 
    response_model=SearchResponse,
    summary="Search Bible text",
    description="Search for specific text in Bible verses with advanced filtering and pagination"
)
async def search_verses(
    q: str = Query(..., min_length=settings.min_search_length, description="Search query", example="love"),
    translation: Translation = Query(Translation.KJV, description="Bible translation"),
    book: Optional[str] = Query(None, description="Limit search to specific book", example="John"),
    testament: Optional[Testament] = Query(None, description="Limit search to testament"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size, description="Results per page"),
    service: BibleService = Depends(get_bible_service)
):
    """
    Search Bible text - @GetMapping with @RequestParam equivalent
    Equivalent to Spring Boot: @GetMapping("/search")
    """
    return service.search_text(
        query=q,
        translation=translation.value,
        book=book,
        testament=testament,
        page=page,
        per_page=per_page
    )

@bible_router.get(
    "/search/reference", 
    response_model=List[BibleVerseResponse],
    summary="Search by Bible reference",
    description="Search by Bible reference (e.g., 'John 3:16' or 'Romans 8:28-30')"
)
async def search_by_reference(
    ref: str = Query(..., description="Bible reference", example="John 3:16"),
    translation: Translation = Query(Translation.KJV, description="Bible translation"),
    service: BibleService = Depends(get_bible_service)
):
    """Search by Bible reference"""
    results = service.search_by_reference(ref, translation.value)
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No verses found for reference: {ref}"
        )
    return results

# ============================================================================
# Special Verse Endpoints
# ============================================================================

@bible_router.get(
    "/verse/random", 
    response_model=BibleVerseResponse,
    summary="Get random verse",
    description="Get a random Bible verse, optionally filtered by testament"
)
async def get_random_verse(
    translation: Translation = Query(Translation.KJV, description="Bible translation"),
    testament: Optional[Testament] = Query(None, description="Limit to testament"),
    service: BibleService = Depends(get_bible_service)
):
    """Get a random Bible verse"""
    result = service.get_random_verse(translation.value, testament)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verses available"
        )
    return result

@bible_router.get(
    "/verse/today", 
    response_model=BibleVerseResponse,
    summary="Get verse of the day",
    description="Get today's verse (deterministic - same verse for the same day)"
)
async def get_verse_of_the_day(
    translation: Translation = Query(Translation.KJV, description="Bible translation"),
    service: BibleService = Depends(get_bible_service)
):
    """Get verse of the day"""
    result = service.get_verse_of_the_day(translation.value)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No verses available"
        )
    return result

# ============================================================================
# Statistics and Info Endpoints
# ============================================================================

@bible_router.get(
    "/stats", 
    summary="Database statistics",
    description="Get database statistics including verse counts by translation"
)
async def get_database_stats(service: BibleService = Depends(get_bible_service)):
    """Get database statistics - similar to Spring Boot Actuator metrics"""
    return service.get_database_stats()

@bible_router.get(
    "/translations", 
    response_model=List[str],
    summary="Available translations",
    description="Get list of available Bible translations in the database"
)
async def get_available_translations(service: BibleService = Depends(get_bible_service)):
    """Get available translations"""
    return service.get_available_translations()

@bible_router.get(
    "/books/available/{translation}", 
    response_model=List[str],
    summary="Books with content",
    description="Get list of books that have content for a specific translation"
)
async def get_books_with_content(
    translation: Translation = Path(..., description="Bible translation"),
    service: BibleService = Depends(get_bible_service)
):
    """Get books that have content in the database"""
    return service.get_books_with_content(translation.value)

# Removed exception handlers from here, as they belong in main.py
