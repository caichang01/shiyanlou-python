#!/usr/bin/env python3

import sys

try:
	income = int(sys.argv[1]) - 3500
	if income  <= 1500:
		tax = (income * 0.03) - 0
	elif income <= 4500:
		tax = (income * 0.10) - 105
	elif income <= 9000:
		tax = (income * 0.20) - 555
	elif income <= 35000:
		tax = (income * 0.25) - 1005
	elif income <= 55000:
		tax = (income * 0.30) - 2755
	elif income <= 80000:
		tax = (income * 0.35) - 5505
	else:  
		tax = income * 0.45 - 13505
	print(format(tax,".2f"))
except:
	print("Parameter Error")
