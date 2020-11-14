#!/usr/bin/env python
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import espeak
from .espeaker import Espeaker
import sys
import logging

from subprocess import Popen, PIPE
import re
from .translate import translate, regex
try:
    from guess_language.guess_language import guessLanguage
except ImportError:
    def guessLanguage(*args):
        return None

XCLIP_MODE = True

def get_clipboard():
    if XCLIP_MODE:
        return Popen(["xclip", "-o"], stdout=PIPE).communicate()[0]
    else:
        import pyperclip
        return pyperclip.paste()

def text_substitution(text, lang):
    text = re.sub(regex.url, "[URL link]", text)
    text = re.sub("(%s)" % regex.timestamp, "[TIMESTAMP]", text, flags=re.X)
    #text = text.replace('<', ' ').replace('>', ' ')
    for source, target in translate[lang]:
        text = text.replace(source, target)
    text = text.replace("\n", '<mark name="eol"/>\n')
    return text

class EspeakUI():
    def __init__(self, root, clipboard=True, languages=["en"]):
        self.speaker = Espeaker()
        self.innerspeaker = Espeaker()
        self.root = root
        self.clipboard_mode = clipboard
        self.languages = languages
        if clipboard:
            self.setupclipboard()

    def setupclipboard(self):
        # self.speaker.rate = 230
        self.speaker.rate = 360
        self.speaker.wordgap = 3
        self.speaker.capitals = 1
        self.speaker.ssml = True

        clipboard = get_clipboard()
        lang = guessLanguage(clipboard)
        if lang not in self.languages:
            lang = self.languages[0]
        self.speaker.voice["language"] = lang

        clipboard = clipboard.decode('utf-8') if sys.version_info[0] >= 3 else clipboard
        text = text_substitution(clipboard, lang)
        self.speaker.add_callback(self.clipcallback)
        self.speaker.play(text)

    def clipcallback(self, wave_string, event_type, position, length, num_samples, name):
        if event_type == espeak.const['event']['msg_terminated']:
            self.root.quit()

    def keypress(self, event):
        key = event.keysym
        logging.debug("Keypress: %s" % key)
        if key == "bracketright":
            self.speaker.rate = int(self.speaker.rate * 1.2)
        elif key == "bracketleft":
            self.speaker.rate = int(self.speaker.rate / 1.2)
        elif key == "space":
            if self.speaker.playing():
                self.speaker.pause()
            else:
                self.speaker.play()
        elif key == "l":
            s = open("text").read()
            self.speaker.play(s)
        elif key in ["Left", "Up", "Right", "Down"]:
            playing = self.speaker.playing()
            diff = {"Left": -20, "Up": 200, "Right": 20, "Down": -200}[key]
            self.speaker.pause()
            self.speaker.position = max(0, self.speaker.position + diff)
            if playing:
                self.speaker.play()
            else:
                self.innerspeaker.rate = self.speaker.rate
                start = self.speaker.position
                end = self.speaker.position + 15
                text = self.speaker.text[start:end]
                self.innerspeaker.say(text)
        elif key == "s":
            self.innerspeaker.rate = int(self.speaker.rate / 2)
            start = max(0, self.speaker.position - 30)
            end = max(0, self.speaker.position + 10)
            text = self.speaker.text[start:end]
            self.innerspeaker.say(text)

if __name__ == "__main__":
    espeak.core.init()
    root = tk.Tk()
    if len(sys.argv) > 1 and sys.argv[1] == '-nc':
        ui = EspeakUI(root, clipboard=False)
    else:
        ui = EspeakUI(root)
    root.geometry('300x200')
    root.bind('<KeyPress>', lambda event: ui.keypress(event))
    root.mainloop()
