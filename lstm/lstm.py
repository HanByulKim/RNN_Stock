import numpy as np
import pandas as pd
from sklearn import preprocessing
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers.recurrent import LSTM
from keras.layers import Dropout
import psycopg2 as pg2
import env
import plot
import matplotlib.ticker as mtick

# Log
file = open("log/result.txt","w")

conn = pg2.connect("host=localhost dbname=testdb user=shinestar password=" + env.password)
print("PSYCOPG2 : DB connect ok")

train_size = 250
all = []
all = plot.candle(conn,train_size)
all_pd = pd.DataFrame(np.atleast_2d(all))
print(all_pd)

# how many data we will use (should not be more than length)
data_to_use = len(all[:])
 
# number of training data (should be less than data_to_use)
train_end = data_to_use-train_size

total_data=len(all[:])
print("total_data : " + str(total_data))

# most recent data is in the end (so need offset)
start=total_data - data_to_use

#currently doing prediction only for 1 step ahead
steps_to_predict =1
a=all_pd[2]
b=all_pd[7]
c=all_pd[4]
d=all_pd[5]
e=all_pd[6]
print ("close head :")
print (a.head())
 
close_ = a.shift(-1)

data = pd.concat ([a, close_, b, c, d, e], axis =1)
data.columns = ['close', 'close_', 'volume', 'open', 'high', 'low']

data = data.dropna()
print (data)
     
# target variable - closed price (after shifting)
y = data ['close_']
cols =['close', 'volume', 'open', 'high', 'low']
x = data [cols]

scaler_x = preprocessing.MinMaxScaler(feature_range=(-1,1))
x = np.array(x).reshape((len(x) ,len(cols)))
x = scaler_x.fit_transform(x)

scaler_y = preprocessing.MinMaxScaler(feature_range=(-1,1))
y = np.array(y).reshape((len(y),1))
y = scaler_y.fit_transform(y)
     
x_train = x [0: train_end,]
x_test = x[ train_end +1:len(x),]    
y_train = y [0: train_end] 
y_test = y[ train_end +1:len(y)]  
x_train = x_train.reshape (x_train. shape + (1,)) 
x_test = x_test.reshape (x_test. shape + (1,))

seed =2016
np.random.seed (seed)
fit1 = Sequential ()
fit1.add (LSTM (  1000 , activation = 'tanh', inner_activation = 'hard_sigmoid' , input_shape =(len(cols), 1) ))
fit1.add(Dropout(0.2))
fit1.add (Dense (output_dim =1, activation = 'linear'))
 
fit1.compile (loss ="mean_squared_error" , optimizer = "adam")   
fit1.fit (x_train, y_train, batch_size =16, nb_epoch =25, shuffle = False)
 
print (fit1.summary())
 
score_train = fit1.evaluate (x_train, y_train, batch_size =1)
score_test = fit1.evaluate (x_test, y_test, batch_size =1)
print (" in train MSE = ", round( score_train ,4)) 
print (" in test MSE = ", score_test )
   
pred1 = fit1.predict (x_test) 
pred1 = scaler_y.inverse_transform (np. array (pred1). reshape ((len( pred1), 1)))

prediction_data = pred1[-1]     

fit1.summary()
print ("Inputs: {}".format(fit1.input_shape))
print ("Outputs: {}".format(fit1.output_shape))
print ("Actual input: {}".format(x_test.shape))
print ("Actual output: {}".format(y_test.shape))
file.write("Inputs: {} \n".format(fit1.input_shape))
file.write("Outputs: {} \n".format(fit1.output_shape))
file.write("Actual input: {} \n".format(x_test.shape))
file.write("Actual output: {} \n".format(y_test.shape))   
 
print ("Prediction data:")
print (*prediction_data)
file.write("Predction data : ")
file.write(str(prediction_data))
file.write("\n")
 
 
print ("Actual data : ")
x_test = scaler_x.inverse_transform (np.array (x_test). reshape ((len( x_test), len(cols))))
print (*x_test)
file.write("Actual data : ")
#file.write(x_test)
file.write("\n")
 
plt.plot(pred1, label="predictions")
 
plt.plot( [row[0] for row in x_test], label="actual")

plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05),
          fancybox=True, shadow=True, ncol=2)
 
fmt = '$%.0f'
tick = mtick.FormatStrFormatter(fmt)
 
ax = plt.axes()
ax.yaxis.set_major_formatter(tick)

file.close()
plt.show()
