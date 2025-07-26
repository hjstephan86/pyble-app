import unittest
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import tempfile
import os
from bible_manager import BibleManager
from elberfelder1905 import Elberfelder1905


class TestBibleManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.manager = BibleManager()
        self.sample_content = """0#1. Mose#1#1#Im Anfang schuf Gott die Himmel und die Erde.
0#1. Mose#1#2#Und die Erde war wüst und leer, und Finsternis war über der Tiefe; und der Geist Gottes schwebte über den Wassern.
0#1. Mose#1#3#Und Gott sprach: Es werde Licht! und es ward Licht."""
    
    def test_init(self):
        """Test BibleManager initialization"""
        self.assertEqual(self.manager.bibles, {})
        self.assertIsInstance(self.manager.bibles, dict)
    
    def test_load_bibles_directory_not_exists(self):
        """Test loading bibles when directory doesn't exist"""
        with patch('builtins.print') as mock_print:
            self.manager.load_bibles("non_existent_directory")
            mock_print.assert_called_once_with("Warning: Texts directory non_existent_directory not found")
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_bibles_no_files(self, mock_glob, mock_exists):
        """Test loading bibles when no txt files exist"""
        mock_exists.return_value = True
        mock_glob.return_value = []
        
        self.manager.load_bibles("test_dir")
        self.assertEqual(len(self.manager.bibles), 0)
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.glob')
    def test_load_bibles_unknown_format(self, mock_glob, mock_exists):
        """Test loading bible with unknown format"""
        mock_exists.return_value = True
        
        # Mock file path with unknown format
        mock_file_path = MagicMock()
        mock_file_path.stem = "unknown_bible_format"
        mock_glob.return_value = [mock_file_path]
        
        with patch('builtins.print') as mock_print:
            self.manager.load_bibles("test_dir")
            
            # Should print warning about unknown format
            mock_print.assert_called_once_with("Warning: No specific parser found for unknown_bible_format, skipping")
            
            # No bibles should be loaded
            self.assertEqual(len(self.manager.bibles), 0)
    
    def test_get_bible_existing(self):
        """Test getting existing bible translation"""
        # Add a mock bible
        mock_bible = MagicMock()
        self.manager.bibles["TestBible"] = mock_bible
        
        result = self.manager.get_bible("TestBible")
        self.assertEqual(result, mock_bible)
    
    def test_get_bible_non_existing(self):
        """Test getting non-existing bible translation"""
        result = self.manager.get_bible("NonExistentBible")
        self.assertIsNone(result)
    
    def test_get_translation_names_empty(self):
        """Test getting translation names when no bibles loaded"""
        names = self.manager.get_translation_names()
        self.assertEqual(names, [])
    
    def test_get_translation_names_with_bibles(self):
        """Test getting translation names with loaded bibles"""
        # Add mock bibles
        self.manager.bibles["Bible1"] = MagicMock()
        self.manager.bibles["Bible2"] = MagicMock()
        self.manager.bibles["Bible3"] = MagicMock()
        
        names = self.manager.get_translation_names()
        self.assertEqual(len(names), 3)
        self.assertIn("Bible1", names)
        self.assertIn("Bible2", names)
        self.assertIn("Bible3", names)
    
    def test_load_bibles_with_real_temp_files(self):
        """Test loading bibles with real temporary files"""
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test file
            test_file = os.path.join(temp_dir, "elberfelder1905_test.txt")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(self.sample_content)
            
            # Load bibles
            with patch('builtins.print'):
                self.manager.load_bibles(temp_dir)
            
            # Verify bible was loaded
            self.assertEqual(len(self.manager.bibles), 1)
            self.assertIn("Elberfelder1905", self.manager.bibles)

if __name__ == '__main__':
    unittest.main()