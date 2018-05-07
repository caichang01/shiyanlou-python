import sys
import pymongo
from pymongo import MongoClient

def get_rank(user_id):
    client = MongoClient()
    db = client.shiyanlou

    # 查询contests中所有的user_id字段
    userIdList = []
    uids = db.contests.find().sort([('user_id', pymongo.ASCENDING)])
    for uid in uids:
        userIdList.append(uid['user_id'])
    userIdList = list(set(userIdList))

    # 计算用户 user_id 的排名、总分以及花费的总时间
    for userId in userIdList:
        items = db.contests.find({'user_id' :  userId})
        scoreTotal = 0
        submit_timeTotal = 0
        for item in items:
            scoreTotal += item['score']
            submit_timeTotal += item['submit_time']
        user = {'uid': userId, 'score': scoreTotal, 'submit_time': submit_timeTotal}
        # 创建新的collection，写入用户id，总成绩和总时间
        db.data.insert_one(user)

    # 从新collection中按成绩和时间进行多列查询
    datas = db.data.find().sort([('score', pymongo.DESCENDING), ('submit_time', pymongo.ASCENDING)])
    rank = 1
    tempList = []
    dataDict = dict()
    for data in datas:
        tempList = [rank, data['score'], data['submit_time']]
        dataDict[data['uid']] = tempList
        rank += 1
    db.drop_collection('data')

    return dataDict[user_id]

if __name__ == '__main__':
    # 判断参数格式
    if len(sys.argv) != 2:
        print("Parameter error.")
        sys.exit(1)

    # 获取用户 ID
    user_id = sys.argv[1]

    # 根据用户 ID 获取用户排名，分数和时间
    userdata = get_rank(int(user_id))
    print(userdata)