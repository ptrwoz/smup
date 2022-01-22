import os


import json
import urllib.request
with open('newsmup.json', 'rb') as f:
    byte_Obj = f.read()
json_string = byte_Obj.decode("ascii", "ignore")
info = json.loads(json_string)

newdata = open('newsmup.json', 'wb')
newdata.write(bytes(json_string,"ascii"))
newdata.close()
exit()