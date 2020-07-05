# Acapela TTS (Text To Speech) API

This is a simple implementation of an API made in Python 3 to interact with the Acapela my-own-voice website:

https://mov.acapela-group.com/

## Installation

Just install dependences:
```sh
$ pip3 install requests
```

## Basic Usage Example

Simply clone the repository and import the Acapela API class.

```python3
# Create an instance
acapela = Acapela_API(verbose=True)

# Logging using a credential file or an username and password pair
acapela.login(
    username=None,
    password=None,
    credentials_path='./acapela_credentials.json')

# Create the voice file and download the wav
acapela.speak_and_download_wav(
    text='Hello World.',
    listen_speed=180,
    listen_shaping=100,
    listen_voice='Spanish - dnn-DavidPalacios_sps'
    convert_to_ogg=False,
    when_ogg_rm_wav_file=True,
    use_cache=True)

# Listen to the voice
acapela.play()
```
