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

    async def audio_file_to_text(self, file_input):
        """Process audio from a file or UploadFile, converting non-supported formats to wav."""
        import io, asyncio
        from pydub import AudioSegment
        try:
            if asyncio.iscoroutine(file_input):
                file_input = await file_input
            # Obtain file bytes from UploadFile or raw bytes
            if hasattr(file_input, "read"):
                read_func = file_input.read
                if asyncio.iscoroutinefunction(read_func):
                    file_bytes = await read_func()
                else:
                    file_bytes = read_func()
                filename = file_input.filename.lower() if hasattr(file_input, "filename") else ""
                supported_ext = [".wav", ".aiff", ".aifc", ".flac"]
                if filename and not any(filename.endswith(ext) for ext in supported_ext):
                    print("Converting file to wav with PCM codec...")
                    audio_segment = AudioSegment.from_file(io.BytesIO(file_bytes))
                    wav_io = io.BytesIO()
                    # Force conversion to PCM 16-bit little-endian WAV
                    audio_segment.export(wav_io, format="wav", parameters=["-acodec", "pcm_s16le"])
                    wav_io.seek(0)
                    audio_file = sr.AudioFile(wav_io)
                else:
                    audio_file = sr.AudioFile(io.BytesIO(file_bytes))
            elif isinstance(file_input, bytes):
                audio_file = sr.AudioFile(io.BytesIO(file_input))
            else:
                audio_file = sr.AudioFile(file_input)
            with audio_file as source:
                print("Processing audio file...")
                audio = self.recognizer.record(source)
                return await self._process_audio(audio)
        except Exception as e:
            print(f"Error processing audio file: {e}")
            return {"error": f"Audio file processing error: {str(e)}"}