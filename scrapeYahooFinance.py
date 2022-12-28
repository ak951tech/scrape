


#from random import *
from datetime import datetime

import time
import json
import requests
import symbols
from bs4 import BeautifulSoup
import os
import random

def getClassificationDataOld(varSymbol):

    listUrls = []

    listUrls.append('https://finance.yahoo.com/quote/{}/profile?p={}')
    listUrls.append('https://finance.yahoo.com')
    listUrls.append('https://finance.yahoo.com/news/')
    listUrls.append('https://finance.yahoo.com/tech')
    listUrls.append('https://finance.yahoo.com/quote/{}/analysis?p={}')

    nMaxRequests    = randint(2,3)
    nRequest        = 0
    indexPrevious   = -1

    while (True):
        time.sleep(randint(3,5))

        if ( nRequest==nMaxRequests ):
            index = 0
        else:
            index = randint(0, len(listUrls) - 1)

            while ( True ):
                if ( index != indexPrevious ):
                    break
                else:
                    index = randint(0, len(listUrls) - 1)

        indexPrevious = index

        sUrl    = listUrls[index]
        sUrl    = sUrl.format(varSymbol, varSymbol)

        # print(varSymbol,datetime.now(),sUrl)

        httpResponseText = makeHttpRequest(sUrl)

        if ( httpResponseText != '' ):
            if ( index==0 ):
                return extractClassificationData(httpResponseText)
            else:
                pass
        else:
            return None

        nRequest = nRequest + 1




def getData(varSymbol):

    dictReturn = {}

    listUrls = []

    listUrls.append('https://finance.yahoo.com/quote/{}/profile?p={}')
    listUrls.append('https://finance.yahoo.com/quote/{}?p={}')

    listOptionalUrls = []
    listOptionalUrls.append('https://finance.yahoo.com/quote/{}/analysis?p={}')
    listOptionalUrls.append('https://finance.yahoo.com')
    listOptionalUrls.append('https://finance.yahoo.com/news/')
    listOptionalUrls.append('https://finance.yahoo.com/tech')

    random.shuffle(listOptionalUrls)
    listOptionalUrls = listOptionalUrls[0:random.randint(1,3)]

    listUrls.extend(listOptionalUrls)
    random.shuffle(listUrls)


    for url in listUrls:
        time.sleep(random.randint(1,4))

        print('\tb')


        url = url.format(varSymbol, varSymbol)
        httpResponseText = makeHttpRequest(url)

        if url.find('profile')!=-1:
            dictTemp = extractClassificationData(httpResponseText)
        elif url.find('quote')!=-1 and url.find('profile')==-1 and url.find('analysis')==-1:
            dictTemp = extractSummaryData(httpResponseText)
        else:
            dictTemp = None
            pass

        if dictTemp!=None:
            for key in dictTemp:
                dictReturn[key] = dictTemp[key]

    dictReturnSorted = {}

    for key in sorted(dictReturn.keys()):
        dictReturnSorted[key] = dictReturn[key]
        print('\tc')

# git remote add origin https://github.com/ak951tech/scrape.git
    return dictReturnSorted













def extractClassificationData(varHttpResponseText):

    dictReturn = {}
    dictReturn['sector']        = ''
    dictReturn['industry']      = ''
    dictReturn['description']   = ''

    if (varHttpResponseText != ''):

        try:
            soup                        = BeautifulSoup(varHttpResponseText, "html.parser")  # "lxml" "html.parser"

            sector                      = soup.find('span',text='Sector(s)').nextSibling.nextSibling.text
            industry                    = soup.find('span',text='Industry').nextSibling.nextSibling.text
            description                 = soup.find('span',text='Description').parent.nextSibling.text

            dictReturn = {}
            dictReturn['sector']        = sector.replace('\u2014', '-')
            dictReturn['industry']      = industry.replace('\u2014', '-')
            dictReturn['description']   = description.replace('\u2014', '-')[:255]

        except Exception as e:
            print('yahoo exception: {}'.format((str(e))))

    return dictReturn


def extractSummaryData(varHttpResponseText):

    dictReturn = {}
    dictReturn['marketCap']        = -1
    dictReturn['avgVolume']        = -1

    if (varHttpResponseText != ''):

        try:
            soup = BeautifulSoup(varHttpResponseText, "html.parser")  # "lxml" "html.parser"

            #temp = varHttpResponseText.find('<span>Avg. Volume</span>')
            #temp = varHttpResponseText[temp:temp+500]

            try:
                marketCap = soup.find('span',text='Market Cap')
                marketCap = marketCap.parent.nextSibling.text
                marketCap = marketCap.replace('.','').replace(',','')
                marketCap = marketCap.replace('M', '000000').replace('B', '000000000').replace('T', '000000000000')
                dictReturn['marketCap'] = int(marketCap)
            except:
                pass

            try:
                avgVolume = soup.find('span',text='Avg. Volume')
                avgVolume = avgVolume.parent.nextSibling.text
                avgVolume = avgVolume.replace('.','').replace(',','')
                avgVolume = avgVolume.replace('M', '000000').replace('B', '000000000')
                dictReturn['avgVolume'] = int(avgVolume)
            except:
                pass

        except Exception as e:
            print('yahoo exception: {}'.format((str(e))))

    return dictReturn


def makeHttpRequest(varUrl):

    httpResponseText = ''
    httpStatusCode = -1

    try:
        response = requests.get(
            varUrl,
            headers={
                # ':scheme'         : 'https',
                # ':authority'      : 'udc.yahoo.com',
                # 'Host'            : 'udc.yahoo.com',
                'Accept'            : '*/*',
                'Origin'            : 'https://finance.yahoo.com',
                'Accept-Language'   : 'en-us',
                'Referer'           : varUrl,
                'Accept-Encoding'   : 'gzip, deflate, br',
                'Connection'        : 'keep-alive',
                'User-Agent'        : getUserAgent()
            })

        httpStatusCode = response.status_code
        if (httpStatusCode == 200):
            httpResponseText = response.text
    except Exception as e:
        print('scrape encountered error making http request: {}, {}').format(httpStatusCode,str(e))


    return httpResponseText



def getUserAgent():

    sReturn         = ''
    listUserAgents  = []

    listUserAgents.append('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15')
    listUserAgents.append('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299')
    listUserAgents.append('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36')
    listUserAgents.append('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:70.0) Gecko/20100101 Firefox/70.0')
    listUserAgents.append('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36')
    listUserAgents.append('Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0')

    countUserAgents = len(listUserAgents)
    if ( countUserAgents ):
        index = random.randint(0,countUserAgents-1)
        sReturn = listUserAgents[index]

    return sReturn



def loop():

    dictClassificationData  = {}
    dictSymbols             = symbols.getSymbols()
    listSymbols             = []

    for symbol in dictSymbols:

        if (dictSymbols[symbol]['exchange'].upper() not in ['NYSE', 'NASDAQ']
            # or dictSymbols[symbol]['type'].upper() != 'COMMON STOCK'
            or len(symbol) > 4):
            continue
        else:
            listSymbols.append(symbol)


    filename        = 'data/classificationData.json'

    dictClassificationData = {}

    if os.path.exists(filename):
        with open(filename, 'r+') as file:
            dictClassificationData = json.load(file)

    for count,symbol in enumerate(listSymbols):
        print('\ta')
        if symbol not in dictClassificationData:
            dictClassificationData[symbol] = getData(symbol)

        if count%10==0:
            with open(filename, 'w') as file:
                json.dump(dictClassificationData, file)

            time.sleep(random.randint(1, 3))

        print(count,symbol)


loop()





