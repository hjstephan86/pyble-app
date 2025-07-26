from src.bible_base import Bible


class Elberfelder1905(Bible):
    """Elberfelder 1905 German Bible Translation"""

    def __init__(self):
        super().__init__("Elberfelder1905")

    def load_text(self, file_path: str) -> None:
        """Load Elberfelder 1905 text from file"""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self._parse_text(content)
        except Exception as e:
            print(f"Error loading Luther1912 from {file_path}: {e}")
