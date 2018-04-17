#！ -*- coding: utf-8 -*-
import sys
import csv
import queue
import configparser
from getopt import getopt, GetoptError
from datetime import datetime
from collections import namedtuple
from multiprocessing import Process, Queue

# 使用namedtuple存储个税速查表，包含三个属性，应纳税所得额（门槛），税率，速算扣除数
TaxLookupItem =  namedtuple(
	'TaxLookupItem',
	['StartPoint','TaxRate','QuickDeduction']
)

# 个税起征点3500
TaxStartPoint = 3500

# 存储个税速查表
IncomeTaxLookupTable = [
	TaxLookupItem(80000, 0.45, 13505),
	TaxLookupItem(55000, 0.35, 5505),
	TaxLookupItem(35000, 0.30, 2755),
	TaxLookupItem(9000, 0.25, 1005),
	TaxLookupItem(4500, 0.20, 555),
	TaxLookupItem(1500, 0.10, 105),
	TaxLookupItem(0, 0.3, 0),
]

# 创建两个队列，一个交换用户数据，一个交换工资数据
q_userdata = Queue()
q_result = Queue()

# 处理命令行参数类
class Args(object):

	# 初始化时读取命令行所有参数到self.args列表中
	def __init__(self):
		self.options = self._options()

	
	def _options(self):
		try:
			# getopt方法返回的是一个二元组，左边是识别出的参数和值，右边是未识别参数
			opts, _ = getopt(sys.argv[1:], 'hC:c:d:o:', ['help'])
		except GetoptError:
			# 如果获取出错，自动打印错误信息并退出：
			print('Parameter Error')
			exit()
		options = dict(opts)
		if len(options) == 1 and ('-h' in options or '--help' in options):
			print('Usage: calculator.py -C city -c configfile -d userdata -o resultdata')
			exit()
		return options
	
	# 提取参数-C,-c,-d,-o后面的值，注意需要排除城市选项有默认值的情况
	def _value_after_option(self, option):
		value = self.options.get(option)
		if value is None and option != '-C':
			print('Parameter Error')
			exit()
		return value
	
	# 获取 -C 参数对应的值，即所在城市
	@property
	def city(self):
		return self._value_after_option('-C')

	# 获取 -c 参数对应的值，即配置文件的路径
	@property
	def config_path(self):
		return self._value_after_option('-c')
	
	# 获取 -d 参数对应的值，即用户数据文件的路径
	@property
	def userdata_path(self):
		return self._value_after_option('-d')

	# 获取 -o 参数对应的值，即输出的用户工资单文件的路径
	@property
	def export_path(self):
		return self._value_after_option('-o')

# 创建命令行参数处理的对象 args
# 在此处创建对象的原因是，后续配置信息处理类 config 需要用到此对象
args = Args()

# 配置信息处理类
class Config(object):

	# 初始化时调用内部接口self._read_config()读取配置文件的所有内容
	# 读取的所有配置项和值都存入字典 self.config中
	def __init__(self):
		self.config = self._read_config()

	# 内部函数，用来读取配置文件中的配置项
	def _read_config(self):
		# 使用configparser模块读取配置文件
		config = configparser.ConfigParser()
		#读取配置文件中的城市选项，存在选项则返回相应配置，否则返回默认配置
		config.read(args.config_path)
		if args.city and args.city.upper() in config.sections():
			return config[args.city.upper()]
		else:
			return config['DEFAULT']


	# 内部函数，用来使用配置项获得配置的值
	def _get_config(self, name):
		try:
			return float(self.config[name]) 
		except (ValueError, KeyError):
			# 如果配置项不存在，则报错退出：
			print('Config Error')
			exit()

	# 获取社保基数下限
	@property
	def social_insurance_baseline_low(self):
		return self._get_config('JiShuL')
			
	# 获取社保基数上限
	@property
	def social_insurance_baseline_high(self):
		return self._get_config('JiShuH')

	# 获取社保总费率，分别获取单项费率之后再使用sum计算总和
	@property
	def social_insurance_total(self):
		return sum([
			self._get_config('YangLao'),
			self._get_config('YiLiao'),
			self._get_config('ShiYe'),
			self._get_config('GongShang'),
			self._get_config('ShengYu'),
			self._get_config('GongJiJin')
		])	

# 创建文件处理的对象 config
# 在此创建的原因是后续的计算器类将使用到此对象
config = Config()

# 用户工资文件处理类
class UserData(Process):
		
	# 内部函数，用于读取用户工资文件
	def _read_user_data(self):
		# 打开用户工资文件
		with open(args.userdata_path) as file:
			for line in file.readlines():
				# 使用逗号分割每一行的字符串，得到工号和工资
				employee_id, income_string = line.strip().split(',')
				try:
					# 将工资字符串转为整数
					income = int(income_string)
				except ValueError:
					# 如果工资无法转为整数，报错退出:
					print('Parameter Error')
					exit()
				# 将每一行的数据转为二元组，存入生成器中：
				yield(employee_id, income)
	
	# 进程发送数据
	def run(self):
		for data in self._read_user_data():
			q_userdata.put(data)

# 税后工资计算类
class TaxCalculate(Process):

	# 静态成员方法，计算用于计算五险一金的工资金额
	@staticmethod
	def InsurIncomeCalc(income):
		# 如果金额低于社保基数下限，则按下限计算社保：
		if income < config.social_insurance_baseline_low:
			return config.social_insurance_baseline_low * config.social_insurance_total
		# 如果金额高于社保基数上限，则按上限计算社保：
		if income > config.social_insurance_baseline_high:
			return config.social_insurance_baseline_high * config.social_insurance_total
		# 其他情况按传入工资金额计算：
		return income * config.social_insurance_total
	
	# 类方法，不需要将类实例化，即可使用，需要传入代表类的cls，计算个税和税后工资，传入参数为工资金额
	@classmethod
	def TaxIncomeCalc(cls, income):
		# 计算五险一金:
		insurance = cls.InsurIncomeCalc(income)
		# 计算纳税工资
		TaxableIncome = income - insurance - TaxStartPoint
		# 如果纳税工资低于个税起征点，则不交个人所得税,税后工资即为交完五险一金所剩工资
		if TaxableIncome <= 0:
			return '0.00','{:2f}'.format(income - insurance)
		# 其他情况使用个税计算表计算个税
		for item in IncomeTaxLookupTable:
			# 循环遍历，直至找到纳税额所在区间
			if TaxableIncome > item.StartPoint:
				tax = TaxableIncome * item.TaxRate - item.QuickDeduction
				# 返回个税及工资，按要求格式输出
				return '{:.2f}'.format(tax), '{:.2f}'.format(income - insurance - tax) 
	
	# 计算所有用户工资，直接使用 self.userdata 对象
	def CalForAllUser(self):
		while True:
			try:
				employee_id, income = q_userdata.get(timeout = 1)
			except queue.Empty:
				return
			# 初始化返回的数据结果，包含工号和税前工资
			data = [employee_id, income]
			# 计算五险一金，按要求格式输出:
			insurance = '{:.2f}'.format(self.InsurIncomeCalc(income))
			# 计算个税和税后工资:
			tax, remain = self.TaxIncomeCalc(income)
			# 将计算数据补充到返回列表中:
			data += [insurance, tax, remain]

			# 写入工资单生成时间
			data.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			
			yield data

	def run(self):
		for data in self.CalForAllUser():
			q_result.put(data)
	
# 导出数据文件为csv格式
class Exporter(Process):

	def run(self):
		with open(args.export_path, 'w', newline='') as file:
			while True:
				writer = csv.writer(file)
				try:
					item = q_result.get(timeout =1)
				except queue.Empty:
					return
				writer.writerow(item)
	
if __name__ == '__main__':
	workers = [
		UserData(),
		TaxCalculate(),
		Exporter()
	]
	for worker in workers:
		worker.run()