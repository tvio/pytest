
#delat na mimorande oprave 
#udelat menu na vytvoreni procesu
#delat na PUT cokoliv
#dalat na UC prohazovani dat POST > Prohlaseni > etc.
from contextlib import contextmanager
from pathlib import Path
from tempfile import NamedTemporaryFile

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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

# config
#pracoviste je natvrdo spojene s certem
pracoviste = '00150017164'
url = 'https://testapi.sukl.cz/reg13/v3'   
timeout = (5,5)
podaniID = str(uuid.uuid4())


#prechod na session, jinak pada na timeout
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


def auth():
 with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as  c:
  global cert
  cert = c 


def doReq(htmlOperace,operace,data={}):
  if htmlOperace=='get':
   res = session.get(url+operace,cert=cert,timeout=timeout)
  elif htmlOperace=='post':
   res = session.post(url+operace,cert=cert,timeout=timeout,json=data)
  elif htmlOperace=='delete':
   res = session.delete(url+operace,cert=cert,timeout=timeout,)
  elif htmlOperace=='put':
   res = session.put(url+operace,cert=cert,timeout=timeout,json=data)
  
  return res
def loadJSON(soubor):
    with  open(soubor,'r') as f:
     data = json.load(f)
     return data

#nacte privni kod pracoviste podle typu
def nactiKodPracoviste(typ,**kwargs):
     if 'kodPracoviste' in kwargs:
       kodPracoviste= str(kwargs.get('kodPracoviste'))
       res = doReq('get','/pracoviste/'+str(typ)+'?kodPracoviste='+kodPracoviste)
       printRes('nactiKodPracovsteJedenKod>>'+kodPracoviste,res)
     elif 'ico' in kwargs:
       ico= str(kwargs.get('ico'))
       res = doReq('get','/pracoviste/'+str(typ)+'?ico='+ico)
       printRes('nactiKodPracovsteJednoICO>>'+ico,res)
     else:
      res = doReq('get','/pracoviste/'+str(typ))
      resjson = res.json()
      firstKod = resjson[0]['kodPracoviste']
      return firstKod
    
def printRes(operace,res,**kwargs):
   print('operace'+operace)
   if 'req' in kwargs:
      print('req>>'+str(kwargs.get("req")))
   print('res>>'+res.text)
   print('statusCode>>'+str(res.status_code))

#delete s getem Id   
def delete(rok,mesic):
   res = doReq('get','/hlaseni/'+pracoviste+'/rok/'+rok+'/mesic/'+mesic)
   printRes('getID podle data a kodu pracoviste',res)
   if res.text =='[]':
     print(' log - Hlaseni neexistuje , neni co mazat')
   else:
    resjson = res.json()[0]
    res =  doReq('delete','/hlaseni/'+resjson )
    printRes('deleteHlaseni',res)

#hlavni post
def postHlaseni(typ,obdobi):
   postHlaseniJSON = loadJSON('postHlaseni.json')
   postHlaseniJSON["podaniID"]  = podaniID
   postHlaseniJSON['reglp'][0]["polozkaID"] = str(uuid.uuid4())
   postHlaseniJSON["obdobi"] = obdobi
   if typ=='dis':
     postHlaseniJSON['reglp'][0]["kodPracoviste"] = nactiKodPracoviste(1)
     postHlaseniJSON['reglp'][0]["typHlaseni"] = (1)
   elif typ=='lek':
     postHlaseniJSON['reglp'][0]["kodPracoviste"] = nactiKodPracoviste(2)
     postHlaseniJSON['reglp'][0]["typHlaseni"] = (2) 
   res = doReq('post','/hlaseni',data=postHlaseniJSON)
   printRes('postHlaseni',res,req=postHlaseniJSON)
#test bez kodu pracoviste   
def bezKoduPrac(obdobi):
  
  with pfx_to_pem('MAHSUKL150017166G.pfx', 'Test1234') as cert:
   #status
   res =  requests.get(url+'/Status', cert=cert )
   printRes('status',res)
   #post  
   postHlaseniJSON = loadJSON('postHlaseni.json')
   postHlaseniJSON["podaniID"]  = podaniID
   postHlaseniJSON['reglp'][0]["polozkaID"] = str(uuid.uuid4())
   postHlaseniJSON["obdobi"] = obdobi
   postHlaseniJSON.pop("kodPracoviste")  
   #postHlaseniJSON["kodPracoviste"]=""
   res = requests.post(url+'/hlaseni',cert=cert,json=postHlaseniJSON)
   printRes('postHlaseni',res,req=postHlaseniJSON)
   
def nactiHlaseniPodleID():
  res = doReq('get','/hlaseni/'+podaniID)
  printRes('getHlaseniPodleID',res)


auth()
#vezme prvni pracoviste dis z ciselniku praocvist
delete('2024','06')
postHlaseni(typ='dis',obdobi='202406')
nactiHlaseniPodleID()
#vezme prvni pracoviste lek z ciselniku pracovist
#postHlaseni(typ='lek',mesic='202404')
#smaze hlaeni za konrketni mesic
#delete('2024','03');
#bezKoduPrac('202404')
#nactiKodPracoviste(2,ico='27460894
