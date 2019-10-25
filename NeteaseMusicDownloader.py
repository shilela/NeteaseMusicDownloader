# -*- coding: utf-8 -*-
import json
import time
import urllib
import urllib.request
import socket
import time
from AES import AESCipher

class NeteaseMusicDownloader(object):

    def __init__(self):
        # secretKey and encSecKey are static which can get from browser
        # At the same time, RSA algorithm can be omitted
        # self.headers can pretend to be a browser in network requests
        self.config = {
                'nonce': '0CoJUm6Qyw8W8jud',
                'secretKey': "jAeVJD4RopCXQ29K",
                'encSecKey': "86f0422931cb11496fbd0b048ad2630752a80c18d518e9db431efd1f4dd478f20eb1bda4cf3c674a1084ea926700d51877ecd508bfc9f575332d15d9af3205827d7f8a136661749c7767dfcade1ec8356147dad022a8177a87522549e9ae17d8f9f412e210c91d6c76ed79bfb8154761bab91f952c95b7ef9d53617c75664385",
                'IV': '0102030405060708'
        }
        self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0',
                        'Cookie': '',# your cookies
                        'Referer':'http://music.163.com/'
        }

    # aes-128-cbc
    def aesEncode(self, data, key):
        return AESCipher(key).encrypt(data, self.config['IV'])

    # prepare post data
    def prepare(self,data):
        result = { 'params': self.aesEncode(json.dumps(data), self.config['nonce']) }
        result['params'] = self.aesEncode(result['params'], self.config['secretKey'])
        result['encSecKey'] = self.config['encSecKey']
        return result

    def getSongInfo(self, songId):
        """
        Index 0: name of the song
        Index 1: picture's url of the song
        """
        songId = str(songId)
        url = 'http://music.163.com/api/v3/song/detail?id='+songId+'&c=[{"id":"'+songId+'"}]'
        request = urllib.request.Request(url,headers=self.headers,method = 'GET')
        response = json.loads(urllib.request.urlopen(request,timeout=10).read().decode('utf-8'))

        if 'code' in response and response['code'] == 200 and response['songs'] != []:
            res = response['songs'][0]
            return res['name'],res['al']['picUrl']
        else:
            return None

    def search(self, keyword):
        """
        Index 0: id of the song
        Index 1: name of the song
        Index 2: picture's url of the song
        """
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token='
        params={
                "hlpretag":"<span class=\"s-fc7\">",
                "hlposttag":"</span>",
                "s":keyword,
                "type":"1",
                "offset":"0",
                "total":"true",
                "limit":"30",
                "csrf_token":""
                }
        paramStr = urllib.parse.urlencode(self.prepare(params))
        postData = paramStr.encode('utf-8')


        request = urllib.request.Request(url=url, data=postData, headers=self.headers, method='POST')
        response = json.loads(urllib.request.urlopen(request,timeout=10).read().decode('utf-8'))
        
        if 'code' in response and response['code'] == 200 and response['result']['songCount'] != 0:
            res = response['result']['songs'][0]
            return res['id'],res['name'],res['al']['picUrl']
        else:
            return None

    def getLyric(self, songId):
        """
        Index 0: lyric
        Index 1: tlyric
        """
        songId=str(songId)
        url='https://music.163.com/weapi/song/lyric?csrf_token='
        params={
                'id': songId,
                'os': 'pc',
                'lv': -1,
                'kv': -1,
                'tv': -1,
                'csrf_token': ''
        }
        postStr = urllib.parse.urlencode(self.prepare(params))
        postData = postStr.encode('utf-8')
        request = urllib.request.Request(url=url, data=postData, headers=self.headers, method='POST')
        response = json.loads(urllib.request.urlopen(request,timeout=10).read().decode('utf-8'))

        lyric = ''
        tlyric = ''
        if 'lrc' in response:
            lyric = response['lrc']['lyric']
        if 'tlyric' in response:
            tlyric = response['tlyric']['lyric']
        return lyric,tlyric
    
    def getUrl(self, songId):
        songId = str(songId)
        url = 'https://music.163.com/weapi/song/enhance/player/url?csrf_token='
        params={'ids': [songId],'br': 999000,'csrf_token': ''}
        postStr = urllib.parse.urlencode(self.prepare(params))
        postData = postStr.encode('utf-8')
        request = urllib.request.Request(url=url, data=postData, headers=self.headers, method='POST')
        response = json.loads(urllib.request.urlopen(request,timeout=10).read().decode('utf-8'))
        url = response['data'][0]['url']
        if isinstance(url,str):
            return url
        else:
            return '' # don't have the copyright
    
    # Backup getUrl function
    def getUrl_backup(self, songId):
        songId = str(songId)
        return 'http://music.163.com/song/media/outer/url?id=' + songId + '.mp3'

    def download(self, songId, callback=None):
        songId = str(songId)
        filename = songId + "_" + str(int(time.time()))
        musicUrl = self.getUrl(songId)
        if musicUrl == '':
            return ''
        savepath = './%s.%s' % (filename,musicUrl.split('.')[-1])
        socket.setdefaulttimeout(600)
        urllib.request.urlretrieve(musicUrl, savepath, callback)
        return savepath
