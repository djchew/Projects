import numpy as np
import statistics
from sklearn.metrics import mean_squared_error, explained_variance_score
from sklearn.model_selection import train_test_split
from sklearn.utils import shuffle
from sklearn.linear_model import LinearRegression
from sklearn.datasets import make_regression
from sklearn.metrics import accuracy_score

from sklearn import preprocessing
import matplotlib.pyplot as plt
import yfinance as yf
import datetime
from datetime import datetime, date, timedelta
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
from pandas import DataFrame
import tkinter as tk
from tkinter import filedialog
from sklearn import model_selection
import os
from csv import reader

# Define start and end dates
start = datetime(2017, 1, 1)
end = datetime.now()

# Open file
# print("Current Working Directory " , os.getcwd())
# os.chdir(r'c:\Users\darre\OneDrive - The University of Melbourne\Personal\yfinance3')
# file = open('prospective_interests.csv', mode = 'r', encoding = 'utf-8-sig')
# lines = file.readlines()
# stocks = []
# with open('prospective_interests.csv', 'r') as read_obj:
#     csv_reader = reader(read_obj)
#     for row in csv_reader:
#         print(row)
#         stocks.append(row)


# stocks[0][0] = stocks[0][0][3:]

# individual_stocks = []
# for each_list in stocks:
#     individual_stocks.append(each_list[0])

# print(individual_stocks)
# for each_stock in individual_stocks:
#     # input_stock = input("What stock are you looking at? ")
#     tickerData = yf.Ticker(each_stock + ".AX")
input_stock = input("What stock are you looking at? ")    
tickerData = yf.Ticker(input_stock + ".AX")  
# #     #Outputting the Historical data into a .csv for later use
input_interval = "1d"
input_days = input("How many days? ")

df = tickerData.history(period= input_interval , start= start, end= end)
# path = r'c:\Users\darre\OneDrive - The University of Melbourne\Personal\yfinance3'
# output_file = os.path.join(path, each_stock + "_history" + "_" + input_interval + ".csv")

df.to_csv(input_stock + "_history" + "_" + input_interval + ".csv", sep = ',', encoding='utf-8', index=False)

# Create pop up window to save csv
# root= tk.Tk()

# canvas1 = tk.Canvas(root, width = 300, height = 300, bg = 'lightsteelblue2', relief = 'raised')
# canvas1.pack()

# def exportCSV ():
#     global df
    
#     export_file_path = filedialog.asksaveasfilename(defaultextension='.csv')
#     df.to_csv (export_file_path, index = False, header=True)

# saveAsButton_CSV = tk.Button(text='Export CSV', command=exportCSV, bg='green', fg='white', font=('helvetica', 12, 'bold'))
# canvas1.create_window(150, 150, window=saveAsButton_CSV)

# root.mainloop()


df['prediction'] = df['Close'].shift(-1)
df.dropna(inplace=True)

forecast_time = int(input_days)


print(df)
# #Predicting the Stock price in the future
X = np.array(df.drop(['prediction'], 1))
Y = np.array(df['prediction'])
X = preprocessing.scale(X)
X_prediction = X[-forecast_time:]
X_train, X_test, y_train, y_test = model_selection.train_test_split(X,Y, train_size=0.6, test_size=0.4, random_state=100)
# X_train, Y_train, Y_test = model_selection.train_test_split(
#     X, Y, test_size=0.5)

#Performing the Regression on the training data
clf = LinearRegression()
clf.fit(X_train, y_train)
prediction = (clf.predict(X_prediction))

print(input_stock + " prediction: ", prediction[::-1])

# last_row = df.tail(1)
# print(last_row['Close'])

