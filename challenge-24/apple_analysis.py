import pandas as pd


def quarter_volume():
    data = pd.read_csv('apple.csv', header=0)

    data = data.volume
    data.index = pd.to_datetime(data.Date)

    data_resample = data.resample('Q').sum()
    second_volume = data_resample[1]

    return second_volume


if __name__ == '__main__':
    quarter_volume()
