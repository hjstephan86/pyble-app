import unittest

from bible_base import Bible


class TestBible(Bible):
    """Concrete implementation of Bible for testing"""

    def load_text(self, file_path: str) -> None:
        """Test implementation of load_text"""
        test_content = """0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.
0#1. Mose#1#2#Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.
0#1. Mose#1#3#Und Gott sprach: Es werde Licht! und es ward Licht.
0#1. Mose#1#4#Und Gott sah das Licht, daß es gut war; und Gott schied das Licht von der Finsternis.
0#1. Mose#1#5#Und Gott nannte das Licht Tag, und die Finsternis nannte er Nacht. Und es ward Abend und es ward Morgen: erster Tag.
0#1. Mose#1#6#Und Gott sprach: Es werde eine Ausdehnung inmitten der Wasser, und sie scheide die Wasser von den Wassern!
0#1. Mose#1#7#Und Gott machte die Ausdehnung und schied die Wasser, welche unterhalb der Ausdehnung, von den Wassern, die oberhalb der Ausdehnung sind. Und es ward also.
0#1. Mose#1#8#Und Gott nannte die Ausdehnung Himmel. Und es ward Abend und es ward Morgen: zweiter Tag.
0#1. Mose#1#9#Und Gott sprach: Es sammeln sich die Wasser unterhalb des Himmels an einen Ort, und es werde sichtbar das Trockene! Und es ward also.
0#1. Mose#1#10#Und Gott nannte das Trockene Erde, und die Sammlung der Wasser nannte er Meere. Und Gott sah, daß es gut war.
0#1. Mose#1#11#Und Gott sprach: Die Erde lasse Gras hervorsprossen, Kraut, das Samen hervorbringe, Fruchtbäume, die Frucht tragen nach ihrer Art, in welcher ihr Same sei auf der Erde! Und es ward also."""
        self._parse_text(test_content)


class TestBibleBase(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.bible = TestBible("Test Bible")
        self.bible.load_text("test_path")

    def test_init(self):
        """Test Bible initialization"""
        bible = TestBible("Test Name")
        self.assertEqual(bible.name, "Test Name")
        self.assertEqual(bible.books, {})

    def test_get_verse_valid(self):
        """Test getting a valid verse"""
        verse = self.bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_get_verse_invalid_book(self):
        """Test getting verse from non-existent book"""
        verse = self.bible.get_verse("NonExistent", 1, 1)
        self.assertIsNone(verse)

    def test_get_verse_invalid_chapter(self):
        """Test getting verse from non-existent chapter"""
        verse = self.bible.get_verse("1. Mose", 999, 1)
        self.assertIsNone(verse)

    def test_get_verse_invalid_verse(self):
        """Test getting non-existent verse"""
        verse = self.bible.get_verse("1. Mose", 1, 999)
        self.assertIsNone(verse)

    def test_get_chapter_valid(self):
        """Test getting a valid chapter"""
        chapter = self.bible.get_chapter("1. Mose", 1)
        self.assertIsNotNone(chapter)
        self.assertEqual(len(chapter), 11)  # 11 verses loaded
        self.assertIn(1, chapter)
        self.assertIn(11, chapter)

    def test_get_chapter_invalid_book(self):
        """Test getting chapter from non-existent book"""
        chapter = self.bible.get_chapter("NonExistent", 1)
        self.assertIsNone(chapter)

    def test_get_chapter_invalid_chapter(self):
        """Test getting non-existent chapter"""
        chapter = self.bible.get_chapter("1. Mose", 999)
        self.assertIsNone(chapter)

    def test_get_book_valid(self):
        """Test getting a valid book"""
        book = self.bible.get_book("1. Mose")
        self.assertIsNotNone(book)
        self.assertIn(1, book)  # Chapter 1 exists

    def test_get_book_invalid(self):
        """Test getting non-existent book"""
        book = self.bible.get_book("NonExistent")
        self.assertIsNone(book)

    def test_get_book_names(self):
        """Test getting list of book names"""
        names = self.bible.get_book_names()
        self.assertIn("1. Mose", names)
        self.assertEqual(len(names), 1)

    def test_get_chapter_count_valid(self):
        """Test getting chapter count for valid book"""
        count = self.bible.get_chapter_count("1. Mose")
        self.assertEqual(count, 1)

    def test_get_chapter_count_invalid(self):
        """Test getting chapter count for invalid book"""
        count = self.bible.get_chapter_count("NonExistent")
        self.assertEqual(count, 0)

    def test_get_verse_count_valid(self):
        """Test getting verse count for valid chapter"""
        count = self.bible.get_verse_count("1. Mose", 1)
        self.assertEqual(count, 11)

    def test_get_verse_count_invalid_book(self):
        """Test getting verse count for invalid book"""
        count = self.bible.get_verse_count("NonExistent", 1)
        self.assertEqual(count, 0)

    def test_get_verse_count_invalid_chapter(self):
        """Test getting verse count for invalid chapter"""
        count = self.bible.get_verse_count("1. Mose", 999)
        self.assertEqual(count, 0)

    def test_parse_text_standard_format(self):
        """Test parsing text in standard format"""
        bible = TestBible("Test")
        content = "1. Mose 1:1 Im Anfang schuf Gott die Himmel und die Erde."
        bible._parse_text(content)

        verse = bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_text_alternative_format(self):
        """Test parsing text in alternative format"""
        bible = TestBible("Test")
        content = "1Mos 1:1 Im Anfang schuf Gott die Himmel und die Erde."
        bible._parse_text(content)

        verse = bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_text_hash_format(self):
        """Test parsing text in hash-separated format"""
        bible = TestBible("Test")
        content = "0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde."
        bible._parse_text(content)

        verse = bible.get_verse("1. Mose", 1, 1)
        self.assertEqual(verse, "Im Anfang schuf Gott die Himmel und die Erde.")

    def test_parse_text_empty_lines(self):
        """Test parsing text with empty lines"""
        bible = TestBible("Test")
        content = """
        
0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.

0#1. Mose#1#2#Und die Erde war wüst und leer.

        """
        bible._parse_text(content)

        verse1 = bible.get_verse("1. Mose", 1, 1)
        verse2 = bible.get_verse("1. Mose", 1, 2)
        self.assertEqual(verse1, "Im Anfang schuf Gott die Himmel und die Erde.")
        self.assertEqual(verse2, "Und die Erde war wüst und leer.")

    def test_parse_text_invalid_format(self):
        """Test parsing text with invalid format"""
        bible = TestBible("Test")
        content = "This is not a valid bible verse format"
        bible._parse_text(content)

        # Should not add any books
        self.assertEqual(len(bible.get_book_names()), 0)

    def test_normalize_german_book_name_abbreviations(self):
        """Test normalization of German book name abbreviations"""
        bible = TestBible("Test")

        # Test common abbreviations
        self.assertEqual(bible._normalize_german_book_name("1Mos"), "1. Mose")
        self.assertEqual(bible._normalize_german_book_name("Mt"), "Matthäus")
        self.assertEqual(bible._normalize_german_book_name("Ps"), "Psalmen")
        self.assertEqual(bible._normalize_german_book_name("Offb"), "Offenbarung")

    def test_normalize_german_book_name_full_names(self):
        """Test normalization of full German book names"""
        bible = TestBible("Test")

        # Test full names (should remain unchanged)
        self.assertEqual(bible._normalize_german_book_name("1. Mose"), "1. Mose")
        self.assertEqual(bible._normalize_german_book_name("Matthäus"), "Matthäus")

    def test_normalize_german_book_name_unknown(self):
        """Test normalization of unknown book names"""
        bible = TestBible("Test")

        # Unknown names should remain unchanged
        self.assertEqual(
            bible._normalize_german_book_name("UnknownBook"), "UnknownBook"
        )


if __name__ == "__main__":
    unittest.main()
