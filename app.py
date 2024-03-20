#importing the libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
#import seaborn as sns
#sns.set(style='darkgrid',context='talk', palette='Dark2')
from flask import Flask,render_template,request
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
from sklearn import metrics

#reading the database
df=pd.read_excel('Datasets/dbmain.xlsx')
df2=pd.read_excel('Datasets/data_test.xlsx')
df3=pd.read_csv('Datasets/Inventory Dataset.csv')
inventdb=df3.to_html()

#all variables
allproducts=list(df.columns)#list of all products in the sold till date
allproducts.remove('Day')#list of all products excluding day
highdemand=[]#after using EMA analysis, the products which are found to have a high ongoing demand(period is 7days)
veryhighdemand=[]#after using EMA analysis, the products which are found to have a very high ongoing demand(period is 7days)
lowdemand=[]#products which have demand lower than the requirement for high demand
veryhighdemand_special=[]#very highly demanded goods with approaching expiry
highdemand_special=[]#highly demanded goods with approaching expiry
lowdemand_special=[]#low demand goods approaching expiry
endangered_names=['Paracetamol','Fenoprofen']#list of all products approaching expiry
endangeredcount=len(endangered_names)
endangered_dates=['31-10-2021','25-09-2021']#list of expiry dates of all products
#login-register information
username=[]
password=[]
mobileno=[]
ans=''





#calculating total sales of the month
for cost in df2['Total Cost']:#making all the values positive
  cost=np.absolute(cost)
totsales=df2['Total Cost'].sum()
totsales=int(totsales)
print(totsales)



#main model
def model(productname):
	highprofit=0#required for classifying the demand
	profit=0
	loss=0
	ema_short = df[productname].ewm(span=20, adjust=True).mean()
	ema_short=ema_short.tolist()
	ema_mid = df[productname].ewm(span=70, adjust=True).mean()
	ema_mid=ema_mid.tolist()
	ema_long=df[productname].ewm(span=120,adjust=True).mean()
	ema_long=ema_long.tolist()

	#last week sales
	lwsales=df[productname][-7:].sum()
	#Prediction for a month 
	X=df['Day']
	Y=df[productname]
	lasso=Lasso(alpha=1.0)

	#prediction for a week
	for day in range(8):
		d=day-7
		if (ema_mid[d]>ema_long[d]):
			if (ema_short[d]>ema_mid[d]):
				highprofit=highprofit+1
			else:
				profit+=1
		else:
			loss+=1


	if highprofit>=5:
		'''demandstate='The product',productname,'is in very high demand'''
		veryhighdemand.append(productname)
	elif profit>loss:
		highdemand.append(productname)
		'''demandstate='The product',productname,'is in high demand'''
	else:
		lowdemand.append(productname)
		'''('The product',productname,'is in low demand')'''

	if productname in endangered_names:
		if productname in veryhighdemand:
			ans='Chill! Your product is nearing expiry, but it is running on very high demand. You may sell it on the MRP or slightly lesser if you please!:)'
		elif productname in highdemand:
			ans='Your product is nearing expiry, but it is running on a fairly high demand. We suggest you keep it on discounted rates.'
			
		else:
			ans='Your product is nearing expiry, but it is running on a low demand. We strongly suggest you keep it on a sale and try selling it away within',"expirydate"
			


for item in allproducts:
	model(item)
#for p in veryhighdemand:
#	x=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
#	y=np.array(df[p][-7:])
#	plt.xticks(rotation='60')
#	plt.plot(x,y)
#	plt.savefig('static/plot_{p}.png'.format(p=p))



















app=Flask(__name__)

@app.context_processor
def utility_processor():
	def model(productname):
		highprofit=0#required for classifying the demand
		profit=0
		loss=0
		ema_short = df[productname].ewm(span=20, adjust=True).mean()
		ema_short=ema_short.tolist()
		ema_mid = df[productname].ewm(span=70, adjust=True).mean()
		ema_mid=ema_mid.tolist()
		ema_long=df[productname].ewm(span=120,adjust=True).mean()
		ema_long=ema_long.tolist()

		#last week sales
		lwsales=df[productname][-7:].sum()
		#Prediction for a month
		X=df['Day']
		Y=df[productname]
		lasso=Lasso(alpha=1.0)

		#prediction for a week
		for day in range(8):
			d=day-7
			if (ema_mid[d]>ema_long[d]):
				if (ema_short[d]>ema_mid[d]):
					highprofit=highprofit+1
				else:
					profit+=1
			else:
				loss+=1


		if highprofit>=5:
			'''demandstate='The product',productname,'is in very high demand'''
			veryhighdemand.append(productname)
		elif profit>loss:
			highdemand.append(productname)
			'''demandstate='The product',productname,'is in high demand'''
		else:
			lowdemand.append(productname)
			'''('The product',productname,'is in low demand')'''

		if productname in endangered_names:
			if productname in veryhighdemand:
				ans='Chill! Your product is nearing expiry, but it is running on very high demand. You may sell it on the MRP or slightly lesser if you please!:)'
			elif productname in highdemand:
				ans='Your product is nearing expiry, but it is running on a fairly high demand. We suggest you keep it on discounted rates.'

			else:
				ans='Your product is nearing expiry, but it is running on a low demand. We strongly suggest you keep it on a sale and try selling it away within',"expirydate"
	return {'model':model}


@app.route('/')
@app.route('/login.html')
def index():
  return render_template("login.html")
@app.route('/register.html')
def register():
  return render_template('register.html',username=username,password=password,mobileno=mobileno)

@app.route('/index.html')
def dashboard():

	labels=['Monday','Tuesday','Wednesday','Thursday','Friday']
	values=list(df['Aceclofenac'][-7:])

	
	return render_template("index.html",endangeredcount=endangeredcount,demandedgoods=veryhighdemand,totalsales=totsales,endangered_dates=endangered_dates,endangered_names=endangered_names,highdemand_special=highdemand_special,veryhighdemand_special=veryhighdemand_special,lowdemand_special=lowdemand_special,veryhighdemand=veryhighdemand,labels=labels,values=values)

#@app.route('/Database-inventory')
#def db():
#  return render_template('inventory.html')
@app.route('/sales.html')
def sales():
  return render_template('blank.html',df3=df3)

@app.route('/err404')
@app.route('/404.html')
def err404():
  return render_template('404.html')


@app.route('/forgot-password.html')
def forgotpassword():
  return render_template('forgot-password.html')

@app.route('/inventory.html')
def inventory():
	return render_template('inventory.html',df3=df3,ans=ans)


if __name__=='__main__':
  app.run(debug=True)









