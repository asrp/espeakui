#!/usr/bin/env python
import urwid
import espeak
from .espeaker import Espeaker
from xreload import xreload
import espeakui
import sys
import regex

class EspeakUI(espeakui.EspeakUI):
    def clipcallback(self, wave_string, event_type, position, length, num_samples, name):
        if event_type == espeak.const['event']['msg_terminated']:
            logging.debug("End of clipboard")
            raise urwid.ExitMainLoop()

    def keypress(self, key):
        #key = event.keysym
        if type(key) == str:
            logging.debug("Keypress: %s" % key)
        if key == "]":
            self.speaker.rate = int(self.speaker.rate * 1.2)
        elif key == "[":
            self.speaker.rate = int(self.speaker.rate / 1.2)
        elif key == " ":
            if self.speaker.playing():
                self.speaker.pause()
            else:
                self.speaker.play()
        elif key == "l":
            #os.system("xclip -o > test")
            s = open("text").read()
            self.speaker.play(s)
        elif key in ["left", "up", "right", "down"]:
            playing = self.speaker.playing()
            diff = {"left": -20, "up": 200, "right": 20, "down": -200}[key]
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
        elif key == "q":
            raise urwid.ExitMainLoop()

if __name__ == "__main__":
    espeak.core.init()
    if len(sys.argv) > 1 and sys.argv[1] == '-nc':
        ui = EspeakUI(None, clipboard=False)
    else:
        ui = EspeakUI(None)
    txt = urwid.Text(u"Welcome to espeak_urwid")
    fill = urwid.Filler(txt, 'top')
    loop = urwid.MainLoop(fill, unhandled_input=ui.keypress)
    loop.run()
