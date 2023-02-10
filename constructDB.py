# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 20:28:13 2023

@author: jesus
"""
# %% Import libraries

import numpy as np
import pandas as pd
import requests
import os.path, sys
import datetime
from bs4 import BeautifulSoup

# %% Import data
typeList=["Main","Close","High","Low","Open","Volume"]
yahooLabels=np.array(["Date","Open","High","Low","Close*",\
                      "Adj Close**","Volume"])
def gFilePath(type):
    if type in typeList:
        #output=f"./output{type}.csv"   
        ## Swap comment to write output in another file
        output=f"./symbols{type}.csv"
        return output
    else:
        print ("Error, file name not in type list")
        sys.exit()
        
def readSymbols(type):
    filePath=gFilePath(type)
    if os.path.isfile(filePath) != True:
        print(f"Error: File \"{filePath}\"does not exist")
        sys.exit()
    else: 
        df=pd.read_csv(filePath,sep=";",header=0,index_col=0)
        return df

# Read all files
dfMain=readSymbols("Main")
dfClose=readSymbols("Close")
dfOpen=readSymbols("Open")
dfLow=readSymbols("Low")
dfHigh=readSymbols("High")
dfVolume=readSymbols("Volume")

# %% Stock Obj

class stockObj:
    def __init__(self,symbol):
        self.symbol=symbol
        today=datetime.datetime.today()
        self.lastUpdate=today.strftime("%d.%m.%Y %H:%M")
        self.history= self.getData(symbol)
    
    def getData(self,symbol):
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                 'AppleWebKit/537.36 (KHTML, like Gecko) '
                 'Chrome/98.0.4758.102 Safari/537.36'}
        # Most time consuming task!! >90%
        r = requests.get("https://finance.yahoo.com/"
                         f"quote/{symbol}"
                         f"/history?p={symbol}"
                         ,headers=headers)
        #print(r)
        soup = BeautifulSoup(r.content,'lxml')
        soup=soup.find_all('table', attrs={'data-test' : "historical-prices"})
        #print(soup)
        labels=np.array([])
        output=np.array([[],[]])
        row=np.array([])
        for item in soup:
            for sitem in item:
                for ssitem in sitem:
                    row=np.array([])
                    for sssitem in ssitem:
                        row=np.append(row,sssitem.text)
                    #print(row)
                    if labels.size==0:
                        labels=row
                    elif output.size==0:
                        output=row
                    elif row.size==7:
                        output=np.vstack([output, row])
        if output.size==0 or output.size==1:
            output=np.zeros((99,7))
            labels=yahooLabels
        df = pd.DataFrame(output, columns=labels)
        return df
    
    def getLastUpdate(self):
        return self.lastUpdate
    
    def print(self,ind):
        lastUpdate=dfMain.loc[ind,'Last Update']
        dfMain.loc[ind,"Last Update"]=self.getLastUpdate()

        #print(self.history)
        if len(self.history.index) ==99:
            name=dfMain.loc[ind,'Name']
            sym=dfMain.loc[ind,'Symbol']
            entry=np.array([name,sym])
            values=np.append(entry,np.array(self.history["Close*"].values))
            dfClose.loc[[ind]]=values
            values=np.append(entry,np.array(self.history["Open"].values))
            dfOpen.loc[[ind]]=values
            values=np.append(entry,np.array(self.history["High"].values))
            dfHigh.loc[[ind]]=values
            values=np.append(entry,np.array(self.history["Low"].values))
            dfLow.loc[[ind]]=values
            values=np.append(entry,np.array(self.history["Volume"].values))
            dfVolume.loc[[ind]]=values
        else:
            for j in range(len(self.history.index)-2):
                dfOpen.iloc[ind-1,j+2]=self.history["Open"].values[j]
                dfHigh.iloc[ind-1,j+2]=self.history["High"].values[j]
                dfLow.iloc[ind-1,j+2]=self.history["Low"].values[j]
                dfClose.iloc[ind-1,j+2]=self.history["Close*"].values[j]
                dfVolume.iloc[ind-1,j+2]=self.history["Volume"].values[j]

        print("########################################################")
        print(f"Symbol: {self.symbol} ({ind})\nPrevious Update: {lastUpdate}\n")
        print(f"Last Open:   {self.history['Open'].values[0]}")
        print(f"Last High:   {self.history['High'].values[0]}")
        print(f"Last Low:    {self.history['Low'].values[0]}")
        print(f"Last Close:  {self.history['Close*'].values[0]}")
        print(f"Last Volume: {self.history['Volume'].values[0]}")
        print("########################################################")

#%% Other functions

def updateSymbol(ind):
    symbol=dfMain.loc[ind,'Symbol'] #iloc? It works
    # Create object
    s=stockObj(symbol)
    # Update object
    s.print(ind)
 
def securityCopy():
    # Call after all operations were completed
    timeSinceSC=datetime.datetime.now()-lastSC
    limitWithoutSC=datetime.timedelta(days = int(updateSCCrit))
    if timeSinceSC > limitWithoutSC:
        today=datetime.datetime.now()
        today=today.strftime("%d_%m_%Y")
        filePath=f"./backUps/{today}_Main.csv"
        pd.DataFrame(dfMain).to_csv(filePath,sep=';')
        filePath=f"./backUps/{today}_Open.csv"
        pd.DataFrame(dfOpen).to_csv(filePath,sep=';')
        filePath=f"./backUps/{today}_Close.csv"
        pd.DataFrame(dfClose).to_csv(filePath,sep=';')
        filePath=f"./backUps/{today}_High.csv"
        pd.DataFrame(dfHigh).to_csv(gFilePath("High"),sep=';')
        filePath=f"./backUps/{today}_Low.csv"
        pd.DataFrame(dfLow).to_csv(filePath,sep=';')
        filePath=f"./backUps/{today}_Volume.csv"
        pd.DataFrame(dfVolume).to_csv(filePath,sep=';')
        today=datetime.datetime.now()
        today=today.strftime("%d.%m.%Y %H:%M")
        dfConfig["Last security copy (d.m.Y H:M)"].values[0]=today

def saveDataFrames():
    # Call to save progress in the csv file
    pd.DataFrame(dfMain).to_csv(gFilePath("Main"),sep=';')
    pd.DataFrame(dfOpen).to_csv(gFilePath("Open"),sep=';')
    pd.DataFrame(dfClose).to_csv(gFilePath("Close"),sep=';')
    pd.DataFrame(dfHigh).to_csv(gFilePath("High"),sep=';')
    pd.DataFrame(dfLow).to_csv(gFilePath("Low"),sep=';')
    pd.DataFrame(dfVolume).to_csv(gFilePath("Volume"),sep=';')
    
# %% Main

startTime=datetime.datetime.now()

# Read configuration file
dfConfig=pd.read_csv("config.csv",sep=";",header=0)
if len(dfConfig.index) != 1:
    print("Error: config.csv file contains more than one entry")
    sys.exit()
else:
    noUpdates=dfConfig["Save every No Updates"].values[0]
    updateSCCrit=dfConfig["Security Copy every (days)"].values[0]
    updateEntriesCrit=dfConfig["Update every (days)"].values[0]
    lastSC=dfConfig["Last security copy (d.m.Y H:M)"].values[0]
    lastSC=datetime.datetime.strptime(lastSC, "%d.%m.%Y %H:%M")


updatesCounter=0     
limDate=datetime.timedelta(days = int(updateEntriesCrit))
limDate=datetime.datetime.today()-limDate

# Start loop coverin all symbols in the main file
for i in range(np.size(dfMain,0)):
   boolUpdate=False
   print(i+1)
   # Checl if commented out
   if dfMain["Comment"].values[i] != "#":
       symbolDate=dfMain["Last Update"].values[i]
       # Make sure that date is a string or update (usage: missing dates!)
       if not isinstance(symbolDate, str):
           boolUpdate=True
       else:
           symbol=dfMain["Symbol"].values[i] #Not used
           # Update if data is older that one day
           symbolDate=datetime.datetime.strptime(symbolDate, "%d.%m.%Y %H:%M")
           # If critical, update
           if symbolDate < limDate: 
               boolUpdate=True
       # Update if the boolUpdate flag is activated
       if boolUpdate==True:
           updatesCounter=updatesCounter+1
           # Using index instead of row number for flexibility,
           # The symbol could also work
           ind=dfMain.index.values[i]
           updateSymbol(ind)
       # Save progress every noUpdates 
       if updatesCounter%noUpdates==0: #Save progress every ten updates
           saveDataFrames()
# Final save and check for a security copy
saveDataFrames()
securityCopy()

# Save some relevant data to config.csv
endTime=datetime.datetime.now()-startTime
dfConfig["Last executtion time"].values[0]=endTime
dfConfig["Last number of updates"].values[0]=updatesCounter    
pd.DataFrame(dfConfig).to_csv("config.csv",sep=';')
print(f"Done\nExecution time: {endTime}\nEntries updated: {updatesCounter}")
    