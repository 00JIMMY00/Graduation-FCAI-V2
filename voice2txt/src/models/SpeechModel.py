class SpeechModel:
    def __init__(self, text=None, language=None, translation=None):
       
        self.text = text if text else ""
        self.language = language if language else ""
        self.translation = translation if translation else ""

    async def to_dict(self):
                
        return {
            "text": self.text,
            "language": self.language,
            "translation": self.translation
        }