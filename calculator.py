#！ -*- coding: utf-8 -*-
import sys
import csv
from collections import namedtuple

#使用namedtuple存储个税速查表，包含三个属性，应纳税所得额（门槛），税率，速算扣除数
TaxLookupItem =  namedtuple(
	'TaxLookupItem',
	['StartPoint','TaxRate','QuickDeduction']
)

#个税起征点3500
TaxStartPoint = 3500

#存储个税速查表
IncomeTaxLookupTable = [
	TaxLookupItem(80000, 0.45, 13505),
	TaxLookupItem(55000, 0.35, 5505),
	TaxLookupItem(35000, 0.30, 2755),
	TaxLookupItem(9000, 0.25, 1005),
	TaxLookupItem(4500, 0.20, 555),
	TaxLookupItem(1500, 0.10, 105),
	TaxLookupItem(1500, 0.3, 0),
]

#处理命令行参数类
class Args(object):

	#初始化时读取命令行所有参数到self.args列表中
	def __init__(self):
		self.args = sys.argv[1:]

	#提取参数-c,-d,-o后面的值
	def _value_after_option(self, option):
		try:
			#首先获得参数的索引值：
			index = self.args.index(option)
			#参数所在位置下一个的字符串就是所需的文件路径
			return self.args[index + 1]
		except (ValueError, IndexError):
			#如果获取出错，自动打印错误信息并退出
			print('Parameter Error')
			exit()
	
	#获取 -c 参数对应的值，即配置文件的路径
	@property
	def config_path(self):
		return self._value_after_option('-c')
	
	#获取 -d 参数对应的值，即用户数据文件的路径
	@property
	def userdata_path(self):
		return self._value_after_option('-d')

	#获取 -o 参数对应的值，即输出的用户工资单文件的路径
	@property
	def export_path(self):
		return self._value_after_option('-o')

	