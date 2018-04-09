#！ -*- coding: utf-8 -*-
import sys
import csv
from collections import namedtuple

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
	TaxLookupItem(1500, 0.3, 0),
]

# 处理命令行参数类
class Args(object):

	# 初始化时读取命令行所有参数到self.args列表中
	def __init__(self):
		self.args = sys.argv[1:]

	# 提取参数-c,-d,-o后面的值
	def _value_after_option(self, option):
		try:
			# 首先获得参数的索引值：
			index = self.args.index(option)
			# 参数所在位置下一个的字符串就是所需的文件路径
			return self.args[index + 1]
		except (ValueError, IndexError):
			# 如果获取出错，自动打印错误信息并退出：
			print('Parameter Error')
			exit()
	
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
		# 从args对象中获得配置文件路径
		config_path = args.config_path
		# 初始化存储配置项和值的字典
		config = {}
		# 打开配置文件读取数据
		with open(config_path) as file:
			# 读取每一行的数据
			for line in file.readlines():
				# 使用 = 分割每一行的内容，需要注意的是要去除每行两边的空格，还要注意，等号两边的空格也需要划分
				key, value = line.strip().split(' = ')
				try:
					# 将配置项和值存入对应的字典中，注意要去除字符串两边的空格
					config[key.strip()] = float(value.strip())
				except ValueError:
					# 如果配置值不能转成浮点型，则报错退出：
					print('Parameter Error')
					exit()
		# 返回存储配置项和值的字典
		return config

	# 内部函数，用来使用配置项获得配置的值
	def _get_config(self, key):
		try:
			return self.config[key] 
		except KeyError:
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
class UserData(object):

	# 初始化过程中，读取用户工资文件并将工资数据存入userdata列表中
	def __init__(self):
		self.userdata = self._read_user_data()
		
	# 内部函数，用于读取用户工资文件
	def _read_user_data(self):
		# 从args中获取用户工资文件路径
		userdata_path = args.userdata_path
		# 初始化存储列表
		userdata = []
		# 打开用户工资文件
		with open(userdata_path) as file:
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
				# 将每一行的数据转为二元组后存入列表中：
				userdata.append((employee_id, income))
		# 返回用户工资数据列表
		return userdata
		
	# 添加__iter__将UserData对象变为可迭代对象
	# 即可以用 for 循环获取中间userdata列表的所有数据
	def __iter__(self):
		return iter(self.userdata)

# 税后工资计算类
class TaxCalculate(object):

	# 初始化时传入userdata对象，传入赋值给self.userdata
	def __init__(self, userdata):
		self.userdata = userdata

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
		# 初始化返回结果
		result = []
		# 循环获取 userdata 中所有的用户工号和税前工资
		for employee_id, income in self.userdata:
			# 初始化返回的数据结果，包含工号和税前工资
			data = [employee_id, income]
			# 计算五险一金，按要求格式输出:
			insurance = '{:.2f}'.format(self.InsurIncomeCalc(income))
			# 计算个税和税后工资:
			tax, remain = self.TaxIncomeCalc(income)
			# 将计算数据补充到返回列表中:
			data += [insurance, tax, remain]
			result.append(data)
		# 返回所有用户数据
		return result

	# 导出数据文件为csv格式
	def export(self, file_type = 'csv'):
		# 计算获取所有用户数据
		result = self.CalForAllUser()
		# 打开导入的文件，写入
		with open(args.export_path, 'w', newline='') as file:
			# 使用csv模块创建writer对象
			writer = csv.writer(file)
			# 写入
			writer.writerows(result)
	
if __name__ == '__main__':
	# 创建userdata对象并使用该对象初始化计算器
	calculator = TaxCalculate(UserData())
	# 调用输出方法
	calculator.export()