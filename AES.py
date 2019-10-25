# -*- coding: utf-8 -*-
import base64
import hashlib

from Crypto.Cipher import AES

class AESCipher(object):
    def __init__(self, key):
        self.key = bytes(key,'utf-8')

    @staticmethod
    def padding(s):
        """
        ensure len(s) % 16 = 0
        """
        s = bytes(s, 'utf-8')
        return s + (16 - len(s) % 16) * bytes(chr(16 - len(s) % 16),'utf-8')

    def encrypt(self, raw, iv):
        raw = self.padding(raw)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(cipher.encrypt(raw)).decode('utf-8')
