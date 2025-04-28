import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import os
from PIL import Image, ImageTk
import time

# Color scheme
DARK_BG = "#2D2D2D"
DARKER_BG = "#1E1E1E"
ACCENT_COLOR = "#4CAF50"
TEXT_COLOR = "#FFFFFF"
SECONDARY_TEXT = "#CCCCCC"
SUCCESS_COLOR = "#2196F3"
ERROR_COLOR = "#FF5252"
BUTTON_BG = "#3D3D3D"

class AIAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Nexora AI Assistant")
        self.root.geometry("1000x800")
        self.root.configure(bg=DARK_BG)

        # Create main frame
        self.main_frame = tk.Frame(root, bg=DARK_BG)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create header
        self.header = tk.Label(
            self.main_frame,
            text="Nexora AI Assistant",
            font=("Segoe UI", 32, "bold"),
            bg=DARK_BG,
            fg=ACCENT_COLOR
        )
        self.header.pack(pady=20)

        # Create input frame at the top
        self.input_frame = tk.Frame(self.main_frame, bg=DARK_BG)
        self.input_frame.pack(fill=tk.X, pady=10)

        # Create input field with high visibility
        self.input_field = tk.Entry(
            self.input_frame,
            font=("Segoe UI", 14),
            bg="#FFFFFF",
            fg="#000000",
            insertbackground="#000000",
            selectbackground=ACCENT_COLOR,
            selectforeground="#FFFFFF",
            relief=tk.SUNKEN,
            borderwidth=3,
            width=50
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", self.send_message)

        # Create send button
        self.send_button = tk.Button(
            self.input_frame,
            text="Send",
            font=("Segoe UI", 14, "bold"),
            bg=ACCENT_COLOR,
            fg="#FFFFFF",
            activebackground=SUCCESS_COLOR,
            activeforeground="#FFFFFF",
            relief=tk.RAISED,
            borderwidth=3,
            width=12,
            command=self.send_message
        )
        self.send_button.pack(side=tk.RIGHT)

        # Create control panel
        self.control_frame = tk.Frame(self.main_frame, bg=DARK_BG)
        self.control_frame.pack(fill=tk.X, pady=10)

        # Create mode selection
        self.mode_frame = tk.Frame(self.control_frame, bg=DARK_BG)
        self.mode_frame.pack(side=tk.LEFT, padx=10)

        self.mode_label = tk.Label(
            self.mode_frame,
            text="Input Mode:",
            font=("Segoe UI", 12, "bold"),
            bg=DARK_BG,
            fg=TEXT_COLOR
        )
        self.mode_label.pack(side=tk.LEFT, padx=(0, 10))

        style = ttk.Style()
        style.configure("Custom.TRadiobutton",
                        background=DARK_BG,
                        foreground=TEXT_COLOR,
                        font=("Segoe UI", 12))

        self.mode_var = tk.StringVar(value="keyboard")
        self.keyboard_radio = ttk.Radiobutton(
            self.mode_frame,
            text="Keyboard",
            variable=self.mode_var,
            value="keyboard",
            style="Custom.TRadiobutton",
            command=self.update_mode
        )
        self.keyboard_radio.pack(side=tk.LEFT, padx=10)

        self.voice_radio = ttk.Radiobutton(
            self.mode_frame,
            text="Voice",
            variable=self.mode_var,
            value="voice",
            style="Custom.TRadiobutton",
            command=self.update_mode
        )
        self.voice_radio.pack(side=tk.LEFT, padx=10)

        self.voice_button = tk.Button(
            self.control_frame,
            text="🎤 Start Voice",
            font=("Segoe UI", 12, "bold"),
            bg=BUTTON_BG,
            fg=TEXT_COLOR,
            activebackground=SUCCESS_COLOR,
            activeforeground=TEXT_COLOR,
            relief=tk.RAISED,
            borderwidth=2,
            command=self.toggle_voice_listening
        )
        self.voice_button.pack(side=tk.RIGHT, padx=10)

        # Create chat display area
        self.chat_display = scrolledtext.ScrolledText(
            self.main_frame,
            wrap=tk.WORD,
            width=90,
            height=30,
            font=("Segoe UI", 12),
            bg=DARKER_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            selectbackground=ACCENT_COLOR,
            selectforeground=DARK_BG
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=10)
        self.chat_display.config(state=tk.DISABLED)

        # Create status bar
        self.status_bar = tk.Label(
            self.main_frame,
            text="Ready",
            font=("Segoe UI", 10),
            bg=DARK_BG,
            fg=SECONDARY_TEXT,
            anchor=tk.W
        )
        self.status_bar.pack(fill=tk.X, pady=5)

        # Initialize callbacks
        self.on_send_message = None
        self.on_voice_command = None

        self.voice_thread = None
        self.is_listening = False

        self.update_status("GUI initialized. Ready to use.")

    def set_callbacks(self, on_send_message, on_voice_command):
        self.on_send_message = on_send_message
        self.on_voice_command = on_voice_command

    def update_status(self, message):
        self.status_bar.config(text=message)

    def add_message(self, sender, message):
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"{sender}: ", "sender")
        self.chat_display.tag_config("sender", foreground=ACCENT_COLOR)
        self.chat_display.insert(tk.END, f"{message}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def send_message(self, event=None):
        message = self.input_field.get().strip()
        if message:
            self.input_field.delete(0, tk.END)
            self.add_message("You", message)
            if self.on_send_message:
                threading.Thread(target=self.on_send_message, args=(message,)).start()

    def start_voice_listening(self):
        if not self.is_listening and self.on_voice_command:
            self.is_listening = True
            self.update_status("Listening for voice commands...")
            self.voice_button.config(
                text="🎤 Stop Voice",
                bg=SUCCESS_COLOR,
                activebackground=ERROR_COLOR
            )
            threading.Thread(target=self._voice_listening_loop).start()

    def stop_voice_listening(self):
        self.is_listening = False
        self.update_status("Voice listening stopped.")
        self.voice_button.config(
            text="🎤 Start Voice",
            bg=BUTTON_BG,
            activebackground=SUCCESS_COLOR
        )

    def _voice_listening_loop(self):
        while self.is_listening:
            if self.on_voice_command:
                try:
                    command = self.on_voice_command()
                    if command:
                        self.add_message("You (Voice)", command)
                except Exception as e:
                    print(f"Voice recognition error: {e}")
                    self.update_status(f"Error: {str(e)}")
            time.sleep(0.1)

    def toggle_voice_listening(self):
        if not self.is_listening:
            self.start_voice_listening()
        else:
            self.stop_voice_listening()

    def update_mode(self):
        if self.mode_var.get() == "voice":
            self.start_voice_listening()
        else:
            self.stop_voice_listening()

    def play_gif(self, gif_path):
        # Placeholder for future GIF animation
        pass

def create_gui():
    root = tk.Tk()
    gui = AIAssistantGUI(root)
    return root, gui

def play_gif(gif_path):
    pass
