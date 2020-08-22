import random as r
import json

import file_util as fu
import config as c

index = -1
def newIndex():
    global index
    index += 1
    return index


# 生成大小矩形数据
def createData():
    result = {}
    bigw = r.randint(300,480)
    bigh = r.randint(160, 300)
    if bigw < bigh:
        temp = bigw
        bigw = bigh
        bigh = temp
    result['big'] = {'width':bigw, 'height':bigh}

    small_boxes = []
    # 创建10组数据
    small_boxes.append(createSmallData(newIndex(), 30,int(bigw/3),30,int(bigh/3)))
    small_boxes.append(createSmallData(newIndex(), 30,int(bigw/3),30,int(bigh/2)))
    small_boxes.append(createSmallData(newIndex(), 30,int(bigw/2),30,int(bigh/3)))
    small_boxes.append(createSmallData(newIndex(), 30,int(bigw/2),30,int(bigh/2)))
    small_boxes.append(createSmallData(newIndex(), 30,bigw,30,int(bigh/3)))
    small_boxes.append(createSmallData(newIndex(), 30,int(bigw/3),30,bigh))
    small_boxes.append(createSmallData(newIndex(), 90,bigw,80,bigh))
    small_boxes.append(createSmallData(newIndex(), 50,bigw,80,int(bigh/2)))
    small_boxes.append(createSmallData(newIndex(), 50,int(bigw/2),80,bigh))
    small_boxes.append(createSmallData(newIndex(), 90,bigw,30,int(bigh/3)))
    result['small_boxes'] = small_boxes
    return result

# 生成一组小矩形数据
def createSmallData(index, width1,width2,height1,height2):
    timesNum = 3
    w1 = int(width1/timesNum)
    w2 = int(width2/timesNum)
    h1 = int(height1/timesNum)
    h2 = int(height2/timesNum)

    if w2<=w1 or h2 <=h1 :
        print('错误数据 w1', w1, 'w2', w2, 'h1', h1, 'h2', h2)
        print('请重新生成！！')
        raise
    result = []
    for i in range(0, 50):
        smallw = r.randint(w1,w2) * timesNum
        smallh = r.randint(h1,h2) * timesNum
        if smallw < smallh:
            temp = smallw
            smallw = smallh
            smallh = smallw
        # result += '\ns' + str(index) + ' ' + str(smallw) + ' ' + str(smallh)
        result.append({'width':smallw, 'height':smallh})

    return result

box_data = createData()
fu.writeFile(c.dataFile, json.dumps(box_data, indent=2))
# print(content)

