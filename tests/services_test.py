# services_test.py - Unit tests for services.py

import unittest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date
import os

from services import BibleService
from models import (
    BibleVerse, BibleVerseCreate, BibleVerseResponse, BibleVerseUpdate,
    ChapterResponse, SearchResult, SearchResponse, BibleBook,
    Translation, Testament, BIBLE_BOOKS_DATA,
    get_books_by_testament, get_book_by_name
)
from config import settings # Import settings for min_search_length

class TestBibleService(unittest.TestCase):

    def setUp(self):
        """Set up a mock database session and BibleService instance."""
        self.mock_db = MagicMock(spec=Session)
        self.service = BibleService(self.mock_db)

        # Mock a sample verse for common use
        self.sample_verse_db = BibleVerse(
            id=1,
            book="John",
            chapter=3,
            verse=16,
            text="For God so loved the world that he gave his son, that whoever believes in him shall not perish but have eternal life.",
            translation="NIV"
        )
        self.sample_verse_response = BibleVerseResponse.from_orm(self.sample_verse_db)

    def tearDown(self):
        """Clean up after each test method"""
        if os.path.exists('bible.db'):
            os.remove('bible.db')

    # ========================================================================
    # Book Operations Tests
    # ========================================================================

    def test_get_all_books(self):
        """Test retrieving all Bible books."""
        books = self.service.get_all_books()
        self.assertEqual(books, BIBLE_BOOKS_DATA)
        self.assertIsInstance(books, list)
        self.assertGreater(len(books), 0)

    def test_get_books_by_testament(self):
        """Test retrieving books filtered by testament."""
        old_testament_books = self.service.get_books_by_testament(Testament.OLD)
        for book in old_testament_books:
            self.assertEqual(book.testament, Testament.OLD)
        self.assertGreater(len(old_testament_books), 0)

        new_testament_books = self.service.get_books_by_testament(Testament.NEW)
        for book in new_testament_books:
            self.assertEqual(book.testament, Testament.NEW)
        self.assertGreater(len(new_testament_books), 0)

    def test_get_book_info_found(self):
        """Test getting info for an existing book."""
        book_info = self.service.get_book_info("Genesis")
        self.assertIsNotNone(book_info)
        self.assertEqual(book_info.name, "Genesis")
        self.assertEqual(book_info.chapters, 50)

    def test_get_book_info_not_found(self):
        """Test getting info for a non-existing book."""
        book_info = self.service.get_book_info("NonExistentBook")
        self.assertIsNone(book_info)

    def test_validate_book_chapter_valid(self):
        """Test validating a valid book and chapter."""
        # Using a known book from BIBLE_BOOKS_DATA
        self.assertTrue(self.service.validate_book_chapter("Genesis", 1))
        self.assertTrue(self.service.validate_book_chapter("Genesis", 50))
        self.assertTrue(self.service.validate_book_chapter("John", 1))
        self.assertTrue(self.service.validate_book_chapter("John", 21))

    def test_validate_book_chapter_invalid_book(self):
        """Test validating an invalid book."""
        self.assertFalse(self.service.validate_book_chapter("NonExistentBook", 1))

    def test_validate_book_chapter_invalid_chapter(self):
        """Test validating an invalid chapter number."""
        self.assertFalse(self.service.validate_book_chapter("Genesis", 0)) # Chapter too low
        self.assertFalse(self.service.validate_book_chapter("Genesis", 51)) # Chapter too high

    # ========================================================================
    # Verse Operations Tests
    # ========================================================================

    def test_get_verse_found(self):
        """Test retrieving an existing verse."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_verse_db
        
        verse = self.service.get_verse("John", 3, 16, "NIV")
        self.assertIsNotNone(verse)
        self.assertEqual(verse.book, "John")
        self.assertEqual(verse.chapter, 3)
        self.assertEqual(verse.verse, 16)
        self.assertEqual(verse.translation, "NIV")
        self.mock_db.query.assert_called_once()

    def test_get_verse_not_found(self):
        """Test retrieving a non-existing verse."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        verse = self.service.get_verse("John", 3, 99, "NIV")
        self.assertIsNone(verse)
        self.mock_db.query.assert_called_once()

    def test_update_verse_success(self):
        """Test updating an existing verse successfully."""
        update_data = BibleVerseUpdate(text="Updated verse text.", translation="ESV")
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_verse_db
        self.mock_db.refresh.return_value = None

        updated_verse = self.service.update_verse(1, update_data)
        
        self.assertIsNotNone(updated_verse)
        self.assertEqual(updated_verse.text, "Updated verse text.")
        self.assertEqual(updated_verse.translation, "ESV")
        self.mock_db.commit.assert_called_once()
        self.mock_db.refresh.assert_called_once_with(self.sample_verse_db)

    def test_update_verse_not_found(self):
        """Test updating a non-existing verse."""
        update_data = BibleVerseUpdate(text="Updated verse text.")
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        updated_verse = self.service.update_verse(999, update_data)
        
        self.assertIsNone(updated_verse)
        self.mock_db.commit.assert_not_called()

    def test_delete_verse_success(self):
        """Test deleting an existing verse successfully."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = self.sample_verse_db
        
        success = self.service.delete_verse(1)
        
        self.assertTrue(success)
        self.mock_db.delete.assert_called_once_with(self.sample_verse_db)
        self.mock_db.commit.assert_called_once()

    def test_delete_verse_not_found(self):
        """Test deleting a non-existing verse."""
        self.mock_db.query.return_value.filter.return_value.first.return_value = None
        
        success = self.service.delete_verse(999)
        
        self.assertFalse(success)
        self.mock_db.delete.assert_not_called()
        self.mock_db.commit.assert_not_called()

    # ========================================================================
    # Chapter Operations Tests
    # ========================================================================

    def test_get_chapter_count(self):
        """Test getting the count of chapters for a book."""
        self.mock_db.query.return_value.filter.return_value.scalar.return_value = 21 # Max chapter for John
        
        count = self.service.get_chapter_count("John", "NIV")
        self.assertEqual(count, 21)
        self.mock_db.query.assert_called_once()

    def test_get_chapter_count_no_chapters(self):
        """Test getting chapter count for a book with no chapters."""
        self.mock_db.query.return_value.filter.return_value.scalar.return_value = None
        
        count = self.service.get_chapter_count("UnknownBook", "NIV")
        self.assertEqual(count, 0)

    # ========================================================================
    # Search Operations Tests
    # ========================================================================

    def test_search_text_basic(self):
        """Test basic text search with pagination."""
        self.mock_db.query.return_value.filter.return_value.count.return_value = 1
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self.sample_verse_db]

        search_response = self.service.search_text(query="loved", translation="NIV")
        
        self.assertIsNotNone(search_response)
        self.assertEqual(search_response.query, "loved")
        self.assertEqual(search_response.total_count, 1)
        self.assertEqual(len(search_response.results), 1)
        self.assertEqual(search_response.results[0].verse.text, self.sample_verse_db.text)
        self.assertFalse(search_response.has_next)
        self.assertFalse(search_response.has_prev)

    def test_search_text_with_book_filter(self):
        """Test text search filtered by book."""
        self.mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 1
        self.mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self.sample_verse_db]

        search_response = self.service.search_text(query="loved", translation="NIV", book="John")
        self.assertEqual(search_response.total_count, 1)
        self.assertEqual(search_response.results[0].verse.book, "John")

    def test_search_text_pagination(self):
        """Test search pagination logic."""
        # Mock 25 verses, request page 2, per_page 20
        mock_verses = [BibleVerse(id=i, book="Gen", chapter=1, verse=i, text=f"text {i}", translation="KJV") for i in range(1, 26)]
        
        self.mock_db.query.return_value.filter.return_value.count.return_value = 25
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_verses[20:25] # Should return last 5

        search_response = self.service.search_text(query="text", translation="KJV", page=2, per_page=20)
        
        self.assertEqual(search_response.total_count, 25)
        self.assertEqual(search_response.page, 2)
        self.assertEqual(search_response.per_page, 20)
        self.assertEqual(len(search_response.results), 5)
        self.assertFalse(search_response.has_next) # 25 verses total, 20 on page 1, 5 on page 2, no more
        self.assertTrue(search_response.has_prev)

    # ========================================================================
    # Statistics and Analytics Tests
    # ========================================================================

    def test_get_verse_count(self):
        """Test getting total verse count."""
        self.mock_db.query.return_value.filter.return_value.count.return_value = 100
        count = self.service.get_verse_count("NIV")
        self.assertEqual(count, 100)

        self.mock_db.query.return_value.filter.return_value.filter.return_value.count.return_value = 50
        count = self.service.get_verse_count("NIV", "John")
        self.assertEqual(count, 50)

    def test_get_available_translations(self):
        """Test getting available translations."""
        self.mock_db.query.return_value.distinct.return_value.all.return_value = [("NIV",), ("KJV",)]
        translations = self.service.get_available_translations()
        self.assertEqual(translations, ["NIV", "KJV"])

    def test_get_books_with_content(self):
        """Test getting books with content for a translation."""
        self.mock_db.query.return_value.filter.return_value.distinct.return_value.all.return_value = [("John",), ("Genesis",)]
        books = self.service.get_books_with_content("NIV")
        self.assertEqual(books, ["John", "Genesis"])

    # ========================================================================
    # Advanced Search Features Tests
    # ========================================================================

    def test_search_by_reference_single_verse(self):
        """Test searching by a single Bible reference."""
        self.mock_db.query.return_value.filter.return_value.all.return_value = [self.sample_verse_db]
        
        results = self.service.search_by_reference("John 3:16", "NIV")
        
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].book, "John")
        self.assertEqual(results[0].verse, 16)

    def test_search_by_reference_verse_range(self):
        """Test searching by a Bible reference range."""
        verse1 = BibleVerse(id=1, book="John", chapter=3, verse=16, text="V16", translation="NIV")
        verse2 = BibleVerse(id=2, book="John", chapter=3, verse=17, text="V17", translation="NIV")
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [verse1, verse2]
        
        results = self.service.search_by_reference("John 3:16-17", "NIV")
        
        self.assertIsNotNone(results)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].verse, 16)
        self.assertEqual(results[1].verse, 17)

    def test_search_by_reference_invalid_format(self):
        """Test searching by an invalid Bible reference format."""
        results = self.service.search_by_reference("Invalid Reference", "NIV")
        self.assertEqual(len(results), 0)
        self.mock_db.query.assert_not_called()

        results = self.service.search_by_reference("John 3", "NIV") # Missing verse
        self.assertEqual(len(results), 0)
        self.mock_db.query.assert_not_called()

        results = self.service.search_by_reference("John:16", "NIV") # Missing chapter
        self.assertEqual(len(results), 0)
        self.mock_db.query.assert_not_called()

    def test_search_by_reference_no_results(self):
        """Test searching by reference with no matching verses."""
        self.mock_db.query.return_value.filter.return_value.all.return_value = []
        
        results = self.service.search_by_reference("John 3:999", "NIV")
        self.assertEqual(len(results), 0)

    def test_get_random_verse_found(self):
        """Test getting a random verse."""
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = self.sample_verse_db
        
        verse = self.service.get_random_verse("NIV")
        self.assertIsNotNone(verse)
        self.assertEqual(verse.book, "John")
        self.mock_db.query.assert_called_once()

    def test_get_random_verse_filtered_by_testament(self):
        """Test getting a random verse filtered by testament."""
        self.mock_db.query.return_value.filter.return_value.filter.return_value.order_by.return_value.first.return_value = self.sample_verse_db
        
        verse = self.service.get_random_verse("NIV", Testament.NEW)
        self.assertIsNotNone(verse)
        self.assertEqual(verse.book, "John") # John is New Testament
        self.mock_db.query.assert_called_once()

    def test_get_random_verse_no_verses(self):
        """Test getting a random verse when no verses are available."""
        self.mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None
        
        verse = self.service.get_random_verse("NIV")
        self.assertIsNone(verse)

if __name__ == '__main__':
    unittest.main()
