import urllib
import time
import psycopg2 as pg2
import sys
import datetime
import env

from urllib.request import urlopen
from bs4 import BeautifulSoup

print("PSYCOPG2 VERSION : " + pg2.__version__)

conn = None

stockCode = '005930' # Samsung Electronics

# Connect database
try :
    conn = pg2.connect("host=localhost dbname=testdb user=shinestar password=" + env.password)
    print("PSYCOPG2 : DB connect ok")

    cur = conn.cursor()
    cur.execute("CREATE TABLE samsung (id INTEGER PRIMARY KEY, date DATE, close INT, variation INT, open INT, high INT, low INT, volume INT)")

except pg2.DatabaseError as e:
    if conn:
        conn.rollback()
    print("ERROR %s" % e)
    sys.exit(1)


dayPriceUrl = 'http://finance.naver.com/item/sise_day.nhn?code=' + stockCode
dayPriceHtml = urlopen(dayPriceUrl)
dayPriceSource = BeautifulSoup(dayPriceHtml.read(), "html.parser")

dayPricePageNavigation = dayPriceSource.find_all("table", align="center")
dayPriceMaxPageSection = dayPricePageNavigation[0].find_all("td", class_="pgRR")
print(dayPriceMaxPageSection)
dayPriceMaxPageNum = int(dayPriceMaxPageSection[0].a.get('href')[-3:])

id_cnt = 0
for page in range(1, dayPriceMaxPageNum + 1):
    url = 'http://finance.naver.com/item/sise_day.nhn?code=' + stockCode + '&page=' + str(page)
    html = urlopen(url)
    source = BeautifulSoup(html.read(), "html.parser")
    srlists = source.find_all("tr")
    isCheckNone = None

    # day: 날짜
    # closingPrice: 종가
    # variation: 전일대비
    # openingPrice: 시가
    # highestPrice: 고가
    # lowestPrice: 저가
    # volume: 거래량

    for i in range(1, len(srlists) - 1): 
        if (srlists[i].span != isCheckNone):
            day = srlists[i].find_all("td", align="center")[0].text
            closingPrice = srlists[i].find_all("td", class_="num")[0].text

            srCompareWithYesterday = srlists[i].find("img")
            if (srCompareWithYesterday != None):
                incOrdec = srCompareWithYesterday.get("src")
                absoluteVariation = (srCompareWithYesterday.find("span").text).strip()  # 부호가 포함되지 않은 전일비

                absoluteVariation = absoluteVariation.replace(',','')

                if (incOrdec == "http://imgstock.naver.com/images/images4/ico_down.gif"):
                    variation = '-' + absoluteVariation
                    printVariation = int(absoluteVariation)*(-1)
                elif (incOrdec == "http://imgstock.naver.com/images/images4/ico_up.gif" or incOrdec == "http://imgstock.naver.com/images/images4/ico_up02.gif"):
                    variation = '+' + absoluteVariation
                    printVariation = int(absoluteVariation)
            else:
                variation = '0'
                printVariation = 0

            openingPrice = srlists[i].find_all("td", class_="num")[2].text
            highestPrice = srlists[i].find_all("td", class_="num")[3].text
            lowestPrice = srlists[i].find_all("td", class_="num")[4].text
            volume = srlists[i].find_all("td", class_="num")[5].text
            closingPrice = closingPrice.replace(',','')
            openingPrice = openingPrice.replace(',','')
            highestPrice = highestPrice.replace(',','')
            lowestPrice = lowestPrice.replace(',','')
            volume = volume.replace(',','')

            d_year = day[slice(0,4)]
            d_month = day[slice(5,7)]
            d_day = day[slice(8,10)]
            date_t = '{0}-{1}-{2}'.format(d_year,d_month,d_day)
            id_cnt = id_cnt + 1

            #cur.execute("INSERT INTO samsung VALUES(" + str(id_num) + "," + date_t + "," + closingPrice + "," + str(printVariation) + "," + openingPrice + "," + highestPrice + "," + lowestPrice + "," + volume + ")")
            cur.execute("""INSERT INTO samsung (id, date, close, variation, open, high, low, volume) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);""", (str(id_cnt),date_t,closingPrice,str(printVariation),openingPrice,highestPrice,lowestPrice,volume))

            print("날짜: " + day, end=" ")
            print("종가: " + closingPrice, end=" ")
            print("전일비: " + variation, end=" ")
            print("시가: " + openingPrice, end=" ")
            print("고가: " + highestPrice, end=" ")
            print("저가: " + lowestPrice, end=" ")
            print("거래량: " + volume)

cur.close()
conn.commit()
