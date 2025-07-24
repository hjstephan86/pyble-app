# services.py - Business Logic (@Service equivalent)

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Tuple
from models import (
    BibleVerse, BibleVerseCreate, BibleVerseResponse, BibleVerseUpdate,
    ChapterResponse, SearchResult, SearchResponse, BibleBook, 
    BIBLE_BOOKS_DATA, Translation, Testament,
    get_books_by_testament, get_book_by_name, get_all_book_names
)
from config import settings

class BibleService:
    """
    Service class for Bible operations (equivalent to @Service in Spring Boot)
    Contains all business logic for Bible verse operations.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    # ========================================================================
    # Book Operations
    # ========================================================================
    
    def get_all_books(self) -> List[BibleBook]:
        """Get all Bible books (single source of truth from data layer)"""
        return BIBLE_BOOKS_DATA
    
    def get_books_by_testament(self, testament: Testament) -> List[BibleBook]:
        """Get books filtered by testament"""
        return get_books_by_testament(testament)
    
    def get_book_info(self, book_name: str) -> Optional[BibleBook]:
        """Get information about a specific book"""
        return get_book_by_name(book_name)
    
    def validate_book_chapter(self, book_name: str, chapter: int) -> bool:
        """Validate if a chapter exists in a book"""
        book = get_book_by_name(book_name)
        if not book:
            return False
        return 1 <= chapter <= book.chapters
    
    # ========================================================================
    # Verse Operations
    # ========================================================================
    
    def get_verse(self, book: str, chapter: int, verse: int, translation: str = "KJV") -> Optional[BibleVerseResponse]:
        """
        Get a specific Bible verse
        Equivalent to a Spring Boot service method with @Transactional
        """
        db_verse = self.db.query(BibleVerse).filter(
            and_(
                func.lower(BibleVerse.book) == book.lower(),
                BibleVerse.chapter == chapter,
                BibleVerse.verse == verse,
                BibleVerse.translation == translation
            )
        ).first()
        
        if db_verse:
            return BibleVerseResponse.from_orm(db_verse)
        return None
    
    def create_verse(self, verse_data: BibleVerseCreate) -> BibleVerseResponse:
        """Create a new Bible verse"""
        # Validate book exists
        if not get_book_by_name(verse_data.book):
            raise ValueError(f"Unknown book: {verse_data.book}")
        
        # Check if verse already exists
        existing = self.db.query(BibleVerse).filter(
            and_(
                func.lower(BibleVerse.book) == verse_data.book.lower(),
                BibleVerse.chapter == verse_data.chapter,
                BibleVerse.verse == verse_data.verse,
                BibleVerse.translation == verse_data.translation
            )
        ).first()
        
        if existing:
            raise ValueError(f"Verse already exists: {verse_data.book} {verse_data.chapter}:{verse_data.verse}")
        
        # Create new verse
        db_verse = BibleVerse(**verse_data.dict())
        self.db.add(db_verse)
        self.db.commit()
        self.db.refresh(db_verse)
        
        return BibleVerseResponse.from_orm(db_verse)
    
    def update_verse(self, verse_id: int, update_data: BibleVerseUpdate) -> Optional[BibleVerseResponse]:
        """Update an existing Bible verse"""
        db_verse = self.db.query(BibleVerse).filter(BibleVerse.id == verse_id).first()
        
        if not db_verse:
            return None
        
        # Update only provided fields
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(db_verse, field, value)
        
        self.db.commit()
        self.db.refresh(db_verse)
        
        return BibleVerseResponse.from_orm(db_verse)
    
    def delete_verse(self, verse_id: int) -> bool:
        """Delete a Bible verse"""
        db_verse = self.db.query(BibleVerse).filter(BibleVerse.id == verse_id).first()
        
        if not db_verse:
            return False
        
        self.db.delete(db_verse)
        self.db.commit()
        return True
    
    # ========================================================================
    # Chapter Operations
    # ========================================================================
    
    def get_chapter(self, book: str, chapter: int, translation: str = "KJV") -> Optional[ChapterResponse]:
        """Get all verses in a chapter"""
        # Validate book and chapter
        if not self.validate_book_chapter(book, chapter):
            return None
        
        db_verses = self.db.query(BibleVerse).filter(
            and_(
                func.lower(BibleVerse.book) == book.lower(),
                BibleVerse.chapter == chapter,
                BibleVerse.translation == translation
            )
        ).order_by(BibleVerse.verse).all()
        
        if not db_verses:
            return None
        
        verses = [BibleVerseResponse.from_orm(verse) for verse in db_verses]
        
        return ChapterResponse(
            book=book,
            chapter=chapter,
            translation=translation,
            verses=verses,
            verse_count=len(verses)
        )
    
    def get_chapter_count(self, book: str, translation: str = "KJV") -> int:
        """Get number of chapters available for a book in a translation"""
        max_chapter = self.db.query(func.max(BibleVerse.chapter)).filter(
            and_(
                func.lower(BibleVerse.book) == book.lower(),
                BibleVerse.translation == translation
            )
        ).scalar()
        
        return max_chapter or 0
    
    # ========================================================================
    # Search Operations
    # ========================================================================
    
    def search_text(self, query: str, translation: str = "KJV", 
                   book: Optional[str] = None, testament: Optional[Testament] = None,
                   page: int = 1, per_page: int = 20) -> SearchResponse:
        """
        Search for text in Bible verses with pagination
        Advanced search with relevance scoring
        """
        # Build base query
        base_query = self.db.query(BibleVerse).filter(
            and_(
                BibleVerse.text.contains(query),
                BibleVerse.translation == translation
            )
        )
        
        # Filter by specific book
        if book:
            base_query = base_query.filter(func.lower(BibleVerse.book) == book.lower())
        
        # Filter by testament
        if testament:
            testament_books = [b.name for b in get_books_by_testament(testament)]
            base_query = base_query.filter(BibleVerse.book.in_(testament_books))
        
        # Get total count
        total_count = base_query.count()
        
        # Calculate pagination
        offset = (page - 1) * per_page
        has_next = total_count > (page * per_page)
        has_prev = page > 1
        
        # Get paginated results with ordering by relevance
        db_verses = base_query.order_by(
            BibleVerse.book, 
            BibleVerse.chapter, 
            BibleVerse.verse
        ).offset(offset).limit(per_page).all()
        
        # Convert to search results with relevance scoring
        results = []
        for verse in db_verses:
            verse_response = BibleVerseResponse.from_orm(verse)
            relevance_score = self._calculate_relevance(verse.text, query)
            context = self._get_search_context(verse.text, query)
            
            results.append(SearchResult(
                verse=verse_response,
                relevance_score=relevance_score,
                context=context
            ))
        
        return SearchResponse(
            query=query,
            translation=translation,
            results=results,
            total_count=total_count,
            page=page,
            per_page=per_page,
            has_next=has_next,
            has_prev=has_prev
        )
    
    def _calculate_relevance(self, text: str, query: str) -> float:
        """Calculate relevance score for search results"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Simple relevance calculation
        word_count = len(text_lower.split())
        query_occurrences = text_lower.count(query_lower)
        
        if query_occurrences == 0:
            return 0.0
        
        # Higher score for more occurrences relative to text length
        relevance = min(1.0, (query_occurrences * 10) / word_count)
        return round(relevance, 2)
    
    def _get_search_context(self, text: str, query: str, context_length: int = 100) -> str:
        """Get context around the search term"""
        text_lower = text.lower()
        query_lower = query.lower()
        
        index = text_lower.find(query_lower)
        if index == -1:
            return text[:context_length] + "..." if len(text) > context_length else text
        
        # Get context around the match
        start = max(0, index - context_length // 2)
        end = min(len(text), index + len(query) + context_length // 2)
        
        context = text[start:end]
        
        # Add ellipsis if truncated
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    # ========================================================================
    # Statistics and Analytics
    # ========================================================================
    
    def get_verse_count(self, translation: str = "KJV", book: Optional[str] = None) -> int:
        """Get total verse count for translation or specific book"""
        query = self.db.query(BibleVerse).filter(BibleVerse.translation == translation)
        
        if book:
            query = query.filter(func.lower(BibleVerse.book) == book.lower())
        
        return query.count()
    
    def get_available_translations(self) -> List[str]:
        """Get list of available translations in the database"""
        translations = self.db.query(BibleVerse.translation).distinct().all()
        return [t[0] for t in translations]
    
    def get_books_with_content(self, translation: str = "KJV") -> List[str]:
        """Get list of books that have content in the database"""
        books = self.db.query(BibleVerse.book).filter(
            BibleVerse.translation == translation
        ).distinct().all()
        return [book[0] for book in books]
    
    def get_database_stats(self) -> dict:
        """Get database statistics"""
        total_verses = self.db.query(BibleVerse).count()
        translations = self.get_available_translations()
        books_with_content = len(self.get_books_with_content())
        
        stats_by_translation = {}
        for translation in translations:
            count = self.get_verse_count(translation)
            stats_by_translation[translation] = count
        
        return {
            "total_verses": total_verses,
            "available_translations": translations,
            "translation_count": len(translations),
            "books_with_content": books_with_content,
            "verses_by_translation": stats_by_translation,
            "total_bible_books": len(BIBLE_BOOKS_DATA)
        }
    
    # ========================================================================
    # Advanced Search Features
    # ========================================================================
    
    def search_by_reference(self, reference: str, translation: str = "KJV") -> List[BibleVerseResponse]:
        """
        Search by Bible reference (e.g., "John 3:16", "Romans 8:28-30")
        Supports single verses and ranges
        """
        try:
            # Parse reference - simplified parser
            if ':' not in reference:
                return []
            
            book_chapter, verse_part = reference.rsplit(':', 1)
            
            # Handle chapter part
            if ' ' in book_chapter:
                book = book_chapter.rsplit(' ', 1)[0].strip()
                chapter = int(book_chapter.rsplit(' ', 1)[1])
            else:
                return []
            
            # Handle verse range
            if '-' in verse_part:
                start_verse, end_verse = verse_part.split('-')
                start_verse = int(start_verse.strip())
                end_verse = int(end_verse.strip())
                
                verses = self.db.query(BibleVerse).filter(
                    and_(
                        func.lower(BibleVerse.book) == book.lower(),
                        BibleVerse.chapter == chapter,
                        BibleVerse.verse >= start_verse,
                        BibleVerse.verse <= end_verse,
                        BibleVerse.translation == translation
                    )
                ).order_by(BibleVerse.verse).all()
            else:
                # Single verse
                verse = int(verse_part.strip())
                verses = self.db.query(BibleVerse).filter(
                    and_(
                        func.lower(BibleVerse.book) == book.lower(),
                        BibleVerse.chapter == chapter,
                        BibleVerse.verse == verse,
                        BibleVerse.translation == translation
                    )
                ).all()
            
            return [BibleVerseResponse.from_orm(v) for v in verses]
        
        except (ValueError, IndexError):
            return []
    
    def get_random_verse(self, translation: str = "KJV", testament: Optional[Testament] = None) -> Optional[BibleVerseResponse]:
        """Get a random Bible verse"""
        query = self.db.query(BibleVerse).filter(BibleVerse.translation == translation)
        
        if testament:
            testament_books = [b.name for b in get_books_by_testament(testament)]
            query = query.filter(BibleVerse.book.in_(testament_books))
        
        # Get random verse
        verse = query.order_by(func.random()).first()
        
        if verse:
            return BibleVerseResponse.from_orm(verse)
        return None
    
    def get_verse_of_the_day(self, translation: str = "KJV") -> Optional[BibleVerseResponse]:
        """
        Get verse of the day (deterministic based on current date)
        Same verse will be returned for the same day
        """
        import datetime
        import hashlib
        
        # Create deterministic seed based on current date
        today = datetime.date.today()
        date_string = today.strftime("%Y-%m-%d")
        seed = int(hashlib.md5(date_string.encode()).hexdigest()[:8], 16)
        
        # Get total verse count
        total_verses = self.get_verse_count(translation)
        if total_verses == 0:
            return None
        
        # Calculate deterministic offset
        offset = seed % total_verses
        
        verse = self.db.query(BibleVerse).filter(
            BibleVerse.translation == translation
        ).offset(offset).first()
        
        if verse:
            return BibleVerseResponse.from_orm(verse)
        return None