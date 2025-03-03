from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.lang import Builder
from languages import *
from googletrans import Translator
import speech_recognition as sr
from kivy.graphics import Color, RoundedRectangle


import threading
from kivy.clock import Clock
import pyttsx3

from kivy.config import Config
Config.set('modules', 'touchring', '0')


import asyncio

#for creating the audio output in the file itself.
# from gtts import gTTS
# import os
# import time
# from playsound import playsound

#For audio playing from os without blocking.

# from deep_translator import GoogleTranslator
# from kivy.core.audio import SoundLoader


class RoundedButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)  
        with self.canvas.before:
            Color(rgba=(0.2, 0.6, 0.8, 1))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[18])

        self.bind(pos=self.update_graphics, size=self.update_graphics)

    def update_graphics(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size



class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.setup_ui()

    def setup_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
       
        title = Label(
            text="SEAMLESS\nTRANSLATOR", 
            font_size='40sp',
            font_name = "Yesteryear-Regular.ttf",
            halign='center',
            size_hint_y=0.2
        )
        
       
        buttons_layout = GridLayout(cols=2, spacing=10, size_hint_y=None, height=100)
        buttons_layout.bind(minimum_height=buttons_layout.setter('height'))
        
        
        buttons_layout.pos_hint = {'center_x': 0.5, 'y': 0} 
        
        modes = [
            ("Text to Text", "t2t"),
            ("Text to Speech", "t2s"),
            ("Speech to Text", "s2t"),
            ("Speech to Speech", "s2s")
        ]
        
        
        for i, (mode_text, mode_id) in enumerate(modes):
            btn = Button(
                text=mode_text,
                size=(180, 40),
                size_hint=(None, None),
                pos=(100 + (i % 2) * 100, 300 - (i // 2) * 50),
                background_color=(0.2, 0.6, 0.8, 1),
                on_press=lambda x, m=mode_id: self.switch_screen(m)
            )
            buttons_layout.add_widget(btn)

        main_layout.add_widget(title)
        main_layout.add_widget(buttons_layout)
        self.add_widget(main_layout)

    def switch_screen(self, mode):
        self.manager.current = mode

class TextToTextScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = Translator()
        with self.canvas.before:
            Color(rgba=(0.0, 0.15, 0.0, 1))  
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)
        self.setup_ui()

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        header = BoxLayout(size_hint_y=0.06, spacing=5)
        back_btn = RoundedButton(
            text='Back',
            size_hint=(0.3,0.8),
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.go_back
        )
        title = Label(text='Text-To-Text Translation', font_size='25sp',font_name = 'Yesteryear-Regular.ttf')
        header.add_widget(back_btn)
        header.add_widget(title)
        
      
        lang_select = BoxLayout(size_hint_y=0.12, spacing=5)
        self.input_button = RoundedButton(
            text='Input Language',
            size_hint=(0.3,0.5),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        swap_btn = RoundedButton(
            text='<---->',
            size_hint=(0.1,0.5),
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.swap_languages
        )
        self.output_button = RoundedButton(
            text='Target Language',
            size_hint=(0.3,0.5),
            background_color=(0.2, 0.6, 0.8, 1)
        )
        
        lang_select.add_widget(self.input_button)
        lang_select.add_widget(swap_btn)
        lang_select.add_widget(self.output_button)
        
        
        self.input_text = TextInput(
            hint_text='Enter text here',
            size_hint_y=0.3,
            multiline=True
        )
        self.output_text = TextInput(
            hint_text='Translation',
            size_hint_y=0.3,
            multiline=True,
            readonly=True
        )
        
        translate_btn = RoundedButton(
            text='Translate',
            size_hint=(0.3, 0.06),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.translate
        )
        
      
        layout.add_widget(header)
        layout.add_widget(lang_select)
        layout.add_widget(self.input_text)
        layout.add_widget(translate_btn)
        layout.add_widget(self.output_text)
        
        self.add_widget(layout)
        self.setup_language_dropdown()

    def setup_language_dropdown(self):
        self.input_dropdown = DropDown()
        self.output_dropdown = DropDown()

       
        self.input_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.output_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )

      
        self.input_search.bind(text=lambda instance, value: self.update_dropdown(value, 'input'))
        self.output_search.bind(text=lambda instance, value: self.update_dropdown(value, 'output'))

      
        self.update_dropdown("", 'input')
        self.update_dropdown("", 'output')

      
        self.input_button.bind(on_release=self.open_input_dropdown)
        self.output_button.bind(on_release=self.open_output_dropdown)

    
    def update_dropdown(self, search_text, dropdown_type):
        dropdown = self.input_dropdown if dropdown_type == 'input' else self.output_dropdown
        dropdown.clear_widgets()  

    
        for code, lang in LANGUAGES.items():
            if search_text.lower() in lang.lower(): 
                btn = Button(
                    text=lang,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                btn.bind(on_release=lambda btn, l=lang: self.select_language(l, dropdown_type))
                dropdown.add_widget(btn)


    def open_input_dropdown(self, instance):
        self.input_dropdown.clear_widgets()
        self.input_dropdown.add_widget(self.input_search)
        self.update_dropdown("", 'input') 
        self.input_dropdown.open(instance)

    def open_output_dropdown(self, instance):
        self.output_dropdown.clear_widgets()
        self.output_dropdown.add_widget(self.output_search)  
        self.update_dropdown("", 'output')  
        self.output_dropdown.open(instance)




    def select_language(self, lang, which):
        if which == 'input':
            self.input_button.text = lang
            self.input_dropdown.dismiss()
        else:
            self.output_button.text = lang
            self.output_dropdown.dismiss()

    # def translate(self, instance=None):
    #     try:
    #         source_lang = self.input_button.text
    #         target_lang = self.output_button.text
    #         text = self.input_text.text
            
    #         translated = self.translator.translate(
    #             text,
    #             src=source_lang,
    #             dest=target_lang
    #         ).text
    #         self.output_text.text = translated
    #     except Exception as e:
    #         self.output_text.text = f"Error: {str(e)}"

    def translate(self, instance=None):
        text = self.input_text.text.strip() 

    
        try:
            source_index = values.index(self.input_button.text)
            target_index = values.index(self.output_button.text)
        
            source_lang = keys[source_index]  
            target_lang = keys[target_index]

        except ValueError: 
            self.output_text.text = "Error: Invalid language selection"
            return

        if not text:
            self.output_text.text = "Please enter text to translate."
            return

        try:
            translator = Translator()
            translated = translator.translate(text, src=source_lang, dest=target_lang).text
            self.output_text.text = translated  
        except Exception as e:
            self.output_text.text = f"Error: {str(e)}"  




    def swap_languages(self, instance):
        self.input_button.text, self.output_button.text = self.output_button.text, self.input_button.text

    def go_back(self, instance):
        self.manager.current = 'home'


class TextToSpeechScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = Translator()
        with self.canvas.before:
            Color(rgba=(0.0, 0.15, 0.0, 1))  # Set background color (dark gray)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)
        self.setup_ui()

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
      
        header = BoxLayout(size_hint_y=0.08, spacing=5)
        back_btn = RoundedButton(
            text='Back',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.go_back
        )
        title = Label(text='Text to Speech', font_size='25sp',font_name = 'Yesteryear-Regular.ttf')
        header.add_widget(back_btn)
        header.add_widget(title)
        
        
        lang_select = BoxLayout(size_hint_y=0.12, spacing=5)
        self.input_button = RoundedButton(
            text='Input Language',
            size_hint_x=0.10,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.output_button = RoundedButton(
            text='Target Language',
            size_hint_x=0.10,
            background_color=(0.2, 0.6, 0.8, 1)
        )
        
        lang_select.add_widget(self.input_button)
        lang_select.add_widget(self.output_button)
        
    
        self.input_text = TextInput(
            hint_text='Enter text here',
            size_hint_y=0.3,
            multiline=True
        )
        
        self.output_text = TextInput(
            hint_text='Translation will appear here',
            size_hint_y=0.3,
            multiline=True,
            readonly=True
        )

       
        speak_btn = RoundedButton(
            text='Translate & Speak',
            size_hint=(0.3, 0.12),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.8, 1),
            on_press= self.translate
        )
        
       
        layout.add_widget(header)
        layout.add_widget(lang_select)
        layout.add_widget(self.input_text)
        layout.add_widget(speak_btn)
        layout.add_widget(self.output_text)
        
        self.add_widget(layout)
        self.setup_language_dropdown()

    def setup_language_dropdown(self):
        self.input_dropdown = DropDown()
        self.output_dropdown = DropDown()

        
        self.input_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.output_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )

       
        self.input_search.bind(text=lambda instance, value: self.update_dropdown(value, 'input'))
        self.output_search.bind(text=lambda instance, value: self.update_dropdown(value, 'output'))

       
        self.update_dropdown("", 'input')
        self.update_dropdown("", 'output')

        
        self.input_button.bind(on_release=self.open_input_dropdown)
        self.output_button.bind(on_release=self.open_output_dropdown)

    
    def update_dropdown(self, search_text, dropdown_type):
        dropdown = self.input_dropdown if dropdown_type == 'input' else self.output_dropdown
        dropdown.clear_widgets() 

       
        for code, lang in LANGUAGES.items():
            if search_text.lower() in lang.lower(): 
                btn = Button(
                    text=lang,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                btn.bind(on_release=lambda btn, l=lang: self.select_language(l, dropdown_type))
                dropdown.add_widget(btn)


    def open_input_dropdown(self, instance):
        self.input_dropdown.clear_widgets()
        self.input_dropdown.add_widget(self.input_search)  
        self.update_dropdown("", 'input') 
        self.input_dropdown.open(instance)

    def open_output_dropdown(self, instance):
        self.output_dropdown.clear_widgets()
        self.output_dropdown.add_widget(self.output_search) 
        self.update_dropdown("", 'output') 
        self.output_dropdown.open(instance)




    def select_language(self, lang, which):
        if which == 'input':
            self.input_button.text = lang
            self.input_dropdown.dismiss()
        else:
            self.output_button.text = lang
            self.output_dropdown.dismiss()

    def translate(self, instance=None):
        text = self.input_text.text.strip()
        # if not hasattr(self, 'input_language') or not hasattr(self, 'output_language'):
        #     self.output_text.text = 'Please select input and output language'
        #     return
     
        try:
            source_index = values.index(self.input_button.text)
            target_index = values.index(self.output_button.text)
        
            source_lang = keys[source_index] 
            target_lang = keys[target_index]

        except ValueError: 
            self.output_text.text = "Error: Invalid language selection"
            return

        if not text:
            self.output_text.text = "Please enter text to translate."
            return

        try:
            translator = Translator()
            translated = translator.translate(text, src=source_lang, dest=target_lang)
            self.output_text.text = translated.text
            self.speak(translated.text)  
        except Exception as e:
            self.output_text.text = f"Error: {str(e)}"  

    def speak(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()


    def go_back(self, instance):
        self.manager.current = 'home'


class SpeechToTextScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = Translator()
        self.engine = pyttsx3.init() 
        self.input_language_code = 'en'
        self.output_language_code = 'en'
        self.is_recording = False
        with self.canvas.before:
            Color(rgba=(0.0, 0.15, 0.0, 1))  # Set background color (dark gray)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)
        self.setup_ui()

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)

      
        header = BoxLayout(size_hint_y=0.08, spacing=5)
        back_btn = RoundedButton(
            text='Back',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.go_back
        )
        title = Label(text='Speech to Text', font_size='25sp',font_name = 'Yesteryear-Regular.ttf')
        header.add_widget(back_btn)
        header.add_widget(title)

      
        lang_select = BoxLayout(size_hint_y=0.12, spacing=5)
        self.input_button = RoundedButton(
            text='Input Language',
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.output_button = RoundedButton(
            text='Target Language',
            background_color=(0.2, 0.6, 0.8, 1)
        )
        lang_select.add_widget(self.input_button)
        lang_select.add_widget(self.output_button)

        self.speech_btn = RoundedButton(
            text='Tap to Start Recording',
            size_hint_y=0.12,
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.toggle_recording
        )

        self.recognized_text = TextInput(
            hint_text='Recognized speech will appear here',
            size_hint_y=0.3,
            multiline=True,
            readonly=True
        )

        self.output_text = TextInput(
            hint_text='Translation will appear here',
            size_hint_y=0.3,
            multiline=True,
            readonly=True
        )

    
        translate_btn = RoundedButton(
            text='Translate',
            size_hint=(0.3, 0.12),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.translate
        )

        layout.add_widget(header)
        layout.add_widget(lang_select)
        layout.add_widget(self.speech_btn)
        layout.add_widget(self.recognized_text)
        layout.add_widget(translate_btn)
        layout.add_widget(self.output_text)
        self.add_widget(layout)
        self.setup_language_dropdown()

    def setup_language_dropdown(self):
        self.input_dropdown = DropDown()
        self.output_dropdown = DropDown()

        self.input_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.output_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )

        self.input_search.bind(text=lambda instance, value: self.update_dropdown(value, 'input'))
        self.output_search.bind(text=lambda instance, value: self.update_dropdown(value, 'output'))

        self.update_dropdown("", 'input')
        self.update_dropdown("", 'output')

   
        self.input_button.bind(on_release=self.open_input_dropdown)
        self.output_button.bind(on_release=self.open_output_dropdown)

    
    def update_dropdown(self, search_text, dropdown_type):
        dropdown = self.input_dropdown if dropdown_type == 'input' else self.output_dropdown
        dropdown.clear_widgets()  

   
        for code, lang in LANGUAGES.items():
            if search_text.lower() in lang.lower():  
                btn = Button(
                    text=lang,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                btn.bind(on_release=lambda btn, l=lang: self.select_language(l, dropdown_type))
                dropdown.add_widget(btn)


    def open_input_dropdown(self, instance):
        self.input_dropdown.clear_widgets()
        self.input_dropdown.add_widget(self.input_search) 
        self.update_dropdown("", 'input')  
        self.input_dropdown.open(instance)

    def open_output_dropdown(self, instance):
        self.output_dropdown.clear_widgets()
        self.output_dropdown.add_widget(self.output_search) 
        self.update_dropdown("", 'output')  
        self.output_dropdown.open(instance)




    def select_language(self, lang, which):
        if which == 'input':
            self.input_button.text = lang
            self.input_dropdown.dismiss()
        else:
            self.output_button.text = lang
            self.output_dropdown.dismiss()

    def toggle_recording(self, instance):
        if not self.is_recording:
            self.speech_btn.text = "Recording... Tap to Stop"
            self.is_recording = True
            threading.Thread(target=self.start_speech_recognition, daemon=True).start()
        else:
            self.speech_btn.text = "Tap to Start Recording"
            self.is_recording = False

    def start_speech_recognition(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            try:
                print("Listening for speech...")
                audio = recognizer.listen(source, timeout=5)
                if self.is_recording:  
                    text = recognizer.recognize_google(audio, language=self.input_language_code)
                    self.recognized_text.text = text
                    print(f"Recognized: {text}")
                    Clock.schedule_once(lambda dt: self.update_recognized_text(text), 0)
            except sr.UnknownValueError:
                Clock.schedule_once(lambda dt: self.update_recognized_text("Could not understand audio"), 0)
            except sr.RequestError:
                Clock.schedule_once(lambda dt: self.update_recognized_text("Error connecting to recognition service"), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_recognized_text(f"Microphone Error: {e}"), 0)

       
        Clock.schedule_once(lambda dt: self.speech_btn_update(), 0)

    def update_recognized_text(self, text):
        self.recognized_text.text = text

    def speech_btn_update(self):
        self.speech_btn.text = "Tap to Start Recording"
        self.is_recording = False

    def translate(self, instance):
        text = self.recognized_text.text.strip()
        if not hasattr(self, 'input_language') or not hasattr(self, 'output_language'):
            self.output_text.text = 'Please select input and output language'
            return
        if not text:
            self.output_text.text = "Please speak something first."
            return
        try:
            translated = self.translator.translate(text, src=self.input_language_code, dest=self.output_language_code).text
            self.output_text.text = translated
        except Exception as e:
            self.output_text.text = f"Error: {str(e)}"

    def go_back(self, instance):
        self.manager.current = 'home'


class SpeechToSpeechScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = Translator()
        self.engine = pyttsx3.init() 
        self.input_language_code = 'en'
        self.output_language_code = 'en'
        self.is_recording = False
        with self.canvas.before:
            Color(rgba=(0.0, 0.15, 0.0, 1))  # Set background color (dark gray)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos)

        self.bind(size=self.update_bg, pos=self.update_bg)
        self.setup_ui()

    def update_bg(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

    def setup_ui(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=5)

      
        header = BoxLayout(size_hint_y=0.08, spacing=5)
        back_btn = RoundedButton(
            text='Back',
            size_hint_x=0.3,
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.go_back
        )
        title = Label(text='Speech to Text', font_size='25sp',font_name = 'Yesteryear-Regular.ttf')
        header.add_widget(back_btn)
        header.add_widget(title)

      
        lang_select = BoxLayout(size_hint_y=0.12, spacing=5)
        self.input_button = RoundedButton(
            text='Input Language',
            background_color=(0.2, 0.6, 0.8, 1)
        )
        self.output_button = RoundedButton(
            text='Target Language',
            background_color=(0.2, 0.6, 0.8, 1)
        )
        lang_select.add_widget(self.input_button)
        lang_select.add_widget(self.output_button)

        self.speech_btn = RoundedButton(
            text='Tap to Start Recording',
            size_hint_y=0.12,
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.toggle_recording
        )

        self.recognized_text = TextInput(
            hint_text='Recognized speech will appear here',
            size_hint_y=0.3,
            multiline=True,
            readonly=True
        )

        self.output_text = TextInput(
            hint_text='Translation will appear here',
            size_hint_y=0.3,
            multiline=True,
            readonly=True
        )

    
        translate_btn = RoundedButton(
            text='Translate',
            size_hint=(0.3, 0.12),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.translate
        )

        
        self.speak_btn = RoundedButton(
            text='Speak Output',
            size_hint=(0.3, 0.12),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.8, 1),
            on_press=self.speak_text
        )

        layout.add_widget(header)
        layout.add_widget(lang_select)
        layout.add_widget(self.speech_btn)
        layout.add_widget(self.recognized_text)
        layout.add_widget(translate_btn)
        layout.add_widget(self.output_text)
        layout.add_widget(self.speak_btn) 
        self.add_widget(layout)
        self.setup_language_dropdown()

    def setup_language_dropdown(self):
        self.input_dropdown = DropDown()
        self.output_dropdown = DropDown()

        self.input_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )
        self.output_search = TextInput(
            hint_text='Search Language',
            size_hint_y=None,
            height=40,
            multiline=False
        )

        self.input_search.bind(text=lambda instance, value: self.update_dropdown(value, 'input'))
        self.output_search.bind(text=lambda instance, value: self.update_dropdown(value, 'output'))

        self.update_dropdown("", 'input')
        self.update_dropdown("", 'output')

   
        self.input_button.bind(on_release=self.open_input_dropdown)
        self.output_button.bind(on_release=self.open_output_dropdown)

    
    def update_dropdown(self, search_text, dropdown_type):
        dropdown = self.input_dropdown if dropdown_type == 'input' else self.output_dropdown
        dropdown.clear_widgets()  

   
        for code, lang in LANGUAGES.items():
            if search_text.lower() in lang.lower():  
                btn = Button(
                    text=lang,
                    size_hint_y=None,
                    height=40,
                    background_color=(0.2, 0.6, 0.8, 1)
                )
                btn.bind(on_release=lambda btn, l=lang: self.select_language(l, dropdown_type))
                dropdown.add_widget(btn)


    def open_input_dropdown(self, instance):
        self.input_dropdown.clear_widgets()
        self.input_dropdown.add_widget(self.input_search) 
        self.update_dropdown("", 'input')  
        self.input_dropdown.open(instance)

    def open_output_dropdown(self, instance):
        self.output_dropdown.clear_widgets()
        self.output_dropdown.add_widget(self.output_search) 
        self.update_dropdown("", 'output')  
        self.output_dropdown.open(instance)




    def select_language(self, lang, which):
        if which == 'input':
            self.input_button.text = lang
            self.input_dropdown.dismiss()
        else:
            self.output_button.text = lang
            self.output_dropdown.dismiss()

    def toggle_recording(self, instance):
        if not self.is_recording:
            self.speech_btn.text = "Recording... Tap to Stop"
            self.is_recording = True
            threading.Thread(target=self.start_speech_recognition, daemon=True).start()
        else:
            self.speech_btn.text = "Tap to Start Recording"
            self.is_recording = False

    def start_speech_recognition(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=1)

            try:
                print("Listening for speech...")
                audio = recognizer.listen(source, timeout=5)
                if self.is_recording:  
                    text = recognizer.recognize_google(audio, language=self.input_language_code)
                    self.recognized_text.text = text
                    print(f"Recognized: {text}")
                    Clock.schedule_once(lambda dt: self.update_recognized_text(text), 0)
            except sr.UnknownValueError:
                Clock.schedule_once(lambda dt: self.update_recognized_text("Could not understand audio"), 0)
            except sr.RequestError:
                Clock.schedule_once(lambda dt: self.update_recognized_text("Error connecting to recognition service"), 0)
            except Exception as e:
                Clock.schedule_once(lambda dt: self.update_recognized_text(f"Microphone Error: {e}"), 0)

       
        Clock.schedule_once(lambda dt: self.speech_btn_update(), 0)

    def update_recognized_text(self, text):
        self.recognized_text.text = text

    def speech_btn_update(self):
        self.speech_btn.text = "Tap to Start Recording"
        self.is_recording = False

    def translate(self, instance):
        text = self.recognized_text.text.strip()
        if not hasattr(self, 'input_language') or not hasattr(self, 'output_language'):
            self.output_text.text = 'Please select input and output language'
            return
        if not text:
            self.output_text.text = "Please speak something first."
            return
        try:
            translated = self.translator.translate(text, src=self.input_language_code, dest=self.output_language_code).text
            self.output_text.text = translated
        except Exception as e:
            self.output_text.text = f"Error: {str(e)}"

    def speak_text(self, instance):
        text = self.output_text.text.strip()
        if text:
            self.engine.say(text)
            self.engine.runAndWait()

    def go_back(self, instance):
        self.manager.current = 'home'



class MainApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(TextToTextScreen(name='t2t'))
        sm.add_widget(TextToSpeechScreen(name = 't2s'))
        sm.add_widget(SpeechToTextScreen(name = 's2t'))
        sm.add_widget(SpeechToSpeechScreen(name = 's2s'))
        return sm

if __name__ == '__main__':
    MainApp().run()
