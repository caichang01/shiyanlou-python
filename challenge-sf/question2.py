# -*- coding: utf8 -*-
import sys
import os
import re
import operator

#请完成下面这个函数，实现题目要求的功能
#当然，你也可以不按照下面这个模板来作答，完全按照自己的想法来 ^-^ 
#******************************开始写代码******************************


def  topk(nums):
    answer_dict = dict()
    answer_list = [0,0]
    for i in range(0, len(nums)):
        try:
            answer_dict[nums[i]] += 1
        except KeyError:
            answer_dict[nums[i]] = 1
    sorted_answer = sorted(answer_dict.items(), key=operator.itemgetter(1))
    sorted_answer_dict = dict(sorted_answer)
    return sorted_answer[-2][0] + sorted_answer[-1][0]

#******************************结束写代码******************************


_nums_cnt = 0
_nums_cnt = int(input())
_nums_i=0
_nums = []
while _nums_i < _nums_cnt:
    _nums_item = int(input())
    _nums.append(_nums_item)
    _nums_i+=1

  
res = topk(_nums)

print(str(res) + "\n")