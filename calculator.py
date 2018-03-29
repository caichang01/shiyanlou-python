#！ -*- coding: utf-8 -*-
import sys
import csv

def TaxCalculate(name, tax_income):
	if tax_income < 0:
		income = 0
	else:
		income = tax_income
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
		tax = (income * 0.45) - 13505
	sallary = format(tax_income + 3500 -tax, ".2f")
	str1 = name + ':' + sallary
	print(str1)

try: 
	for arg in sys.argv[1:]:
		params = arg.split(':')
		name = params[0]
		income = int(params[1])
		tax_income = (income * (1 - 0.08 - 0.02 - 0.005 - 0.06)) -3500
		TaxCalculate(name, tax_income)

except:
	print("Parameter Error")
