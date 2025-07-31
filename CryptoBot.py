import ccxt
import time
import datetime
import pandas as pd
from ta.momentum import RSIIndicator
from plyer import notification
from openai import OpenAI
import os
from dotenv import load_dotenv

#loads the Binance and ChatGPT API
load_dotenv()
gptAPI = OpenAI(api_key = os.getenv('API'))
binanceAPI = ccxt.binanceus()

#Function to ask ChatGPT and receive a response
def askGPT (price, rsi, coin):
    GPTprompt = f'Based on the {price}, {rsi}, and market value of this {coin} at this exact moment, should I buy, sell, or hold that coin.'
    
    GPTresponse = gptAPI.chat.completions.create(
        model = 'gpt-4o',
        messages = [{'role': 'system', 'content': "You're a crypto trading professional that gives concise, smart advice based on all market trends."}, {'role': 'user', 'content': GPTprompt}]
        )

    return GPTresponse.choices[0].message.content

#Hourly loop that fetches data from Binance and feeds it into the askGPT function for a response. The response is displayed as form of a Window's desktop notification
while True:
    dataReq = binanceAPI.fetch_ohlcv('BTC/USDT', '1h', limit = 100)
    dataSpread = pd.DataFrame(dataReq, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    dataSpread['datetime'] = pd.to_datetime(dataSpread['timestamp'], unit='ms')

    close = dataSpread['close']
    
    rsiData = RSIIndicator(close, window = 14).rsi().iloc[-1]
    priceData = close.iloc[-1]
    
    GPTadvice = askGPT(priceData, rsiData, 'BTC/USDT')
    
    notification.notify(
        title = 'Trading Advice!',
        message = GPTadvice,
        timeout = 10
    )

    time.sleep(3600)