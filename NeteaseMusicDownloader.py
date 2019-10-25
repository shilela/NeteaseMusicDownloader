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
                        'Cookie': '_iuqxldmzr_=32; _ntes_nnid=8d4ef0883a3bcc9d3a2889b0bf36766a,1533782432391; _ntes_nuid=8d4ef0883a3bcc9d3a2889b0bf36766a; __utmc=94650624; WM_TID=GzmBlbRkRGQXeQiYuDVCfoEatU6VSsKC; playerid=19729878; __utma=94650624.1180067615.1533782433.1533816989.1533822858.9; __utmz=94650624.1533822858.9.7.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; WM_NI=S5gViyNVs14K%2BZoVerGK69gLlmtnH5NqzyHcCUY%2BiWm2ZaHATeI1gfsEnK%2BQ1jyP%2FROzbzDV0AyJHR4YQfBetXSRipyrYCFn%2BNdA%2FA8Mv80riS3cuMVJi%2BAFgCpXTiHBNHE%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee84b674afedfbd3cd7d98b8e1d0f554f888a4abc76990b184badc4f89e7af8ece2af0fea7c3b92a91eba9b7ec738e8abdd2b741e986a1b7e87a8595fadae648b0b3bc8fcb3f8eafb69acb69818b97ccec5dafee9682cb4b98bb87d2e66eb19ba2acaa5bf3b6b7b1ae5a8da6ae9bc75ef49fb7abcb5af8879f87c16fb8889db3ec7cbbae97a4c566e992aca2ae4bfc93bad9b37aab8dfd84f8479696a7ccc44ea59dc0b9d7638c9e82a9c837e2a3; JSESSIONID-WYYY=sHwCKYJYxz6ODfURChA471BMF%5CSVf3%5CTc8Qcy9h9Whj6CfMxw4YWTMV7CIx5g6rqW8OBv04YGHwwq%2B%5CD1N61qknTP%2Fym%2BHJZ1ylSH1EabbQASc9ywIT8YvOr%2FpMgvmm1cbr2%2Bd6ssMYXuTlpOIrKqp%5C%2FM611EhmfAfU47%5CSQWAs%2BYzgY%3A1533828139236',
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

a=NeteaseMusicDownloader()
print(a.getSongInfo(298317))
#print(a.getUrl_backup(26594185))
#print(a.search('bwv 1006'))
#print(a.search("周杰伦"))
print(a.getLyric(298317))
print(a.download(298317))
