import speech_recognition as sr

class SpeechService:
    def __init__(self, languages=("ar-EG", "en-US")):
        self.recognizer = sr.Recognizer()
        self.languages = languages

    async def _process_audio(self, audio):
        """Process audio data with multiple language attempts."""
        print("Processing audio input...")
        for language in self.languages:
            try:
                recognized_text = self.recognizer.recognize_google(audio, language=language)
                print(f"Recognized text ({language}): {recognized_text}")
                return {"text": recognized_text}
                    
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
                return {"error": f"Speech recognition service error: {str(e)}"}
            
        print("Sorry, I could not understand the audio in the supported languages.")
        return {"error": "Could not understand the audio"}

    async def voice_to_text(self):
        """Record and process audio from microphone."""
        with sr.Microphone() as source:
            # Removed ambient noise adjustment for immediate start
            print(f"Speak now (Supported languages: {', '.join(self.languages)})...")
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                return await self._process_audio(audio)
            except Exception as e:
                print(f"Error capturing audio: {e}")
                return {"error": f"Audio capture error: {str(e)}"}

    async def audio_file_to_text(self, file_path):
        """Process audio from a file."""
        try:
            with sr.AudioFile(file_path) as source:
                print(f"Processing audio file: {file_path}")
                audio = self.recognizer.record(source)
                return await self._process_audio(audio)
        except Exception as e:
            print(f"Error processing audio file: {e}")
            return {"error": f"Audio file processing error: {str(e)}"}