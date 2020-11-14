# espeakui - a text-to-speech interface with mplayer-like bindings, using espeak

## Installation

    pip install espeakui

## Dependencies

- [python-espeak](https://github.com/asrp/python-espeak) - The custom version that's here on Github
- xclip - For clipboard mode only. Install for your system with something like `sudo apt-get install xclip` or `pacman -S xclip` or other.

    An untested Windows and OSX version is available using [pyperclip](https://github.com/asweigart/pyperclip). Change `XCLIP_MODE = True` to `False` in `espeakui.py` to activate. The reason for not using pyperclip by default is that pyperclip defaults to the wrong clipboard for xclip on Linux and doesn't have an option to change clipboards.
- [guess_language](https://pypi.python.org/pypi/guess-language) (optional) - For automatically detecting the text language and picking the voice for that language. Install with `pip install guess_language`.

## Usage

Run

    python -m espeakui.espeakui

A contentless window opens. It accepts these keys.

- `space` Pause/resume
- `[` Slow down
- `]` Speed up
- `Up arrow` Seek forward
- `Down arrow` Seek backward
- `Left arrow` Seek forward less
- `Right arrow` Seek backward less
- `s` Zoom: speaks the text around the current cursor at a much slower pace and then resumes normal speech.
- `l` load a text file "text" and read it (replaces what is currently being read). Mainly for non-clipboard mode.

Seeking is possible while paused and "preview" of the text surrounding the new cursor position is played.

There are two modes of operation: "normal" and "clipboard". clipboard mode is the most used but needs `xclip` to be installed.

There's an alternative curses interface with the same keybindings. It uses [urwid](http://urwid.org/).

    pip install urwid
    python -m espeakui.espeak_urwid

**Suggestion:** I've setup a keyboard shortcut to call `python espeakui.py` in my windows manager. Then just highlight text somewhere and hit the keyboard shortcut.

## Uses

- Read long articles and comment sections while you do other things. A bit like your own radio station.
- Proofread your own writing. Its possible to read the visual text along with `espeakui` to catch more errors in the same amount of time. (Yes, it was used to proofread this readme although there are probably still some errors.)
- Use as a library to make your own UI with the framework and keybindings of your choice. Some efforts was put into making the individual files modular.

## Earcon

An end-of-line earcon can be enabled by uncommenting the line in the `play_wave` function at the beginning of `espeaker.py`. Requires the `play` binary from SoX (or substitute your own; it must be non-blocking).

## Other

The rest of the features are a hodgepodge of personal preferences. Hopefully espeakui is small enough to be modified to your own liking.

- Text substitution. Some text like URL links are replaced before being spoken. (Its usually not very insightful to hear full URL links out loud.)
- An earcon for end of line. Useful for text with lots of short lines. Don't want too many earcons or we'll forget what they mean.
- Multilanguage support with language detection using [guess_language](link)

## Usage as a library

`espeakui.py` depends on `espeaker.py` which can be used independently as a library. It also provides some classes not used by `espeakui.py`.

### FileEspeak

    import espeak
    from espeakui.espeaker import FileEspeak
    espeak.init(playback=False)
    file_espeak = FileEspeak(open("test.wav", "w"))
    file_espeak.say("Hello world")

`espeaker.FileEspeak` writes its output to a file instead of playing back.

### SubprocessEspeak

`espeaker.SubprocessEspeak` pipes the wave content to a subprocess.

    import espeak
    from espeakui.espeaker import SubprocessEspeak
    espeak.init(playback=False)
    subprocess_espeak = SubprocessEspeak(command="aplay")
    subprocess_espeak.say("Hello world")

will use `aplay` to playa the audio output.

### Espeaker

`Espeaker` provides an API that resembles audio file playback: `play`, `pause`, `stop`. Speaker parameter changes (rate, pitch, volume, etc) appear to take effect immediately when this `Espeaker` is speaking.

For example, run this in the interpreter

    import espeak
    from espeakui import espeaker
    espeak.init()
    espeaker = espeaker.Espeaker()
    text = "\n".join("\n".join(["{} little bugs in the code.".format(i),
                                "{} bugs in the code.".format(i),
                                "Fix one bug. Compile it again.",
                                "{} little bugs in the code.".format(i+1)])
                     for i in range(99, 150))
    espeaker.play(text)
    # Wait a bit between each command
    espeaker.rate = 300
    espeaker.rate = 100
    espeaker.pitch = 70
    espeaker.pitch = 30
    espeaker.punctuation = 'all'
    # To make it stop
    espeaker.pause()

## Why?

Sending large amounts of text to espeak is too fragile. If you miss a bit you have to restart the entire thing. If some parts are uninteresting its not possible to skip through it. But large amounts of text is where espeak is really useful. An audio/video player's interface on the other hand *is* very good for playback. So I made this, a TTS with (some of) mplayer's playback interface.

Another way would be to use `espeak -w` and then call `mplayer` but this involves waiting while espeak writes the wav file and the file is created for nothing if only listened through halfway through. And even with `-af scaletempo`, there's some distortion, especially when sped up more than 2x.

## Future ideas

Ideas that may be worth trying

- Recognize more patterns in the text. Short audio for large numbers (such as pitch depending on its value).
- Paste from the html or other non-plain text clipboard and adjust speed depending on the text's visibility (size, contrast).
- Find the "skip to content" link for webpages and jump to it.
