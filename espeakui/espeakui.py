#!/usr/bin/env python
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import espeak
from .espeaker import Espeaker
import sys
import logging
import os, os.path

import threading
from subprocess import Popen, PIPE
import re
from .translate import translate, regex, languages as translate_languages
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
    text = re.sub("(%s)" % regex.time, "[TIMESTAMP]", text, flags=re.X)
    text = text.replace('<', ' ').replace('>', ' ')
    for source, target in translate[lang]:
        text = text.replace(source, target)
    text = text.replace("\n", '<mark name="eol"/>\n')
    return text

class EspeakUI():
    def __init__(self, root, filename="<clipboard>", languages=["en"], dirname=None):
        self.speaker = Espeaker()
        self.innerspeaker = Espeaker()
        self.root = root
        self.dirname = dirname
        self.filename = filename
        if dirname:
            self.entries = sorted((f for f in os.listdir(dirname)
                                   if os.path.isfile(self.abspath(f))),
                                  key=lambda f: os.path.getmtime(self.abspath(f)))
            if filename is None:
                self.filename = self.entries[-1]
        self.languages = languages
        self.lock = threading.Lock()
        self.speaker.rate = 360
        self.speaker.wordgap = 3
        self.speaker.capitals = 1
        self.speaker.ssml = True
        if self.filename == "<clipboard>":
            self.setupclipboard(get_clipboard())
        elif self.filename:
            self.setupclipboard(open(self.abspath(self.filename)).read())

    def abspath(self, filename):
        return os.path.join(self.dirname, filename) if self.dirname else filename

    def setupclipboard(self, clipboard):
        lang = guessLanguage(clipboard)
        if lang not in self.languages:
            lang = self.languages[0]
        self.speaker.voice["language"] = lang

        clipboard = clipboard.decode('utf-8') if sys.version_info[0] >= 3 and type(clipboard) == bytes else clipboard
        text = text_substitution(clipboard, lang)
        if self.dirname is None:
            self.speaker.add_callback(self.clipcallback)
        self.speaker.play(text)

    def clipcallback(self, wave_string, event_type, position, length, num_samples, name):
        if event_type == espeak.const['event']['msg_terminated']:
            def quit_():
                if not self.speaker.playing():
                    with self.lock:
                        self.root.quit()
            # Calling self.root.quit from the callback with segfault (or block)
            self.root.after(100, quit_)

    def keypress(self, event):
        with self.lock:
            key = event.keysym
            logging.debug("Acquired lock")
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
                inner_playing = self.innerspeaker.playing()
                # logging.debug(i, playing, inner_playing, self.speaker.position)
                diff = {"Left": -20, "Up": 200, "Right": 20, "Down": -200}[key]
                self.speaker.pause()
                self.speaker.position = max(0, self.speaker.position + diff)
                if playing:
                    self.speaker.play()
                elif inner_playing:
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
            elif key == "q":
                self.speaker.pause()
                self.root.quit()
            elif key in ["n", "p"]:
                if self.dirname:
                    diffs = {"n": 1, "p": -1}
                    # Should rescan or not?
                    index = self.entries.index(self.filename) + diffs[key]
                    if 0 <= index < len(self.entries):
                        self.speaker.pause()
                        self.filename = self.entries[index]
                        logging.debug(self.filename)
                        self.setupclipboard(open(self.abspath(self.filename)).read())
        logging.debug("Released lock")

if __name__ == '__main__':
    root = tk.Tk()

    espeak.core.init()
    if len(sys.argv) > 1 and sys.argv[1] == '-nc':
        ui = EspeakUI(root, filename=None)
    elif len(sys.argv) > 1 and sys.argv[1] == '-f':
        ui = EspeakUI(root, filename=sys.argv[2])
    elif len(sys.argv) > 1 and sys.argv[1] == '-d':
        ui = EspeakUI(root, filename=None, dirname=sys.argv[2])
    else:
        ui = EspeakUI(root)
    root.geometry('300x200')
    root.bind('<KeyPress>', lambda event: ui.keypress(event))
    root.mainloop()
