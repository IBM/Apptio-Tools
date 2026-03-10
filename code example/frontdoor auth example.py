import requests
import json


apptio_pub = '<insert frontdoor public key or ref to environment variable>'
apptio_priv = '<insert frontdoor private key or ref to environment variable>'
obtain_token_uri = "https://frontdoor.apptio.com/service/apikeylogin" 

##above frontdoor url may be different for different regions.  frontdoor-eu.apptio.com for emea, frontdoor-au.apptio.com for apac region

#need to obtain apptio-opentoken by posting the public/private keys
headers = {"Accept": "application/json", "content-type":"application/json"}
data = {
    "keyAccess": apptio_pub,
    "keySecret": apptio_priv
}
response = requests.post(obtain_token_uri, headers=headers, json=data)

apptio_token = response.headers['apptio-opentoken']
print('the auth token is '+str(apptio_token))

#Use token to get the Environment ID
apptio_api_header = {
    "Content-Type": "application/json",
    "apptio-opentoken": apptio_token
}

response = requests.get(f'https://frontdoor.apptio.com/api/environment/'+str(domain)+'/main', headers=apptio_api_header)
apptio_envid = response.json()['id']
print('the envid is '+str(apptio_envid))

##subsequently can pass the envid and the apptio_token as headers to API Calls for Cloudability or Apptio Uploader Service