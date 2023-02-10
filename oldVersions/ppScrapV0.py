# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 11:49:27 2023

@author: jesus
"""
import numpy as np
import requests
import pandas as pd
import datetime, csv
from bs4 import BeautifulSoup

def histQuery(stock):
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
    r = requests.get(f"https://finance.yahoo.com/quote/{stock}/history?p={stock}",headers=headers)
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
    df = pd.DataFrame(output, columns=labels)
    return df
            
a=histQuery("IBM")

# Last close value of stock
# stock="AAPL"
# url2 = ('https://finance.yahoo.com/quote/')+stock+('?p=')+stock+('&.tsrc=fin-srch')
# res = requests.get(url2)
# webcont = BeautifulSoup(res.text,'lxml')
# webcont=webcont.find_all('td', attrs={'data-test' : 'PREV_CLOSE-value'})
# print(f"Stock: {stock}\nItem\t\t\tValue")
# for item in webcont:
#     print(f"{item['data-test']}\t\t\t{item.text}")