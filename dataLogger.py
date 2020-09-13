from apiHandler import BetFairApiHndler
import pandas as pd
import sys
from Exceptions import LoginException, RequestException
from datetime import datetime, timedelta
import json
import sched, time

class DataLogger():
    '''
        Logs data from the Betfair Exchange API and stores in csv-files
    '''

    def __init__(self,my_username,my_password,app_key):
        self.api = BetFairApiHndler(my_username,my_password,app_key)

    def _timeUntil(self,startTime,roundTo=1):
        crntTime = datetime.now()
        crntTime = crntTime - timedelta(seconds=crntTime.second%roundTo,microseconds = crntTime.microsecond)
        startTime = datetime.strptime(startTime,'%Y-%m-%d %H:%M:%S')
        timeToStart = startTime-crntTime
        return timeToStart

    def startLogging(self,sample_every = 60, duration =24, folder = './Logs'):
        print('starting to run logger..')
        print('To stop process press ctrl+z in terminal')
        print('Data is stored in csv files in the designated folder specified')
        print('Three csv files will be stored')
        ### Initiate Datastructures
        # Set up timeFrame
        start = timedelta()
        time_intervl = timedelta(seconds = sample_every)
        tot_samples = int(duration*3600/sample_every)
        time_samples = [str(start+(tot_samples-i)*time_intervl) for i in range(tot_samples)]
        empty_row = {time:None for time in time_samples}
        # save market to csv File
        runners, markets, marketData = self.getMarketData()
        marketTimeseries = pd.DataFrame(columns = time_samples, index = marketData.index)
        markets.to_csv(folder+'AvalibleGames.csv')
        runners.to_csv(folder+'AvalibleOdds.csv')
        marketTimeseries.to_csv(folder+'marketTimeseries.csv')

        crntTime = datetime.now()
        timeToNextMin = timedelta(seconds = 60-crntTime.second)
        print(timeToNextMin.seconds)
        time.sleep(timeToNextMin.seconds)
        while True:
            # crntTime = datetime.now()
            # crntMin = crntTime - timedelta(seconds=crntTime.second,milliseconds=crntTIme.millisecond)
            print('Time:'+datetime.now().strftime('%Y-%m-%d %H:%M'))
            timeToNextMin = timedelta(seconds = 60-datetime.now().second)
            print(timeToNextMin.seconds)
            time.sleep(timeToNextMin.seconds)



        ## Sample new Data and enter into samples
        # while true:
        #     pass


        # for marketId, row in markets.iterrows():
        #     timeToStart = self._timeUntil(row['marketStartTime'],roundTo = sample_every)
        #     print(marketVolumes[marketId])
        #     if(marketId not in volumes_Timeseries.index):
        #         volumes_Timeseries.loc[marketId] = empty_row
            # volumes_Timeseries[marketId]['totalAvailable'][timeTostart] = marketVolumes[(marketId,'totalAvailable')]
            # volumes_Timeseries[marketId]['totalMatched'][timeTostart] = marketVolumes[(marketId,'totalMatched')]

        # print(volumes_Timeseries)


    def getMarketData(self,inPlay=False,eventTypeIds = [2], marketTypeCodes = ['MATCH_ODDS']):
        # Get current avalible markets and sort relevant data
        marketCataloge = self.api.getMarketCatalogue(filter = {"eventTypeIds":eventTypeIds,'inPlayOnly':inPlay, 'marketTypeCodes':marketTypeCodes},maxresults=400, sort="FIRST_TO_START",marketProjection=['EVENT','MARKET_START_TIME','COMPETITION','RUNNER_DESCRIPTION'])
        runners = {(market['marketId'],run['selectionId']):{'runnerName':run['runnerName']} for market in marketCataloge for run in market['runners']}
        runners = pd.DataFrame.from_dict(runners,orient='index')
        markets = {}
        for market in marketCataloge:
            mrktName=market['marketName']
            marketId = market['marketId']
            comp = market['competition']['name']
            compId = market['competition']['id']
            evntNme = market['event']['name']
            evntId = market['event']['id']
            # Adjust to the our timezone
            marketStartTime = datetime.strptime(market['marketStartTime'],'%Y-%m-%dT%H:%M:%S.%fZ')
            marketStartTime = str(marketStartTime+timedelta(hours=2))
            markets[marketId] = {   'name':evntNme,
                                    'eventId':evntId,
                                    'Market Name':mrktName,
                                    'competition':comp,
                                    'competition id': compId,
                                    'marketStartTime':marketStartTime,}
        markets = pd.DataFrame.from_dict(markets, orient='index')
        # Get current Odds and volumes
        marketIds = list(markets.index)
        marketBooks = self.api.getMarketBooks(marketIds,PriceData='EX_BEST_OFFERS',orderProjection='EXECUTABLE')
        # Get Market volumes
        marketData = {}
        for mb in marketBooks:
            marketId = mb['marketId']
            marketData[(marketId,'totalMatched')] =  mb['totalMatched']
            marketData[(marketId,'totalAvailable')] =  mb['totalAvailable']
            for run in mb['runners']:
                lastPriceTrded = None if ('lastPriceTraded' not in run) else run['lastPriceTraded']
                marketData[(marketId,run['selectionId'])] = lastPriceTrded
        marketData = pd.Series(marketData)
        return runners, markets, marketData



if __name__=='__main__':
    my_username = sys.argv[1]
    my_password = sys.argv[2]
    app_key = "BF1R7et3n1XVYycB"
    try:
        lgr = DataLogger(my_username,my_password,app_key)
        lgr.startLogging(folder = './Logs/TennisOddsTimeseries')
    except LoginException as e:
        print(e.message)
    except RequestException as e:
        print(e.message)
