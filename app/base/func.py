# list to csv
def listToCSV(obj):
    csv = ''
    for x in obj:
        csv += str(x)
        csv += ','
    return csv[:-1]


# csv to list
def CSVToList(csv):
    obj = csv.split(',')
    li = []
    for x in obj:
        li.append(int(x))
    return li


# 更新数据库
def update_db(obj, d):
    if not isinstance(d, dict):
        raise TypeError
    for i in d:
        setattr(obj, i, d[i])
