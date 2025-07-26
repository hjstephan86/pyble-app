from src.bible_base import Bible

class Schlachter1951(Bible):
    """Schlachter 1951 German Bible Translation"""
    
    def __init__(self):
        super().__init__("Schlachter1951")
    
    def load_text(self, file_path: str) -> None:
        """Load Schlachter 1951 text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self._parse_text(content)
        except Exception as e:
            print(f"Error loading Schlachter1951 from {file_path}: {e}")
