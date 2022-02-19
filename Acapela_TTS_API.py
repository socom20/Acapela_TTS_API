import requests
import os, sys
import json

import random
import string
import re
import subprocess
import glob

import hashlib

class Acapela_API():
    def __init__(self, download_dir='./downloads', verbose=False):
        self.verbose = verbose
        self.PHPSESSID = None
        self._is_logged = False
        self.wav_name = None

        self.secure_ajaxlogin = None

        self.download_dir = download_dir

        self._check_download_dir()
        
        return None

    def _check_download_dir(self):
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)

        return None

    def gen_phpsessid(self):
        return ''.join( random.choices(string.ascii_lowercase + string.digits, k=32) )


    def _set_secure_ajaxlogin(self):
        r = requests.get('https://mov.acapela-group.com/')
        c = r.text
        
        f_v = re.findall('<input type="hidden" id="secure_ajaxlogin" name="secure_ajaxlogin" value="([{}]*)" />'.format(string.hexdigits), c)
        if len(f_v) > 0:
            self.secure_ajaxlogin = f_v[0]
        else:
            print(' WARNING, secure_ajaxlogin not found!!!, returning DEFAULT value.', file=sys.stderr)
            self.secure_ajaxlogin = '4d3f994c38'

        return None

    def make_wav_name(self, text='hola', listen_speed=180, listen_shaping=100, listen_voice='Spanish - dnn-DavidPalacios_sps'):
        to_hash_str = '-'.join( [text, str(listen_speed), str(listen_shaping), listen_voice] )
        wav_name = hashlib.md5(to_hash_str.encode()).hexdigest()  + '.wav'
        return wav_name

    def _load_credentials(self, credentials_path='./acapela_credentials.json'):
        with open(credentials_path, 'r') as f:
            credentials_d = json.loads(f.read())

        return credentials_d['username'], credentials_d['password']
    
                
    def login(self, username='username', password='pasword', PHPSESSID=None, credentials_path=None):

        if credentials_path is not None:
            if os.path.exists(credentials_path):
                username, password = self._load_credentials(credentials_path)
            else:
                print(' - WARNING, File Not Found: credentials_path file = "{}". Using "username" and "password".'.format(credentials_path), file=sys.stderr)

        if self.secure_ajaxlogin is None:
            self._set_secure_ajaxlogin()
            
        if PHPSESSID is None:
            PHPSESSID = self.gen_phpsessid()

        self.PHPSESSID = PHPSESSID
        
        headers = {'Host': 'mov.acapela-group.com',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'X-Requested-With':'XMLHttpRequest',
                   'Content-Length':'130',
                   'Connection': 'keep-alive',
                   'Referer': 'https://mov.acapela-group.com/',
                   }

        url = 'https://mov.acapela-group.com/wp-admin/admin-ajax.php'

        cookies = {'PHPSESSID':PHPSESSID}

        payload = {'MOV_user_login':username,
                   'MOV_user_pass':password,
                   'email':  '',
                   'action':  'ajaxmovlogin',
                   'secure_ajaxlogin':self.secure_ajaxlogin,
                   '_wp_http_referer':'/'}


        r = requests.post(url, data=payload, headers=headers, cookies=cookies)

        if self.verbose:
            print(' - Login Status:', r.status_code, ' - reason:', r.reason)

                
        d = json.loads( r.text )
        

        if d['userresult'] == 1:
            if self.verbose:
                print(' - Login OK!! generado PHPSESSID: {}'.format(PHPSESSID))

            self._is_logged = True
            return PHPSESSID
        else:
            raise Exception(' - ERROR: Acapela Login Fail :( ')
            self._is_logged = False
            return None


    
    def _make_voice(self, text='hola que hay de nuevo', listen_speed=180, listen_shaping=100, listen_voice='Spanish - dnn-DavidPalacios_sps'):
        
        PHPSESSID = self.PHPSESSID
        
        if PHPSESSID is None:
            raise Exception(' - ERROR, _make_voice: You must do the loggin step first')
        

        
        listen_speed =  int(listen_speed)
        assert 50 <= listen_speed <= 300, '_make_voice must be: 50 <= listen_speed <= 300'

        listen_shaping =  int(listen_shaping)
        assert 60 <= listen_shaping <= 140, '_make_voice must be: 60 <= listen_shaping <= 140'

        
        
        headers = {'Host': 'mov.acapela-group.com',
                   'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Accept-Language': 'es-AR,es;q=0.8,en-US;q=0.5,en;q=0.3',
                   'Accept-Encoding': 'gzip, deflate, br',
                   'Content-Lenght': '161',
                   'Content-Type': 'application/x-www-form-urlencoded',
                   'Origin': 'https://mov.acapela-group.com',
                   'Connection': 'keep-alive',
                   'Referer': 'https://mov.acapela-group.com/listen/',
                   'Upgrade-Insecure-Requests': '1'}



        url = 'https://mov.acapela-group.com/listen/'

        cookies = {'PHPSESSID':PHPSESSID}
        
        
        payload = {'listen_language':'Spanish',
                   'listen_voice':listen_voice,
                   'listen_text':  text,
                   'listen_speed':  str(listen_speed),
                   'listen_shaping':str(listen_shaping),
                   'MOV_listen_button':'Listen'}


        r = requests.post(url, data=payload, headers=headers, cookies=cookies)

        if self.verbose:
            print(' - _make_voice: Status:', r.status_code, ' - reason:', r.reason)


        data = r.text

        
        idx0 = data.find('<source src="https://mov.acapela-group.com/user_text/')
        if idx0 != -1:
            idx1 = data.find('" type="audio/wav">', idx0)
            dwd_name = data[idx0+53:idx1]
        else:
            dwd_name = None


        if self.verbose:
            print(' - _make_voice: Creado:', dwd_name)

        if dwd_name is None:
            raise Exception(' - ERROR, _make_voice: unable to create wav file.')
        
        return dwd_name


    def _download_wav(self, dwd_name='DavidPalacios_1576548394.wav', wav_name=None):

        if wav_name is None:
            wav_name = dwd_name

            
        self._check_download_dir()
        
        url = 'https://mov.acapela-group.com/user_text/{}'.format(dwd_name)

        if self.verbose:
            print(' - download_wav: Bajando archivo wav:', dwd_name)
            
        r = requests.get(url)
        
        if self.verbose:
            print(' - download_wav: Status:', r.status_code, ' - reason:', r.reason)
            
        data = r.content

        if len(data) == 0:
            raise Exception(' - ERROR, get_make_wav: unable to download wave file.')
        
        wav_path = os.path.join(self.download_dir, wav_name)
        with open(wav_path, 'wb') as f:
            f.write(data)

        if self.verbose:
            print(' - download_wav: Archivo escrito en disco: {}'.format(wav_path))

        self.wav_name = wav_name
        self.wav_path = wav_path
        return wav_path
    

    def speak_and_download_wav(self, text='Lista la API', listen_speed=180, listen_shaping=100, listen_voice='Spanish - dnn-DavidPalacios_sps', convert_to_ogg=False, when_ogg_rm_wav_file=True, use_cache=True):
        if not self._is_logged:
            raise Exception(' - ERROR, speak_and_download_wav: You must do the loggin step first')

        wav_name = self.make_wav_name(text, listen_speed=180, listen_shaping=100, listen_voice=listen_voice)
        wav_path = os.path.join(self.download_dir, wav_name)
        
        if use_cache and os.path.exists(wav_path):
            if self.verbose:
                print(' - speak_and_download_wav: using cached file: {}'.format(wav_path) )
                
            self.wav_name = wav_name
            self.wav_path = wav_path
            
        else:
            dwd_name = self._make_voice(text=text, listen_speed=listen_speed, listen_shaping=listen_shaping, listen_voice=listen_voice)
            wav_path = self._download_wav(dwd_name=dwd_name, wav_name=wav_name)

        if convert_to_ogg:
            wav_name = self.wav_to_ogg(wav_path, rm_wav_file=when_ogg_rm_wav_file)
        
        return wav_name


    def wav_to_ogg(self, wav_path=None, ogg_filename=None, rm_wav_file=False):
        if wav_path is None:
            wav_path = self.wav_path

        if ogg_filename is None:
            ogg_path = os.path.splitext(wav_path)[0] + '.ogg'
            
        subprocess.check_call('oggenc -q 3 -o {} {}'.format(ogg_path, wav_path).split())

        if rm_wav_file:
            os.remove(wav_path)
            
        return ogg_path
    

    def play(self, filename=None):
        
        if filename is None:
            filename = self.wav_path

        if self.verbose:
            print(' - play: filename={}'.format(filename))
            
        os.system('aplay -q {}'.format(filename))
        return None


    def purge_downloaded_files(self):
        for ext in ['*.wav', '*.ogg']:
            for path in glob.glob(os.path.join( self.download_dir, ext)):
                os.remove(path)
                if self.verbose:
                    print(' Removed: "{}"'.format(path))
                           
        return None        
        
    


if __name__ == '__main__':

##    listen_voice = 'Spanish - dnn-DavidPalacios_sps'
    listen_voice = 'Spanish (Spain) - dnn-DavidPalacios5802_sps'

    acapela = Acapela_API(verbose=True)
    acapela.login(credentials_path='./acapela_credentials2.json')
    acapela.speak_and_download_wav('Esta es una API python para acapela.', convert_to_ogg=False, listen_voice=listen_voice)
    acapela.play()
    









    
