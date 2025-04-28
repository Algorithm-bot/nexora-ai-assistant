import time
import speech_recognition as sr
import os
import webbrowser
import win32com.client
import datetime
import google.generativeai as genai
from config import gemini_api_key
import pyautogui
import psutil
import speedtest
from twilio.rest import Client
from gui import create_gui, play_gif  # Import the GUI module
import pyaudio

# Configure Gemini
genai.configure(api_key=gemini_api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize speaker for speech output
speaker = win32com.client.Dispatch("SAPI.SPvoice")
speaker.Voice = speaker.GetVoices().Item(1)  # Set to female voice
speaker.speak("Welcome to Nexora A I")

# Initialize chat string for logging the conversation
chatStr = ""

def list_microphones():
    """List all available microphones with detailed information"""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    print("\nAvailable Audio Devices:")
    print("=" * 50)
    for i in range(numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        print(f"\nDevice ID: {i}")
        print(f"Name: {device_info.get('name')}")
        print(f"Input Channels: {device_info.get('maxInputChannels')}")
        print(f"Output Channels: {device_info.get('maxOutputChannels')}")
        print(f"Default Sample Rate: {device_info.get('defaultSampleRate')}")
        print(f"Host API: {p.get_host_api_info_by_index(device_info.get('hostApi')).get('name')}")
        print("-" * 50)
    p.terminate()

def get_bluetooth_microphone_index():
    """Find the index of the Bluetooth microphone"""
    p = pyaudio.PyAudio()
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(numdevices):
        device_info = p.get_device_info_by_host_api_device_index(0, i)
        device_name = device_info.get('name').lower()
        # Check for various Bluetooth-related keywords
        if any(keyword in device_name for keyword in ['bluetooth', 'bt', 'wireless', 'headset', 'headphones']):
            print(f"\nFound potential Bluetooth device:")
            print(f"Device ID: {i}")
            print(f"Name: {device_info.get('name')}")
            print(f"Input Channels: {device_info.get('maxInputChannels')}")
            p.terminate()
            return i
    p.terminate()
    return None

# Function to handle chatbot interaction
def chat(query):
    global chatStr
    print(chatStr)
    chatStr += f"Nexora: {query}\n Nexora A.I: "
    
    try:
        response = model.generate_content(query)
        response_text = response.text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        # Fallback response when API fails
        response_text = "I'm sorry, I'm having trouble connecting to my AI service right now. Please try again later or use a different command."
    
    speaker.speak(response_text)
    chatStr += f"{response_text}\n"
    return response_text

# Function to handle AI prompt response
def ai(prompt):
    text = f"Gemini response for Prompt: {prompt} \n *********\n\n"
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text
        print(response_text)
        text += response_text
    except Exception as e:
        print(f"Gemini API Error: {e}")
        response_text = "I'm sorry, I'm having trouble connecting to my AI service right now. Please try again later."
        text += response_text

    # Ensure 'Openai' folder exists
    os.makedirs("Openai", exist_ok=True)
    
    # Save response to a text file
    file_name = "".join(prompt.split("Artificial intelligence")[1:]).strip()
    with open(f"Openai/{file_name}.txt", "w") as f:
        f.write(text)
    
    return response_text

# Function to capture voice command
def takeCommand():
    r = sr.Recognizer()
    
    try:
        # Use default microphone without specifying device index
        with sr.Microphone() as source:
            print("\nAdjusting for ambient noise...")
            r.adjust_for_ambient_noise(source, duration=3)
            
            print("Listening...")
            
            # Increase timeout and phrase time limit
            audio = r.listen(source, timeout=10, phrase_time_limit=10)
            
            print("Recognizing...")
            try:
                query = r.recognize_google(audio, language="en-in")
                print(f"User said: {query}")
                return query.lower()
            except sr.UnknownValueError:
                print("Could not understand audio")
                speaker.speak("I couldn't understand what you said. Please try again.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                speaker.speak("I'm having trouble connecting to the speech recognition service. Please try again.")
                return None
                
    except Exception as e:
        print(f"Error accessing microphone: {e}")
        speaker.speak("Sorry, I'm having trouble accessing the microphone. Please check your microphone settings.")
        return None

# Function to get keyboard input
def getKeyboardInput():
    print("Type your command (or 'exit' to quit):")
    return input().lower()

# Function to process commands
def process_command(query, gui=None):
    """Process a command and return the response"""
    if query is None:
        return "No command received"
        
    response = ""
    
    # Opening specific websites
    sites = {
        "youtube": "https://www.youtube.com",
        "wikipedia": "https://www.wikipedia.com",
        "google": "https://www.google.com",
        "instagram": "https://www.instagram.com"
    }
    
    site_opened = False
    for site, url in sites.items():
        if f"open {site}" in query:
            response = f"Opening {site} sir..."
            speaker.speak(response)
            webbrowser.open(url)
            site_opened = True
            break
            
    # Check the time
    if not site_opened and "the time" in query:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        response = f"Sir, the time is {current_time}"
        speaker.speak(response)
        
    # Handle AI interaction
    elif not site_opened and "using artificial intelligence" in query:
        response = ai(prompt=query)
        speaker.speak(response)
        
    # Play music 
    elif not site_opened and "play music" in query:
        try:
            music_dir = "C:\\Users\\arsla\\Music"
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))
            response = "Playing music"
        except Exception as e:
            response = f"Sorry, I couldn't play music. Error: {e}"
        speaker.speak(response)
        
    # Volume control
    elif not site_opened and "increase volume" in query:
        pyautogui.press("volumeup")
        response = "Increasing the volume sir"
        speaker.speak(response)
    elif not site_opened and "decrease volume" in query:
        pyautogui.press("volumedown")
        response = "Decreasing the volume sir"
        speaker.speak(response)
    elif not site_opened and "mute" in query:
        pyautogui.press("volumemute")
        response = "Now the volume is mute sir"
        speaker.speak(response)
        
    # Open applications
    elif not site_opened and "open visual" in query:
        try:
            response = "Opening Visual Studio Code sir"
            speaker.speak(response)
            os.startfile("C:\\Users\\arsla\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")
        except Exception as e:
            response = f"Sorry, I couldn't open Visual Studio Code. Error: {e}"
            speaker.speak(response)
    elif not site_opened and "open camera" in query:
        try:
            response = "Opening the Camera sir"
            speaker.speak(response)
            os.startfile("C:\\Users\\arsla\\OneDrive\\Desktop\\Camera")
        except Exception as e:
            response = f"Sorry, I couldn't open the camera. Error: {e}"
            speaker.speak(response)
    elif not site_opened and "open profile" in query:
        response = "Enter username to find profile"
        speaker.speak(response)
        username = input("Enter Instagram username: ")
        response = "Opening Instagram profile sir"
        speaker.speak(response)
        webbrowser.open(f"www.instagram.com/{username}")
        
    # Take a screenshot
    elif not site_opened and "take screenshot" in query:
        response = "Sir, please tell me the name for this screenshot file"
        speaker.speak(response)
        name = takeCommand()
        if name:
            response = "Please hold the screen for a few seconds, I am taking the screenshot"
            speaker.speak(response)
            time.sleep(3)
            img = pyautogui.screenshot()
            img.save(f"{name}.png")
            response = "Done, the screenshot is saved in your main folder."
            speaker.speak(response)
        
    # Check battery status
    elif not site_opened and "how much battery we have" in query:
        try:
            battery = psutil.sensors_battery()
            percentage = battery.percent
            response = f"Sir, our system has {percentage}% battery"
        except Exception as e:
            response = f"Sorry, I couldn't check the battery status. Error: {e}"
        speaker.speak(response)
        
    # Default case for chatting
    elif not site_opened:
        response = chat(query)
    
    # Update GUI if available
    if gui:
        gui.add_message("Nexora AI", response)
    
    return response

# Main function to control the flow
if __name__ == '__main__':
    print('Welcome to Nexora A.I')
    
    # Create GUI
    root, gui = create_gui()
    
    # Set up callbacks for the GUI
    def on_send_message(message):
        print(f"Processing message: {message}")
        process_command(message, gui)
    
    def on_voice_command():
        print("Voice button clicked - Starting voice command...")
        try:
            command = takeCommand()
            print(f"Voice command received: {command}")
            if command:
                process_command(command, gui)
            return command
        except Exception as e:
            print(f"Error in voice command: {e}")
            speaker.speak("Sorry, there was an error with the voice command.")
            return None
    
    # Set callbacks with error handling
    try:
        gui.set_callbacks(on_send_message, on_voice_command)
        print("GUI callbacks set successfully")
    except Exception as e:
        print(f"Error setting GUI callbacks: {e}")
    
    # Add welcome message to GUI
    try:
        gui.add_message("Nexora AI", "Welcome to Nexora AI Assistant! How can I help you today?")
        print("Welcome message added to GUI")
    except Exception as e:
        print(f"Error adding welcome message: {e}")
    
    # Start the GUI main loop
    print("Starting GUI main loop...")
    root.mainloop()
