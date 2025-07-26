from typing import Dict, List, Optional
from pathlib import Path
from src.bible_base import Bible
from src.elberfelder1905 import Elberfelder1905
from src.world import WorldEnglishBible
from src.schlachter1951 import Schlachter1951

class BibleManager:
    """Manages multiple Bible translations"""
    
    def __init__(self):
        self.bibles: Dict[str, Bible] = {}
    
    async def load_bibles(self, texts_dir: str = "src/texts/"):
        """Load all bible texts from directory"""
        texts_path = Path(texts_dir)
        if not texts_path.exists():
            print(f"Warning: Texts directory {texts_dir} not found")
            return
        
        # Map file patterns to bible classes
        bible_mappings = {
            'elberfelder1905': Elberfelder1905,
            'world': WorldEnglishBible,
            'schlachter1951': Schlachter1951
        }
        
        for file_path in texts_path.glob("*.txt"):
            filename = file_path.stem.lower()
            
            # Try to match filename to known translations
            bible_class = None
            for pattern, cls in bible_mappings.items():
                if pattern in filename:
                    bible_class = cls
                    break
            
            # If no specific class found, skip or use a generic approach
            if bible_class is None:
                print(f"Warning: No specific parser found for {filename}, skipping")
                continue
            
            # Create and load bible
            bible = bible_class()
            bible.load_text(str(file_path))
            
            if bible.books:  # Only add if successfully loaded
                self.bibles[bible.name] = bible
                print(f"Loaded {bible.name} with {len(bible.books)} books")
            else:
                print(f"Warning: No content loaded from {filename}")
    
    def get_bible(self, translation: str) -> Optional[Bible]:
        """Get a specific bible translation"""
        return self.bibles.get(translation)
    
    def get_translation_names(self) -> List[str]:
        """Get list of available translations"""
        return list(self.bibles.keys())
