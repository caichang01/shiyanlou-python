import pandas as pd


def quarter_volume():
    data = pd.read_csv('apple.csv', header=0)

    data_serialized = data.Volume
    data_serialized.index = pd.to_datetime(data.Date)

    data_resample = data_serialized.resample('Q').sum().sort_values()
    second_volume = data_resample[-2]

    # print(second_volume)
    return second_volume


if __name__ == '__main__':
    quarter_volume()
