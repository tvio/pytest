from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
import uuid
import json
from cryptography.hazmat.primitives.serialization import Encoding, PrivateFormat, NoEncryption
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates


@contextmanager
def pfx_to_pem(pfx_path, pfx_password):
    ''' Decrypts the .pfx file to be used with requests. '''
    pfx = Path(pfx_path).read_bytes()
    private_key, main_cert, add_certs = load_key_and_certificates(pfx, pfx_password.encode('utf-8'), None)

    with NamedTemporaryFile(suffix='.pem',delete=False) as t_pem:
        with open(t_pem.name, 'wb') as pem_file:
            pem_file.write(private_key.private_bytes(Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()))
            pem_file.write(main_cert.public_bytes(Encoding.PEM))
            for ca in add_certs:
                pem_file.write(ca.public_bytes(Encoding.PEM))
        yield t_pem.name

# HOW TO USE:

url = 'https://testapi.sukl.cz/reg13/v3'   


def loadJSON(soubor):
    f = open(soubor)
    data = json.load(f)
    f.close()
    return data

#nacte privni kod pracoviste podle typu
def nactiKodPracoviste(typ,ico=None,kodPracoviste=None):
     res = requests.get(url+'/pracoviste/'+str(typ),cert=cert)
     resjson = res.json()
     firstKod = resjson[0]['kodPracoviste']
     return firstKod
    
def printRes(operace,res):
   print('operace'+operace)
   print('res>>'+res.text)
   print('statusCode>>'+str(res.status_code))
   


def mainUC():
  with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as cert:
   #status
   res =  requests.get(url+'/Status', cert=cert )
   printRes('status',res)
   #post  
   postHlaseniJSON = loadJSON('postHlaseni.json')
   postHlaseniJSON["podaniID"]  = str(uuid.uuid4())
   postHlaseniJSON['reglp'][0]["kodPracoviste"] = nactiKodPracoviste(2)
   print(postHlaseniJSON)
   res = requests.post(url+'hlaseni',cert=cert,json=postHlaseniJSON)
   printRes('postHlaseni',res)


mainUC()