import requests
from bs4 import BeautifulSoup
import json
import urllib.parse
import re
from js2py import eval_js

class Decipher:
    '''
    Returns Deciphered Signature using the Algo provided in the JavaScript File
    '''
    def __init__(self, js: str = None, signature: str = None, process=False):
        if process is True:
            self.js = js.replace('\n', '')
            self.signature = signature
            self.main_js = self.get_main_function(js)
            self.var_name,  self.func = self.get_algo_data(self.main_js)
            self.alog_js = self.get_full_function()
        else:
            pass

    def get_main_function(self, js: str):
        # js contains the javascript from YouTube
        # Returns the main Javascript function that has subfunctions
        main_func = re.search(r"[\{\d\w\(\)\\.\=\"]*?;(..\...\(.\,..?\)\;){3,}.*?}", js)[0]
        return main_func

    def get_algo_data(self, main_js: str):
        """
        Returns :  The name of the Variable and Function that contain actual decipher algo
        """
        main_func = main_js
        variable = re.findall(r'(\w\w)\...', main_func)[0]
        var_regex = r"var "+variable+r"={.+?};"
        func = re.findall(var_regex, self.js)[0]
        var_name = main_func.split('=')[0].split(' ')[-1]
        return [var_name, func]

    def get_full_function(self):
        # Return the Final JS function to be executed to decipher the signature
        full_func = self.main_js+";"+self.func+';var output = {0}("{1}");'.format(self.var_name, self.signature)
        return full_func

def download(url):

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    scripts = soup.find_all('script')
    for script in scripts:
        if script.text.startswith("var ytInitialPlayerResponse"):
            ytInitialPlayerResponse = json.loads(script.text.replace('var ytInitialPlayerResponse = ', "").replace('};', "}"))
        try:
            if "/player/" in script.get("src"):
            #     print(script)
                playerUrl = "https://www.youtube.com" + script.get("src")
        except TypeError:
            continue

    player = requests.get(playerUrl)
    for video in ytInitialPlayerResponse["streamingData"]["adaptiveFormats"]:
        if "audio" in video["mimeType"]:           
            signatureCipher = video["signatureCipher"]
            break
    signatureCipher = urllib.parse.unquote(signatureCipher)
    sig = signatureCipher.split("&sp=sig&url=")
    func = Decipher(player.text, signature=sig[0].replace("s=",""), process=True)
    output = eval_js(func.get_full_function())
    print(output)
    print()
    print(sig[1])
    print()
    return (sig[1] + "&sig=" + output)
    
rick = 'https://www.youtube.com/watch?v=rUfB5ZogzB4'
print(download(rick))