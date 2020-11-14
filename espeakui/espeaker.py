import espeak
import subprocess
import sys
import pkg_resources

def play_wave(filename):
    # subprocess.Popen(["play", "-q", filename])
    pass

class SubprocessEspeak(espeak.Espeak):
    def __init__(self, command="aplay"):
        espeak.Espeak.__init__(self)
        self.command = command
        self.add_callback(self.espeak_callback)
        self.process = None

    def espeak_callback(self, *args):
        logging.debug("Stream %s %s\n" % (len(args), len(args[0])))
        if not self.process:
            self.process = subprocess.Popen(self.command,
                                            stdin=subprocess.PIPE,
                                            bufsize=0)
            self.process.stdin.write(espeak.wave_header())
        self.process.stdin.write(args[0])

# Don't really know how to stop...
class FileEspeak(espeak.Espeak):
    def __init__(self, stream=sys.stdout):
        espeak.Espeak.__init__(self)
        self.add_callback(self.espeak_callback)
        self.stream = stream
        self.stream.write(espeak.wave_header())

    def espeak_callback(self, *args):
        logging.debug("Stream %s %s\n" % (len(args), len(args[0])))
        self.stream.write(args[0])

class Espeaker(espeak.Espeak):
    def __init__(self, text=""):
        espeak.Espeak.__init__(self)
        self.text = text
        self.position = 0
        self.add_callback(self.callback)
        self.param_change_restart = True
        self.lastpos = {}
        self.sentences = []
        self.ssml = False
        self.phonemes = False
        self.endpause = False
        self.continuous = False

    def callback(self, wave_string, event_type, position, length, num_samples, name):
        if espeak.event_name[event_type] == "mark" and name == "eol":
            filename = pkg_resources.resource_filename(
                'espeakui', 'earcon/carriage_return.wav')
            play_wave(filename)
        #print(espeak.event_name[event_type], position, name)
        #print(repr(self.text[position-1]))
        if espeak.event_name[event_type] == "sentence":
            self.sentences.append(position)
        self.lastpos[espeak.event_name[event_type]] = position
        if espeak.event_name[event_type] in ["sentence", "msg_terminated"] and self.continuous:
            pass
            #if espeak.event_name[event_type] == "msg_terminated" and len(self.text) > self.position + 1:
            #    self.play()
        else:
            self.position = position

    def stop(self):
        self.pause()
        self.position = 0

    def play(self, newtext=None):
        if newtext is not None:
            self.stop()
            self.text = newtext
        self.say(self.text, self.position,
                 ssml=self.ssml,
                 phonemes=self.phonemes,
                 endpause=self.endpause)

    def __setattr__(self, key, value):
        if (key in espeak.const["parameter"] and self.param_change_restart and\
           self.playing()):
            self.pause()
            espeak.Espeak.__setattr__(self, key, value)
            self.play()
        else:
            espeak.Espeak.__setattr__(self, key, value)

    def saysentence(self, index=-1):
        text = self.text[self.sentences[index-1]-1:self.sentences[index]-1]
        espinner = Espeaker(text)
        espinner.play()
        return espinner

if __name__ == '__main__':
    espeak.init(playback=False)
    file_espeak = FileEspeak(open("test.wav", "wb"))
    file_espeak.say("Hello world")
