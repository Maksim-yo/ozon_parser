import pandas as pd


# Загрузим данные из файла, созданного scrapy
data = pd.read_csv('phones.csv')

# Подсчитаем распределение версий операционных систем
phone_os_versions = data.groupby(['phone_os','phone_os_version'], as_index=False).size().sort_values('size', ascending=False)

# Выведем результат
for index, phone_os_version in phone_os_versions.iterrows():
    print(f"{phone_os_version['phone_os']} {phone_os_version['phone_os_version']} - {phone_os_version['size']}")
