import speech_recognition as sr

class SpeechService:
    def __init__(self, languages=("ar-EG", "en-US")):
        self.recognizer = sr.Recognizer()
        self.languages = languages

    async def voice_to_text(self):
        with sr.Microphone() as source:
            print("Adjusting for ambient noise... Please wait.")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.25)
            print(f"Speak now (Supported languages: {', '.join(self.languages)})...")

            try:
                # Increase wait time for audio input
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print("Processing your input...")
                for language in self.languages:
                    try:
                        recognized_text = self.recognizer.recognize_google(audio, language=language)
                        print(f"You said ({language}): {recognized_text}")
                        return {"text": recognized_text}
                            
                    except sr.UnknownValueError:
                        continue
                    
                print("Sorry, I could not understand the audio in the supported languages.")
                return {"error": "Could not understand the audio"}
                
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return {"error": f"Speech recognition service error: {str(e)}"}