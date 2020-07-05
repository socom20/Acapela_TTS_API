# Acapela TTS (Text To Speech) API

This is a simple implementation of an API made in Python 3 to interact with the Acapela my-own-voice website:

https://mov.acapela-group.com/

## Installation

Just install dependences:
```sh
$ pip3 install requests
```


## Usage

Simply clone the repository and import the Acapela API class:

## Example

```python3
acapela = Acapela_API(verbose=True)
acapela.login(credentials_path='./acapela_credentials.json')
acapela.speak_and_download_wav('Hello World.', convert_to_ogg=False)
acapela.play()
```
