from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class Bible(ABC):
    """Abstract base class for Bible translations"""
    
    def __init__(self, name: str):
        self.name = name
        self.books: Dict[str, Dict[int, Dict[int, str]]] = {}
    
    @abstractmethod
    def load_text(self, file_path: str) -> None:
        """Load bible text from file - must be implemented by subclasses"""
        pass
    
    def get_verse(self, book: str, chapter: int, verse: int) -> Optional[str]:
        """Get a specific verse"""
        if book in self.books:
            if chapter in self.books[book]:
                if verse in self.books[book][chapter]:
                    return self.books[book][chapter][verse]
        return None
    
    def get_chapter(self, book: str, chapter: int) -> Optional[Dict[int, str]]:
        """Get all verses in a chapter"""
        if book in self.books:
            if chapter in self.books[book]:
                return self.books[book][chapter]
        return None
    
    def get_book(self, book: str) -> Optional[Dict[int, Dict[int, str]]]:
        """Get all chapters in a book"""
        if book in self.books:
            return self.books[book]
        return None
    
    def get_book_names(self) -> List[str]:
        """Get list of all book names"""
        return list(self.books.keys())
    
    def get_chapter_count(self, book: str) -> int:
        """Get number of chapters in a book"""
        if book in self.books:
            return len(self.books[book])
        return 0
    
    def get_verse_count(self, book: str, chapter: int) -> int:
        """Get number of verses in a chapter"""
        if book in self.books and chapter in self.books[book]:
            return len(self.books[book][chapter])
        return 0
    
    def _parse_standard_format(self, content: str) -> None:
        """Parse standard bible format: 'BookName Chapter:Verse Text'"""
        import re
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to match verse patterns like "Genesis 1:1" or "1. Mose 1:1"
            verse_match = re.match(r'^(.+?)\s+(\d+):(\d+)\s+(.+)$', line)
            if verse_match:
                book_name = verse_match.group(1).strip()
                chapter_num = int(verse_match.group(2))
                verse_num = int(verse_match.group(3))
                verse_text = verse_match.group(4).strip()
                
                # Initialize book if not exists
                if book_name not in self.books:
                    self.books[book_name] = {}
                
                # Initialize chapter if not exists
                if chapter_num not in self.books[book_name]:
                    self.books[book_name][chapter_num] = {}
                
                # Add verse
                self.books[book_name][chapter_num][verse_num] = verse_text