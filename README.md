# BetfairExchange
A python api-wrapper for the Swedish betfair exchange api.

Full documentation and support can be found at https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni 

## How to set up for the Betfair exchange api
So in order to use the api you must enable non-Interactive (bot) login for your account and create a Self Signed Certificate.
You can enable this setting at My Details page on your betfair account.
To generate the Certificate you need to generate a RSA key pair using openssl by running the following command
```
openssl genrsa -out client-2048.key 2048
```
This may require you to override some default settings of openSSL which is done by creating a configuration file openssl.cnf with the following settings.
```
[ ssl_client ]
basicConstraints = CA:FALSE
nsCertType = client
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = clientAuth
```

After this is done you need to generate a certificate signing request file to verify identity.
```
openssl req -new -config openssl.cnf -key client-2048.key -out client-2048.csr
```

Here it is important that the information submitted matches your account settings.
The next step is to self-sign the certificate request to create a certificate used to verify yourself at the api endpoint.
```
openssl x509 -req -days 365 -in client-2048.csr -signkey client-2048.key -out client-2048.crt -extfile openssl.cnf -extensions ssl_client 
```

Once this certificate is generated log into your betfair account, go to My Details and upload your certificate by pressing edit under Automated Betting Program Access.
After this is done, the api should be functional and ready to use.

If having trouble during the verification, betfair has their own guide which can be found here https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/Non-Interactive+%28bot%29+login .



