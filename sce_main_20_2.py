# -*- coding: utf-8 -*-

''' --------------------------------------------------------------
	Simulation Store Stocks Model for SCE Core Assortment
	02/2018
	Retail Analytics
	for
	Tom Pichlmeier
	
	Christof Schatz
	
	Version: For variation of 2 simulation parameters	
	
	
	Next to do: 
	
	
    -------------------------------------------------------------- '''

from datetime import date
import sys
import os




outfname="G:\\data\order_20_2.csv"	

# Time a product should be sufficiently on store stock
P_coverdays=5
# Base amount (Sockelbestand)
P_sockel=1
# Backward Mean Quantity over n days as forecast
P_backday=10
# Delivery time in days from ZL to Store
P_deliveryday=1


P_promocut=11.0
P_promosubst=2.0


Cdate_id=0
Cday_of_week=1
Cavg_qty=2
Cqty_n2=3
Csales_qty2=4

O_date_id=0
O_stock=1
O_order=2
O_oos=3

B_order=0
B_stock=1
B_nstock=2
B_oos=3

class Check_dat:
	prod_id=0
	start1=1
	outlet_id=0
check_dat=Check_dat()


logf=open("G:\\data\\logf.txt","w")
logf.close()


#Order Container. Format: [date_id,prod_id,n_order]
zl_order={}

def	expected_sales(salesprod,iday):

	avg_qty=salesprod[iday][Cavg_qty]
	exp_qty=int(avg_qty*P_coverdays+0.5)
	
	#Backward mean:
	if (iday>0):
		sum1=0
		n=0
		n1=1
		n2=1
		idaystart=max(iday-P_backday,0)
		for x in salesprod[idaystart:iday+1]:
			sum1+=x[Csales_qty2]
			n+=1
		if n>0:
			back_forecast=sum1*1.0/n
	
		exp_qty2=int(back_forecast*P_coverdays+0.5)
	else:
		exp_qty2=-1
		
	exp_qty=max(exp_qty,exp_qty2)	
	
	return exp_qty
	
# ---------------------------------------------


def main_part(salesprod):

	# Process one product in one store
		
	#Expected Sales Quantity:
	# avg_qty=salesprod[0][Cavg_qty]
	
	exp_qty=expected_sales(salesprod,0)
	
	#Initial stocks
	stock=max(exp_qty,P_sockel)
	outdat=[]
	delivery=[0]*len(salesprod)
	#Ordered, but not delivered:
	ordered_stock=0
	
	#print check_dat.outlet_id
	
	
	k=0
	kmax=len(salesprod)-1
	for sp in salesprod:
				
		stock=stock-sp[Csales_qty2]+delivery[k]
		#If deliveries arrive, bookkeep them in the ordered_stock:
		ordered_stock-=delivery[k]
		if (ordered_stock<0):
			print("prod_id: "+check_dat.prod_id)
			print("date_id: "+sp[Cdate_id])
			sys.exit("Error: ordered_stock<0")
		#Check Order Size:
		exp_qty=expected_sales(salesprod,k)		
		order_size=max(max(exp_qty,P_sockel)-stock-ordered_stock,0)		
		# Notice: Stock can be negative!
		# orders are increased accordingly, but negative stocks are compensated only after
		# P_deliveryday
		# ##5
		if (k+P_deliveryday<=kmax and order_size>0): 
			delivery[k+P_deliveryday]=order_size
			ordered_stock+=order_size
		x=[-1]*3
		x[O_date_id]=salesprod[k][Cdate_id]
		x[O_stock]=stock
		x[O_order]=order_size
		outdat.append(x)

				
		
		date0=str2date2(sp[Cdate_id])
		#sp[Cdate_id]=='2017-04-10'
		if date0>=str2date2('2017-04-10') and date0<=str2date2('2017-04-14') and check_dat.prod_id=='491002958':
			###1
			outs=str(P_deliveryday)+";"+str(check_dat.outlet_id)+";"+sp[Cdate_id]+";"+str(stock)+";"+str(sp[Csales_qty2])+";"+str(delivery[k])+";"+str(ordered_stock)+";"+str(exp_qty)+";"+str(order_size)+"\n"
			logf.write(outs)
			
		
		
		k+=1
	
	return outdat	
	
	
# -----------------------------------

def str2date1(s):
	
	#For dates in the format "19.11.2016"

	date_s=s.split(".")
	date1=date(int(date_s[2]),int(date_s[1]),int(date_s[0]))
	return date1


	
# -----------------------------------
	
def write_data():

	ofi = open(outfname,'a')

	if check_dat.start1==1:	
		ofi.write("day_deliv;prod_id;week;Order;Stock;OOS\n")		
	
	for prodid in zl_order.keys():
	
		order0={}
				
		for date_s in zl_order[prodid].keys():
			week1=str2date2(date_s).isocalendar()[1]
			year1=str2date2(date_s).isocalendar()[0]
			dateweek=year1*100+week1
			if date_s=='2017-04-10' and prodid=='491002958':
				k=1
			
			#if (dateweek==201716)			:
			#	k=k;
			
			if dateweek in order0.keys():
				order0[dateweek][B_order]+=zl_order[prodid][date_s][O_order]
				order0[dateweek][B_stock]+=zl_order[prodid][date_s][O_stock]
				order0[dateweek][B_nstock]+=1
				order0[dateweek][B_oos]+=zl_order[prodid][date_s][O_oos]
			else:
				order0[dateweek]=[0]*4
				order0[dateweek][B_order]=zl_order[prodid][date_s][O_order]
				order0[dateweek][B_stock]=zl_order[prodid][date_s][O_stock]
				order0[dateweek][B_nstock]=1
				order0[dateweek][B_oos]=zl_order[prodid][date_s][O_oos]				
								
		for dateweek in sorted(order0.keys()):			
			stock=int(order0[dateweek][B_stock]*1.0/order0[dateweek][B_nstock]+0.5)
			oos=str(order0[dateweek][B_oos]*1.0/order0[dateweek][B_nstock]).replace('.',',')
			s=str(P_sockel)+";"+str(P_deliveryday)+";"+prodid+";"+str(dateweek)+";"+str(order0[dateweek][B_order])+";"+str(stock)+";"+oos+"\n"
			ofi.write(s)	
	
	ofi.close()	
		
	
# -----------------------------------	


# 0	date_id
# 1	prod_id
# 2	outlet_id
# 3	sales_val
# 4	sales_qty
# 5	day_of_week
# 6	mm_abs
# 7	avg_qty
# 8	qty_n1
# 9	qty_n2
# 10	sales_qty2
# 11	sales_val2
# 12	sales_val3
# 13	orderx1

def main_loop(ndeliveryday, nsocket):

	k=0
	#check1=0
	x=[]
	global zl_order
	zl_order={}
	
	global P_deliveryday
	P_deliveryday=ndeliveryday

	global P_sockel
	P_sockel=nsocket
	
	ifi = open('G:\\data\sales4_20_1.csv','r')
	for s in ifi:
		#if k>1000: break
		if k>0:
			dat=s.split(';')		
			if (k==1):
				prod_id1=dat[1]
				outlet_id1=dat[2]
			prod_id2=dat[1]			
			outlet_id2=dat[2]
			if prod_id1==prod_id2 and outlet_id1==outlet_id2:
				date_id=dat[0]
				day_of_week=int(dat[5])
				try:
					avg_qty=float(dat[7])
				except ValueError:
					avg_qty=0.0
					

				try:
					qty_n2=float(dat[9])
				except ValueError:
					qty_n2=0

				try:					
					sales_qty2=int(dat[10])		
				except ValueError:
					sales_qty2=0
				
				# Correction removal of promotion effects: 
				# In the database in case of promotion patterns the cut was done on P_promocut
				# not on P_promosubst
				if (qty_n2>P_promocut and sales_qty2>2):
					qty_n2=P_promosubst
					sales_qty2=int(qty_n2*avg_qty+0.5)

				x.append([date_id,day_of_week,avg_qty,qty_n2,sales_qty2])
								
			else:
				
				#Process Product in Store against sales data and get order sequence:
				
				check_dat.prod_id=prod_id1
				check_dat.outlet_id=outlet_id1
					
				store_order=main_part(x)					
				
				#Prepare zl_order container:
				if not prod_id1 in zl_order.keys():
					zl_order[prod_id1]={}
					#Temporary Record for zl_order:
					o={}
				else:
					o=zl_order[prod_id1]
					
				#Transfer to zentrallager_order
				for x1 in store_order:
					if x1[O_date_id] in o.keys():
						o[x1[O_date_id]][O_order]+=x1[O_order]
						o[x1[O_date_id]][O_stock]+=max(x1[O_stock],0)
						o[x1[O_date_id]][O_oos]+=min(x1[O_stock],0)
					else:
						o[x1[O_date_id]]=[0]*4						
						o[x1[O_date_id]][O_order]=x1[O_order]
						o[x1[O_date_id]][O_stock]=max(x1[O_stock],0)
						o[x1[O_date_id]][O_oos]=min(x1[O_stock],0)
						
					if o[x1[O_date_id]][O_oos]<0:
						k=k
				
				zl_order[prod_id1]=o
					
					
				if outlet_id1!=outlet_id2:
					print("day="+str(P_deliveryday)+" socket="+str(P_sockel)+" store="+outlet_id1+" done")
				#if prod_id1=="491052031":
				x=[]
				
			prod_id1=prod_id2
			outlet_id1=outlet_id2			
			
		k+=1
		
	ifi.close()
	
	write_data()
	
	check_dat.start1=0
	
def main1():
	
	os.system("del "+outfname)
	global logf
	logf=open("G:\\data\\logf.txt","w")
	main_loop(2,1)
	#main_loop(5,1)
	#main_loop(10,1)
	#main_loop(2,2)
	#main_loop(5,2)
	#main_loop(10,2)	
	#main_loop(2,3)
	#main_loop(5,3)
	#main_loop(10,3)
	
	logf.close()
	
main1()


