# models_test.py - Unit tests for models.py

import unittest
from pydantic import ValidationError
from models import (
    BibleVerse, Translation, Testament, BibleVerseCreate,
    BibleVerseResponse, BibleVerseUpdate, BibleBook,
    ChapterResponse, SearchRequest, SearchResult, SearchResponse,
    ErrorResponse, BIBLE_BOOKS_DATA, get_books_by_testament,
    get_book_by_name, get_all_book_names
)

class TestSQLAlchemyModels(unittest.TestCase):

    def test_bible_verse_repr(self):
        """Test __repr__ method of BibleVerse."""
        verse = BibleVerse(book="John", chapter=3, verse=16, text="Test", translation="NIV")
        self.assertEqual(repr(verse), "<BibleVerse(John 3:16)>")

class TestPydanticModels(unittest.TestCase):

    def test_translation_enum(self):
        """Test Translation enum."""
        self.assertEqual(Translation.KJV.value, "KJV")
        self.assertEqual(Translation.NIV.value, "NIV")
        self.assertEqual(Translation.ESV.value, "ESV")
        self.assertEqual(Translation.LUTHER1912.value, "LUTHER1912")
        self.assertEqual(Translation.ELBERFELDER1905.value, "ELBERFELDER1905")

    def test_testament_enum(self):
        """Test Testament enum."""
        self.assertEqual(Testament.OLD.value, "OLD")
        self.assertEqual(Testament.NEW.value, "NEW")

    def test_bible_verse_create_valid(self):
        """Test valid BibleVerseCreate model."""
        data = {
            "book": "Genesis",
            "chapter": 1,
            "verse": 1,
            "text": "In the beginning...",
            "translation": "KJV"
        }
        verse_create = BibleVerseCreate(**data)
        self.assertEqual(verse_create.book, "Genesis")
        self.assertEqual(verse_create.chapter, 1)
        self.assertEqual(verse_create.verse, 1)
        self.assertEqual(verse_create.text, "In the beginning...")
        self.assertEqual(verse_create.translation, Translation.KJV)

    def test_bible_verse_create_invalid_book(self):
        """Test BibleVerseCreate with invalid book length."""
        data = {
            "book": "A" * 51, # Too long
            "chapter": 1,
            "verse": 1,
            "text": "Text",
            "translation": "KJV"
        }
        with self.assertRaises(ValidationError):
            BibleVerseCreate(**data)

    def test_bible_verse_create_invalid_chapter(self):
        """Test BibleVerseCreate with invalid chapter."""
        data = {
            "book": "Genesis",
            "chapter": 0, # Too low
            "verse": 1,
            "text": "Text",
            "translation": "KJV"
        }
        with self.assertRaises(ValidationError):
            BibleVerseCreate(**data)
        
        data["chapter"] = 151 # Too high
        with self.assertRaises(ValidationError):
            BibleVerseCreate(**data)

    def test_bible_verse_create_invalid_verse(self):
        """Test BibleVerseCreate with invalid verse."""
        data = {
            "book": "Genesis",
            "chapter": 1,
            "verse": 0, # Too low
            "text": "Text",
            "translation": "KJV"
        }
        with self.assertRaises(ValidationError):
            BibleVerseCreate(**data)
        
        data["verse"] = 201 # Too high
        with self.assertRaises(ValidationError):
            BibleVerseCreate(**data)

    def test_bible_verse_create_missing_required(self):
        """Test BibleVerseCreate with missing required fields."""
        data = {
            "book": "Genesis",
            "chapter": 1,
            "verse": 1,
            # Missing text
            "translation": "KJV"
        }
        with self.assertRaises(ValidationError):
            BibleVerseCreate(**data)

    def test_bible_verse_response_valid(self):
        """Test valid BibleVerseResponse model."""
        data = {
            "id": 1,
            "book": "John",
            "chapter": 3,
            "verse": 16,
            "text": "For God so loved the world...",
            "translation": "NIV"
        }
        verse_response = BibleVerseResponse(**data)
        self.assertEqual(verse_response.id, 1)
        self.assertEqual(verse_response.book, "John")

    def test_bible_verse_update_valid(self):
        """Test valid BibleVerseUpdate model."""
        data = {"text": "Updated text."}
        update = BibleVerseUpdate(**data)
        self.assertEqual(update.text, "Updated text.")
        self.assertIsNone(update.translation)

        data = {"translation": "ESV"}
        update = BibleVerseUpdate(**data)
        self.assertIsNone(update.text)
        self.assertEqual(update.translation, Translation.ESV)

        data = {"text": "New text", "translation": "LUTHER1912"}
        update = BibleVerseUpdate(**data)
        self.assertEqual(update.text, "New text")
        self.assertEqual(update.translation, Translation.LUTHER1912)

    def test_bible_verse_update_empty(self):
        """Test BibleVerseUpdate with no fields."""
        update = BibleVerseUpdate()
        self.assertIsNone(update.text)
        self.assertIsNone(update.translation)

    def test_bible_book_valid(self):
        """Test valid BibleBook model."""
        data = {
            "name": "Genesis",
            "abbreviation": "Gen",
            "testament": "OLD",
            "chapters": 50
        }
        book = BibleBook(**data)
        self.assertEqual(book.name, "Genesis")
        self.assertEqual(book.testament, Testament.OLD)

    def test_chapter_response_valid(self):
        """Test valid ChapterResponse model."""
        verse_data = {
            "id": 1, "book": "John", "chapter": 3, "verse": 16,
            "text": "Text", "translation": "NIV"
        }
        verse_response = BibleVerseResponse(**verse_data)
        data = {
            "book": "John",
            "chapter": 3,
            "translation": "NIV",
            "verses": [verse_response],
            "verse_count": 1
        }
        chapter_response = ChapterResponse(**data)
        self.assertEqual(chapter_response.book, "John")
        self.assertEqual(chapter_response.verse_count, 1)
        self.assertEqual(chapter_response.verses[0].text, "Text")

    def test_search_request_valid(self):
        """Test valid SearchRequest model."""
        data = {"query": "love"}
        search_req = SearchRequest(**data)
        self.assertEqual(search_req.query, "love")
        self.assertEqual(search_req.translation, Translation.KJV)

    def test_search_request_invalid_query(self):
        """Test SearchRequest with too short query."""
        data = {"query": "lo"} # Too short
        with self.assertRaises(ValidationError):
            SearchRequest(**data)

    def test_search_result_valid(self):
        """Test valid SearchResult model."""
        verse_data = {
            "id": 1, "book": "John", "chapter": 3, "verse": 16,
            "text": "Text", "translation": "NIV"
        }
        verse_response = BibleVerseResponse(**verse_data)
        data = {
            "verse": verse_response,
            "relevance_score": 0.85,
            "context": "Some context..."
        }
        search_result = SearchResult(**data)
        self.assertEqual(search_result.relevance_score, 0.85)
        self.assertEqual(search_result.context, "Some context...")

    def test_search_response_valid(self):
        """Test valid SearchResponse model."""
        verse_data = {
            "id": 1, "book": "John", "chapter": 3, "verse": 16,
            "text": "Text", "translation": "NIV"
        }
        verse_response = BibleVerseResponse(**verse_data)
        search_result_data = {
            "verse": verse_response,
            "relevance_score": 0.85,
            "context": "Some context..."
        }
        search_result = SearchResult(**search_result_data)
        data = {
            "query": "love",
            "translation": "NIV",
            "results": [search_result],
            "total_count": 1,
            "page": 1,
            "per_page": 20,
            "has_next": False,
            "has_prev": False
        }
        search_response = SearchResponse(**data)
        self.assertEqual(search_response.query, "love")
        self.assertEqual(search_response.total_count, 1)

    def test_error_response_valid(self):
        """Test valid ErrorResponse model."""
        data = {
            "error": True,
            "message": "Something went wrong",
            "details": "Detailed error message"
        }
        error_response = ErrorResponse(**data)
        self.assertTrue(error_response.error)
        self.assertEqual(error_response.message, "Something went wrong")

class TestBibleBooksDataAndUtilities(unittest.TestCase):

    def test_bible_books_data_structure(self):
        """Test the structure and content of BIBLE_BOOKS_DATA."""
        self.assertIsInstance(BIBLE_BOOKS_DATA, list)
        self.assertGreater(len(BIBLE_BOOKS_DATA), 0)
        for book in BIBLE_BOOKS_DATA:
            self.assertIsInstance(book, BibleBook)
            self.assertIsInstance(book.name, str)
            self.assertIsInstance(book.abbreviation, str)
            self.assertIsInstance(book.testament, Testament)
            self.assertIsInstance(book.chapters, int)
            self.assertGreater(book.chapters, 0)

    def test_get_books_by_testament(self):
        """Test get_books_by_testament function."""
        old_testament_books = get_books_by_testament(Testament.OLD)
        new_testament_books = get_books_by_testament(Testament.NEW)

        self.assertGreater(len(old_testament_books), 0)
        self.assertGreater(len(new_testament_books), 0)

        for book in old_testament_books:
            self.assertEqual(book.testament, Testament.OLD)
        for book in new_testament_books:
            self.assertEqual(book.testament, Testament.NEW)
        
        # Ensure no overlap
        self.assertEqual(len(old_testament_books) + len(new_testament_books), len(BIBLE_BOOKS_DATA))

    def test_get_book_by_name_found(self):
        """Test get_book_by_name for an existing book (case-insensitive)."""
        genesis = get_book_by_name("Genesis")
        self.assertIsNotNone(genesis)
        self.assertEqual(genesis.name, "Genesis")
        self.assertEqual(genesis.testament, Testament.OLD)
        self.assertEqual(genesis.chapters, 50)

        # Test case-insensitivity
        john_lower = get_book_by_name("john")
        self.assertIsNotNone(john_lower)
        self.assertEqual(john_lower.name, "John")

        romans_mixed = get_book_by_name("RoMaNs")
        self.assertIsNotNone(romans_mixed)
        self.assertEqual(romans_mixed.name, "Romans")

    def test_get_book_by_name_not_found(self):
        """Test get_book_by_name for a non-existing book."""
        non_existent_book = get_book_by_name("NonExistentBook")
        self.assertIsNone(non_existent_book)

    def test_get_all_book_names(self):
        """Test get_all_book_names function."""
        all_names = get_all_book_names()
        self.assertIsInstance(all_names, list)
        self.assertGreater(len(all_names), 0)
        self.assertIn("Genesis", all_names)
        self.assertIn("Revelation", all_names)
        self.assertEqual(len(all_names), len(BIBLE_BOOKS_DATA))
        # Ensure all names are unique
        self.assertEqual(len(set(all_names)), len(all_names))

if __name__ == '__main__':
    unittest.main()
