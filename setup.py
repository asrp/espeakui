from setuptools import setup, find_packages

setup(name='espeakui',
      version='0.1',
      description='A text-to-speech interface with mplayer-like bindings, using espeak',
      long_description=open("readme.md").read(),
      long_description_content_type="text/markdown",
      url='https://github.com/asrp/espeakui',
      author='asrp',
      author_email='asrp@email.com',
      packages=find_packages(),
      install_requires=['python-espeak', 'guess_language'],
      extras_require = {'full': ['urwid']},
      keywords='espeak ui tts')
