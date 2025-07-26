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
    
    def _parse_text(self, content: str) -> None:
        """Parse Elberfelder 1905 specific format"""
        import re
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Text format might use German book names like "1. Mose", "2. Mose", etc.
            patterns = [
                # Standard format: "1. Mose 1:1 Am Anfang schuf Gott..."
                r'^(.+?)\s+(\d+):(\d+)\s+(.+)$',
                # Alternative format with book numbers: "1Mos 1:1 Am Anfang..."
                r'^(\w+)\s+(\d+):(\d+)\s+(.+)$',
                # Alternative format: "0#1. Mose#1#1#Am Anfang schuf Gott..."
                r'^\d+#(.+?)#(\d+)#(\d+)#(.+)$'
            ]
            
            verse_match = None
            for pattern in patterns:
                verse_match = re.match(pattern, line)
                if verse_match:
                    break
            
            if verse_match:
                book_name = self._normalize_german_book_name(verse_match.group(1).strip())
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
    
    def _normalize_german_book_name(self, book_name: str) -> str:
        """Normalize German book names to consistent format"""
        # Common German book name mappings
        name_mappings = {
            "1Mos": "1. Mose",
            "2Mos": "2. Mose", 
            "3Mos": "3. Mose",
            "4Mos": "4. Mose",
            "5Mos": "5. Mose",
            "Jos": "Josua",
            "Ri": "Richter",
            "Ruth": "Ruth",
            "1Sam": "1. Samuel",
            "2Sam": "2. Samuel",
            "1Kön": "1. Könige",
            "2Kön": "2. Könige",
            "1Chr": "1. Chronik",
            "2Chr": "2. Chronik",
            "Esr": "Esra",
            "Neh": "Nehemia",
            "Est": "Ester",
            "Hi": "Hiob",
            "Ps": "Psalmen",
            "Spr": "Sprüche",
            "Pred": "Prediger",
            "Hld": "Hohelied",
            "Jes": "Jesaja",
            "Jer": "Jeremia",
            "Kla": "Klagelieder",
            "Hes": "Hesekiel",
            "Dan": "Daniel",
            "Hos": "Hosea",
            "Joe": "Joel",
            "Am": "Amos",
            "Ob": "Obadja",
            "Jon": "Jona",
            "Mi": "Micha",
            "Nah": "Nahum",
            "Hab": "Habakuk",
            "Zef": "Zefanja",
            "Hag": "Haggai",
            "Sach": "Sacharja",
            "Mal": "Maleachi",
            "Mt": "Matthäus",
            "Mk": "Markus",
            "Lk": "Lukas",
            "Joh": "Johannes",
            "Apg": "Apostelgeschichte",
            "Röm": "Römer",
            "1Kor": "1. Korinther",
            "2Kor": "2. Korinther",
            "Gal": "Galater",
            "Eph": "Epheser",
            "Phil": "Philipper",
            "Kol": "Kolosser",
            "1Thess": "1. Thessalonicher",
            "2Thess": "2. Thessalonicher",
            "1Tim": "1. Timotheus",
            "2Tim": "2. Timotheus",
            "Tit": "Titus",
            "Phlm": "Philemon",
            "Hebr": "Hebräer",
            "Jak": "Jakobus",
            "1Petr": "1. Petrus",
            "2Petr": "2. Petrus",
            "1Joh": "1. Johannes",
            "2Joh": "2. Johannes",
            "3Joh": "3. Johannes",
            "Jud": "Judas",
            "Offb": "Offenbarung"
        }
        
        return name_mappings.get(book_name, book_name)