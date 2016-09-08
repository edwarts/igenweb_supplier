from flask import session


# 是否已登录
def isSession():
    if 'username' in session:
        return True
    return False


# 返回字典
def toDict(index, lists):
    result = []
    for list in lists:
        row = {}
        for i in range(len(index)):
            if list[i] == 'None' or list[i] is None:
                row[index[i]] = " "
            else:
                row[index[i]] = str(list[i])
        result.append(row)
    return result


def theme(l):
    a, b, c = "", "", ""
    if len(l) == 1:
        a = l
    elif len(l) == 2:
        a, b = l
    elif len(l) == 3:
        a, b, c = l
    else:
        pass
    return a, b, c
