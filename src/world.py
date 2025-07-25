from src.bible_base import Bible

class WorldEnglishBible(Bible):
    """World English Bible Translation"""
    
    def __init__(self):
        super().__init__("World English Bible")
    
    def load_text(self, file_path: str) -> None:
        """World English bible text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self._parse_world_format(content)
        except Exception as e:
            print(f"Error loading World English Bible from {file_path}: {e}")
    
    def _parse_world_format(self, content: str) -> None:
        """Parse World English Bible specific format"""
        import re
        
        lines = content.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # World English Bible format patterns
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
