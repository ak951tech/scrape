

from random import *

import time
import json
import requests
import os
from datetime import datetime, timedelta

def getSymbols():

    dictReturn      = {}
    filename        = 'data/symbols.json'
    fUpdateNeeded   = False

    if os.path.exists(filename):
        filetime    = datetime.fromtimestamp(os.path.getmtime(filename))
        expiration  = datetime.now() - timedelta(hours=24)

        if ( filetime < expiration ):
            fUpdateNeeded = True

    if ( fUpdateNeeded ):

        dictSymbolsEodHistorical    = {} # getSymbolsFromEodHistorical()
        dictSymbolsTwelveData       = getSymbolsFromTwelveData()

        dictReturn                  = dictSymbolsTwelveData     # better source at present

        if ( dictSymbolsEodHistorical ):
            listKeysEodHistorical = list(dictSymbolsEodHistorical.keys())

            # find and insert anything in EodHistorical that is not in TwelveData
            for symbol in listKeysEodHistorical:
                if ( symbol not in dictReturn ):
                    dictReturn[symbol] = dictSymbolsEodHistorical[symbol]

        with open(filename, 'w') as file:
            json.dump(dictReturn, file)

    else:
        with open(filename, 'r+') as file:
            dictReturn = json.load(file)



    return dictReturn




def getSymbolsFromEodHistorical():

    dictSymbols     = {}
    listExchanges   = ['US']
    sApiKey         = '603ef05b40b5c8.40877015'

    for exchange in listExchanges:

        nRetry = 0
        sUrl = 'https://eodhistoricaldata.com/api/exchange-symbol-list/{}?api_token={}&fmt=json'.format(exchange,sApiKey)

        while (nRetry < 5):
            try:
                response = requests.get(sUrl)

                if (response.status_code == 200):

                    listSymbols = json.loads(response.text)

                    for dictSymbol in listSymbols:
                        if (dictSymbol['Exchange'] in ['NYSE', 'NASDAQ', 'NYSE ARCA', 'BATS', 'NYSE MKT']):
                            if (dictSymbol['Type'] not in ['FUND', 'Fund', 'Mutual Fund']):

                                # normalize
                                dictSymbol['symbol']    = dictSymbol.pop('Code')
                                dictSymbol['name']      = dictSymbol.pop('Name')
                                dictSymbol['exchange']  = dictSymbol.pop('Exchange')
                                dictSymbol['country']   = dictSymbol.pop('Country')
                                dictSymbol['currency']  = dictSymbol.pop('Currency')
                                dictSymbol['type']      = dictSymbol.pop('Type')
                                dictSymbol['source']    = 'EodHistorical'

                                dictSymbols[dictSymbol['symbol']] = dictSymbol
                    break
                else:
                    pass

            except Exception as e:
                pass

            nRetry = nRetry + 1
            time.sleep(nRetry)


    return dictSymbols




def getSymbolsFromTwelveData():

    dictHttpResponse    = {}
    dictReturn          = {}
    nRetry              = 0
    sUrl                = 'https://api.twelvedata.com/stocks?source=docs'

    while (nRetry < 5):

        try:
            response = requests.get(sUrl)
            if (response.status_code == 200):
                dictHttpResponse = json.loads(response.text)
                break
            else:
                pass

        except Exception as e:
            pass

        nRetry = nRetry + 1
        time.sleep(nRetry)

    # normalize results
    if ( bool(dictHttpResponse) ):
        listSymbols = dictHttpResponse['data']

        for dictSymbol in listSymbols:

            if ( dictSymbol['country'].find('United States')!=-1 ):
                dictSymbol['country'] = 'USA'

            if ( dictSymbol['type'].upper()=='EQUITY' ):
                dictSymbol['type'] = 'Common Stock'
            elif ( dictSymbol['type'].upper().find('EXCHANGE')!=-1 and dictSymbol['type'].upper().find('TRADED')!=-1 ):
                dictSymbol['type'] = 'ETF'
            elif (dictSymbol['type'].find('REIT') != -1 ):
                dictSymbol['type'] = 'REIT'

            dictSymbol['source'] = 'TwelveData'

            if ( dictSymbol['country'] == 'USA' ):
                dictReturn[dictSymbol['symbol']] = dictSymbol

    return dictReturn

