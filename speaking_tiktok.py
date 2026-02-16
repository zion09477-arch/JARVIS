from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
import pyttsx3
import datetime
import os
from pydub import AudioSegment
import tempfile

app = Flask(__name__)

class WebJARVIS:
    def __init__(self):
        # Note: pyttsx3 won't work on Vercel (no audio output)
        # We'll handle speech on the client side instead
        pass
    
    def process_command(self, command):
        response = ""
        
        if 'time' in command:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The time is {current_time}"
        elif 'date' in command:
            current_date = datetime.datetime.now().strftime("%B %d, %Y")
            response = f"Today is {current_date}"
        elif 'hello' in command or 'hi' in command:
            response = "Hello! How can I help you today?"
        elif 'joke' in command:
            response = "Why don't scientists trust atoms? Because they make up everything!"
        elif 'open youtube' in command:
            # This will return a command for the frontend to execute
            response = "OPEN_YOUTUBE"
        elif 'bye' in command:
            response = "Goodbye! Have a great day!"
        else:
            response = f"You said: '{command}'"
        
        return response

jarvis = WebJARVIS()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process_audio', methods=['POST'])
def process_audio():
    temp_files = []
    
    try:
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file received'})
        
        audio_file = request.files['audio']
        
        # Save temporarily
        temp_webm = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        audio_file.save(temp_webm.name)
        temp_files.append(temp_webm.name)
        
        # Convert to WAV
        temp_wav = tempfile.NamedTemporaryFile(delete=False, suffix='.wav').name
        temp_files.append(temp_wav)
        
        audio = AudioSegment.from_file(temp_webm.name, format="webm")
        audio.export(temp_wav, format="wav")
        
        # Recognize speech
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_wav) as source:
            audio_data = recognizer.record(source)
            command = recognizer.recognize_google(audio_data)
        
        # Process command
        response = jarvis.process_command(command.lower())
        
        return jsonify({
            'success': True,
            'command': command,
            'response': response
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    finally:
        for file_path in temp_files:
            try:
                os.unlink(file_path)
            except:
                pass

# This is important for Vercel
app = app

if __name__ == '__main__':
    app.run(debug=True)