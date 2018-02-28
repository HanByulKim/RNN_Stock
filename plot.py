import matplotlib.pyplot as plt
import matplotlib.finance as matfin
import matplotlib.ticker as ticker
import psycopg2 as pg2
import numpy as np
import env
import datetime

def candle(conn):
    cur = conn.cursor()
    cur.execute("""SELECT open FROM samsung""")
    open = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT high FROM samsung""")
    high = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT low FROM samsung""")
    low = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT close FROM samsung""")
    close = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT date FROM samsung""")
    date = np.array(cur.fetchall())[:,0]

    day_list = []
    name_list = []

    for i, day in enumerate(date):
        if day.weekday() == 0:
            day_list.append(i)
            name_list.append(day.strftime('%Y-%m-%d') + '(Mon)')

    fig = plt.figure(figsize=(24,16))
    ax = fig.add_subplot(111)

    ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

    matfin.candlestick2_ohlc(ax, np.ndarray.tolist(open[::-1]), np.ndarray.tolist(high[::-1]), np.ndarray.tolist(low[::-1]), np.ndarray.tolist(close[::-1]), width=0.5, colorup='r', colordown='b')

    plt.show()

conn = pg2.connect("host=localhost dbname=testdb user=shinestar password=" + env.password)
print("PSYCOPG2 : DB connect ok")

candle(conn)

#for row in rows:
#    candle(ax, str(row[4]), str(row[5]), str(row[6]), str(row[2]))
#plt.show()