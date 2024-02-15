#nemam dodelany deleta s getem ID
#nemam dodelany test bez kodu pracoviste
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

#pracoviste je natvrdo spojene s certem
pracoviste = '00150017164'
url = 'https://testapi.sukl.cz/reg13/v3'   


def loadJSON(soubor):
    with  open(soubor,'r') as f:
     data = json.load(f)
     return data

#nacte privni kod pracoviste podle typu
def nactiKodPracoviste(typ,ico=None,kodPracoviste=None):
  with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as cert:
     res = requests.get(url+'/pracoviste/'+str(typ),cert=cert)
     resjson = res.json()
     firstKod = resjson[0]['kodPracoviste']
     return firstKod
    
def printRes(operace,res,**kwargs):
   print('operace'+operace)
   if 'req' in kwargs:
      print('req>>'+str(kwargs.get("req")))
   print('res>>'+res.text)
   print('statusCode>>'+str(res.status_code))
   
def delete(rok,mesic):
 with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as cert:
   res = requests.get(url+'/hlaseni/'+pracoviste+'/rok/'+rok+'/mesic/'+mesic)
   print(res.)
   res =  requests.delete(url+'/hlaseni'+str(podaniID), cert=cert )
   printRes('deleteHlaseni',res)

#mainUC
def sKodemPrac(typ,mesic):
  
  with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as cert:
   #status
   res =  requests.get(url+'/Status', cert=cert )
   printRes('status',res)
   #post  
   postHlaseniJSON = loadJSON('postHlaseni.json')
   postHlaseniJSON["podaniID"]  = str(uuid.uuid4())
   postHlaseniJSON['reglp'][0]["polozkaID"] = str(uuid.uuid4())
   postHlaseniJSON["obdobi"] = mesic
   if typ=='dis':
     postHlaseniJSON['reglp'][0]["kodPracoviste"] = nactiKodPracoviste(2)
     postHlaseniJSON['reglp'][0]["typHlaseni"] = (1)
   elif typ=='lek':
     postHlaseniJSON['reglp'][0]["kodPracoviste"] = nactiKodPracoviste(1)
     postHlaseniJSON['reglp'][0]["typHlaseni"] = (2) 
   res = requests.post(url+'/hlaseni',cert=cert,json=postHlaseniJSON)
   printRes('postHlaseni',res,req=postHlaseniJSON)
#test bez kodu pracoviste   
def bezKoduPrac(typ,mesic):
  
  with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as cert:
   #status
   res =  requests.get(url+'/Status', cert=cert )
   printRes('status',res)
   #post  
   postHlaseniJSON = loadJSON('postHlaseni.json')
   postHlaseniJSON["podaniID"]  = str(uuid.uuid4())
   postHlaseniJSON['reglp'][0]["polozkaID"] = str(uuid.uuid4())
   postHlaseniJSON["obdobi"] = mesic
   if typ=='dis':
     postHlaseniJSON['reglp'][0]["kodPracoviste"] = ''
     postHlaseniJSON['reglp'][0]["typHlaseni"] = (1)
   elif typ=='lek':
     postHlaseniJSON['reglp'][0]["kodPracoviste"] = ''
     postHlaseniJSON['reglp'][0]["typHlaseni"] = (2) 
   res = requests.post(url+'/hlaseni',cert=cert,json=postHlaseniJSON)
   printRes('postHlaseni',res,req=postHlaseniJSON)
   

#mainUC(typ='dis',mesic='202403')
#mainUC(typ='lek',mesic='202404')
bezKodu