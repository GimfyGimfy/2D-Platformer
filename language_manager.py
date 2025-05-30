import json
import os

class LanguageManager:
    def __init__(self):
        self.current_lang = "en"
        self.strings = {}
        self.languages = self.get_available_languages()
        
    def get_available_languages(self):
        languages = {}
        lang_dir = "languages"
        if os.path.exists(lang_dir):
            for file in os.listdir(lang_dir):
                if file.endswith(".json"):
                    lang_code = file.split(".")[0]
                    languages[lang_code] = lang_code
        return languages
        
    def load_languages(self):
        try:
            with open(f"languages/{self.current_lang}.json", "r", encoding="utf-8") as f:
                self.strings = json.load(f)
        except FileNotFoundError:
            print(f"Language file for {self.current_lang} not found! Using English.")
            self.current_lang = "en"
            with open("languages/en.json", "r", encoding="utf-8") as f:
                self.strings = json.load(f)
    
    def set_language(self, lang_code):
        if lang_code in self.languages:
            self.current_lang = lang_code
            self.load_languages()
            return True
        return False

LANG = LanguageManager()