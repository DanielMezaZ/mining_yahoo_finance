# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 20:28:13 2023

@author: jesus
"""
import numpy as np
import pandas as pd
import requests
import os.path, sys,time
import datetime
import csv
filePath="./symbols.csv"
    
def readSymbols():
    if os.path.isfile(filePath) != True:
        print(f"Error: File \"{filePath}\"does not exist")
        sys.exit()
    else: 
        df=pd.read_csv(filePath,sep=";",header=0,index_col=0)
        return df

def rUrl(symbol):
    return (
            "https://www.alphavantage.co/query?"
            "function="      "TIME_SERIES_DAILY_ADJUSTED"
            "&symbol="                        f"{symbol}"
            "&apikey="                 "ZENOGX48FP41TC2D"
            "&outputsize="                      "compact"
           )


class stockObj:
    def __init__(self,symbol):
        data = requests.get(rUrl(symbol)).json()
        if len(data)!=2:
            pd.DataFrame(df).to_csv(filePath,sep=';')
            print("Waiting for API (60s)")
            for i in range(4):
                time.sleep(15)
                print(str((i+1)*15)+"s")
            data = requests.get(rUrl(symbol)).json()
            if len(data)!=2:
                print("Error with the API")
                print(data)
                #pd.DataFrame(df).to_csv(filePath,sep=';')
                sys.exit()
        self.symbol=data['Meta Data']['2. Symbol']
        self.lastUpdate=data['Meta Data']['3. Last Refreshed']
        self.history=data['Time Series (Daily)']
        
    def getLastUpdate(self):
        return self.lastUpdate
    
    def print(self,k):
        df["Last Update"].values[k]=self.getLastUpdate()
        dateToday=datetime.datetime.today()
        print("########################################################")
        print(f"Symbol: {self.symbol}\nLast Update: {self.lastUpdate}\n")
        i=0
        j=0
        print("Date; Price")
        while i < 31:
            date=dateToday-datetime.timedelta(days = j)
            date=date.strftime('%Y-%m-%d')
            if date in self.history:
                price=self.history.get(date).get("4. close")
                df.iloc[k,i+6]=price
                print(f"{date}; {price}")
                i=i+1
                j=j+1
            else: j=j+1
        print("########################################################")


def updateSymbol(i):
    symbol=df["Symbol"].values[i]
    s=stockObj(symbol)
    s.print(i)
   
df=readSymbols()
a=df["Comment"].values
    
for i in range(np.size(df,0)):
   boolUpdate=False
   
   if df["Comment"].values[i] != "#":
       symbolDate=df["Last Update"].values[i]
       if not isinstance(symbolDate, str):
           boolUpdate=True
       else:
           symbolDate=datetime.datetime.strptime(symbolDate, '%Y-%m-%d')
           dif=datetime.datetime.today()-symbolDate
           if dif > datetime.timedelta(days = 5):
               boolUpdate=True
   if boolUpdate==True:
       updateSymbol(i)
    
pd.DataFrame(df).to_csv(filePath,sep=';')
    


