import matplotlib.pyplot as plt
import matplotlib.finance as matfin
import matplotlib.ticker as ticker
import psycopg2 as pg2
import numpy as np
import env
import datetime

def candle(conn, size):
    cur = conn.cursor()
    cur.execute("""SELECT open FROM samsung ORDER BY id DESC""")
    open = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT high FROM samsung ORDER BY id DESC""")
    high = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT low FROM samsung ORDER BY id DESC""")
    low = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT close FROM samsung ORDER BY id DESC""")
    close = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT date FROM samsung ORDER BY id DESC""")
    date = np.array(cur.fetchall())[:,0]
    cur.execute("""SELECT volume FROM samsung ORDER BY id DESC""")
    volume = np.array(cur.fetchall())[:,0]

    day_list = []
    name_list = []

    for i, day in enumerate(date[len(date)-size:]):
        if day.weekday() == 0:
            day_list.append(i)
            name_list.append(day.strftime('%m/%d'))

    fig = plt.figure(figsize=(24,16))
    ax = fig.add_subplot(111)

    ax.xaxis.set_major_locator(ticker.FixedLocator(day_list))
    ax.xaxis.set_major_formatter(ticker.FixedFormatter(name_list))

    matfin.candlestick2_ohlc(ax, np.ndarray.tolist(open[len(date)-size:]), np.ndarray.tolist(high[len(date)-size:]), np.ndarray.tolist(low[len(date)-size:]), np.ndarray.tolist(close[len(date)-size:]), width=0.5, colorup='r', colordown='b')

    plt.title('Samsung Electronics ' + str(size) + ' Days')
    plt.show()
    plt.gcf().clear()
    cur.execute("""SELECT * FROM samsung ORDER BY id DESC""")
    all = np.array(cur.fetchall())[:,:]

    return all

#__main__
#conn = pg2.connect("host=localhost dbname=testdb user=shinestar password=" + env.password)
#print("PSYCOPG2 : DB connect ok")

#candle(conn)
