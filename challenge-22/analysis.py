import json
import pandas as pd
import sys


# 纯python实现
def analysis_by_python_only(file, user_id):

    times = 0
    minutes = 0

    try:
        with open(file, 'r') as f:
            records = json.loads(f.read())
        for item in records:
            if item['user_id'] == user_id:
                times += 1
                minutes += 1
    except ValueError:
        pass
    return times, minutes


def analysis(file, user_id):

    times = 0
    minutes = 0

    try:
        df = pd.read_json(file)
        df = df[df['user_id'] == int(user_id)].minutes
    except ValueError:
        return 0, 0

    times = df.count()
    minutes = df.sum()
    return times, minutes


if __name__ == '__main__':

    file = sys.argv[1]
    user_id = sys.argv[2]

    analysis(file, user_id)
