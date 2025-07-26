from src.bible_base import Bible

class WorldEnglishBible(Bible):
    """World English Bible Translation"""
    
    def __init__(self):
        super().__init__("World English Bible")
    
    def load_text(self, file_path: str) -> None:
        """Load World English Bible text from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                self._parse_text(content)
        except Exception as e:
            print(f"Error loading World English Bible from {file_path}: {e}")
