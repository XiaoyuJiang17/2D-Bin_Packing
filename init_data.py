import random as r

import file_util as fu
import config as c

index = -1
def newIndex():
    global index
    index += 1
    return index


# 生成大小矩形数据
def createData():
    result = '' 
    bigw = r.randint(300,480)
    bigh = r.randint(160, 300)
    if bigw < bigh:
        temp = bigw
        bigw = bigh
        bigh = temp
    result += 'big ' + str(bigw) + " " + str(bigh)

    # 创建10组数据
    result += createSmallData(newIndex(), 30,int(bigw/3),30,int(bigh/3))
    result += createSmallData(newIndex(), 30,int(bigw/3),30,int(bigh/2))
    result += createSmallData(newIndex(), 30,int(bigw/2),30,int(bigh/3))
    result += createSmallData(newIndex(), 30,int(bigw/2),30,int(bigh/2))
    result += createSmallData(newIndex(), 30,bigw,30,int(bigh/3))
    result += createSmallData(newIndex(), 30,int(bigw/3),30,bigh)
    result += createSmallData(newIndex(), 90,bigw,80,bigh)
    result += createSmallData(newIndex(), 50,bigw,80,int(bigh/2))
    result += createSmallData(newIndex(), 50,int(bigw/2),80,bigh)
    result += createSmallData(newIndex(), 90,bigw,30,int(bigh/3))
    return result

# 生成一组小矩形数据
def createSmallData(index, w1,w2,h1,h2):
    if w2<=w1 or h2 <=h1 :
        print('错误数据 w1', w1, 'w2', w2, 'h1', h1, 'h2', h2)
        print('请重新生成！！')
        raise
    result = ''
    for i in range(0, 50):
        smallw = r.randint(w1,w2)
        smallh = r.randint(h1,h2)
        if smallw < smallh:
            temp = smallw
            smallw = smallh
            smallh = smallw
        result += '\ns' + str(index) + ' ' + str(smallw) + ' ' + str(smallh)

    return result

content = createData()
fu.writeFile(c.dataFile, content)
# print(content)

