import json
import datetime
import urllib
import urllib.request
import urllib.error
import requests
import pandas as pd
import sys
from Exceptions import *

class BetFairApi:

    def __init__(self, username,password, app_key, SafeMode=True):
        self.payload = 'username=' + username + '&password=' + password
        self.initheaders = {'X-Application': app_key, 'Content-Type': 'application/x-www-form-urlencoded'}
        self.bet_url = 'https://api.betfair.com/exchange/betting/json-rpc/v1'
        self.headers = headers = {'X-Application': app_key, 'content-type':'application/json'}
        self.login()

    def login(self):
        self.bet_url = 'https://api.betfair.com/exchange/betting/json-rpc/v1'
        resp = requests.post('https://identitysso-cert.betfair.se/api/certlogin',
                                data=self.payload,
                                cert=('AppCert.crt','client-2048.key'),
                                headers=self.initheaders)
        json_resp=resp.json()
        if json_resp['loginStatus'] != 'SUCCESS':
            raise LoginException("Login failed, status:"+str(json_resp['loginStatus']))
        SSOID = json_resp['sessionToken']
        self.headers['X-Authentication'] = SSOID
        self.logedin = True

    def logout(self):
        headers = { 'X-Application': self.headers['X-Application'],
                    'X-Authentication': self.headers['X-Authentication'],
                    'Accept': 'application/json'}
        resp = requests.post("https://identitysso.betfair.com/api/logout",headers= headers)
        if(resp.status_code!=200):
            raise LoginException("Failed to logout:"+str(json_resp['loginStatus']))
        self.logedin = False

    def keepAlive(self):
        resp = requests.post("https://identitysso.betfair.com/api/keepAlive",headers= self.headers)
        if(resp.status_code!=200):
            raise LoginException("Failed to keep token alive:"+str(json_resp['loginStatus']))

    def _request(self,reference,params):
        paramstmp = json.dumps(params)
        usr_req = '{"jsonrpc":"2.0", "method":"SportsAPING/v1.0/'+reference+'", "params":'+paramstmp+', "id":"1"}'
        req = requests.post(self.bet_url, data = usr_req.encode('utf-8'),headers= self.headers)
        resp = req.json()
        if "error" in resp:
            raise RequestException(str(resp['error']['code']))
        return resp

    def getEventTypes(self,filter = {}, **kwargs):
        '''
            Get existent EventTypes.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listEventTypes
        '''
        params = {**{"filter":filter}, **kwargs}
        eventTypes = self._request(reference = 'listEventTypes',params=params)
        eventTypes = [{**eventType['eventType'], 'marketCount':eventType['marketCount']} for eventType in eventTypes['result']]
        return eventTypes

    def getEvents(self,filter = {}, **kwargs):
        '''
            Get current events avalible.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listEvents
        '''
        params = {**{"filter":filter}, **kwargs}
        req_data = self._request(reference = 'listEvents',params=params)
        events = req_data['result']
        return events

    def getMarketTypes(self,filter={},**kwargs):
        '''
            Get Markettypes avalible.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listMarketTypes
        '''
        params = {**{"filter":filter}, **kwargs}
        req_data = self._request(reference = 'listMarketTypes',params=params)
        markettypes = req_data['result']
        return markettypes

    def getCountries(self,filter={},**kwargs):
        '''
            Get Country and number of events of that country.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listCountries
        '''
        params = {**{"filter":filter}, **kwargs}
        req_data = self._request(reference = 'listCountries',params=params)
        Countries = [req for req in req_data['result']]
        return Countries

    def getCompetition(self,filter={},**kwargs):
        '''
            Get list of current Competitions.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listEventTypes
        '''
        params = {**{"filter":filter}, **kwargs}
        comps = self._request(reference = 'listCompetitions',params=params)
        # comps =  [{**comp['competition'], 'marketCount':comp['marketCount']} for comp in comps['result']]
        return comps['result']

    def getMarketCatalogue(self,filter={},maxResults ="100",**kwargs):
        '''
            Get a Catalogue of current Markets avalible.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listMarketCatalogue
        '''
        params = {**{"filter":filter, 'maxResults':maxResults}, **kwargs}
        cata = self._request(reference = 'listMarketCatalogue',params=params)
        return cata['result']

    def getListTimeRanges(self,filter={}, granularity = "MINUTES",**kwargs):
        params = {**{"filter":filter, 'granularity':granularity}, **kwargs}
        data = self._request(reference = 'listMarketCatalogue',params=params)
        return data['result']

    def getMarketBooks(self, marketIds,**kwargs):
        '''
            Get MarketBook for an lost of specifed market.
            Observe that it is limited to 100 requests

            Separate requests should be made for OPEN & CLOSED markets.
            Request that include both OPEN & CLOSED markets will only return those markets that are OPEN.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listMarketBook
        '''
        nmbrIds = len(marketIds)
        lim = 100
        batches = [marketIds[i*lim:min((i+1)*lim,nmbrIds)] for i in range(0,nmbrIds//lim+1)]
        marketBooks = []
        for batch in batches:
            params = {**{"marketIds":batch}, **kwargs}
            req_data = self._request(reference = 'listMarketBook',params=params)
            marketBooks = marketBooks+req_data['result']

        return marketBooks

    def getMarketBookRunners(self, marketId, **kwargs):
        '''
            Get Runners for a marketbook for an speciifed market.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listMarketBook
        '''
        params = {**{"marketIds":[marketId]}, **kwargs}
        req_data = self._request(reference = 'listMarketBook',params=params)
        runners = [req['runners'] for req in req_data['result']][0]
        return runners

    def getRunnerBook(self,marketId,selectionId,**kwargs):
        '''
            Get information about a RunnerBook for speciifed market and selectionId.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listRunnerBook
        '''
        params = {**{"marketId":marketId, 'selectionId':selectionId}, **kwargs}
        req_data = self._request(reference = 'listRunnerBook',params=params)
        return req_data['result']

    def getMarketProfitAndLoss(self,marketIds,**kwargs):
        '''
            Get current market profits and losses for market specified by marketIds.
            doc:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listMarketProfitAndLoss
        '''
        params = {**{"marketIds":marketIds}, **kwargs}
        req_data = self._request(reference = 'listMarketProfitAndLoss',params=params)
        marketProfitAndLoss = req_data['result']
        return marketProfitAndLoss

    def getCurrentOrders(self,**kwargs):
        '''
            Get your current orders:
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listCurrentOrders
        '''
        params = kwargs
        req_data = self._request(reference = 'listCurrentOrders',params=params)
        crntOrders = req_data['result']
        return crntOrders

    def getClearedOrders(self,betStatus="SETTLED",**kwargs):
        '''
            Get list of Orders who are "SETTLED", "VOIDED" by betfair,"LAPSED" aka cancelled by betfair or "CANCELLED" by user.
            docs:
                https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listClearedOrders
        '''
        params = {**{"betStatus":betStatus}, **kwargs}
        req_data = self._request(reference = 'listClearedOrders',params=params)
        clrOrders = req_data['result']
        return clrOrders

    def PlaceOrder(self,marketId,placeInstructions = {},**kwargs):
        pass

    def cancelOrder(self,**kwargs):
        '''
            Cancel an order by specifying the marketID or if left empty cancel ALL orders.
        '''
        pass
