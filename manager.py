
import math

from data_type import Big, Small, DataBox
import file_util as fu
import config as c
import box_helper as helper

dataBox = None   # 存储读入的数据
packingResults = [] # 存储结果


# 读取保存的矩形数据
def readData():
    global dataBox
    dataBox = DataBox()
    lines = fu.readLines(c.dataFile)
    smallIndex = 0
    for line in lines:
        if line.startswith('big'):
            parts = line.split(' ')
            big = Big()
            big.width = int(parts[1])
            big.height = int(parts[2])
            dataBox.bin = big
        elif line.startswith('s'):
            parts = line.split(' ')
            small = Small(int(parts[1]), int(parts[2]), big)
            index = int(parts[0][1:])
            if len(dataBox.datas) > index:
                dataBox.datas[index].append(small)
                smallIndex += 1
            else:
                dataBox.datas.append([small])
                smallIndex = 0
            small.num = smallIndex
    return dataBox


# 总的装箱处理程序入口
def start():
    global packingResults
    packingResults = []
    dataBox = readData()
    big = dataBox.bin

    i = 0
    for group in dataBox.datas:
        if i < 3:
            i += 1
            continue
        result = packingGroup(big, group)
        packingResults.append(result)
        break


# 对一组的装箱进行处理
def packingGroup(big, group):
    # 按照宽度排序后全部放入箱子中
    bins = fillFirst(big, group)
   
    maxBins = [] # 值最大化后的箱子列表  
    # 选择价值最大的箱子装满
    fillResult = fillMaxValueBin(bins)
    maxBins.append(fillResult['max'])
    fillResult['max'].setNum(len(maxBins) - 1)
    while len(fillResult['unused']) > 0:
        bins = fillFirst(big, fillResult['unused'])
        fillResult = fillMaxValueBin(bins)
        maxBins.append(fillResult['max'])
        fillResult['max'].setNum(len(maxBins) - 1)
        # print('fillMaxOver len:', len(maxBins), '------------------')
        # printBoxCount(maxBins, fillResult['unused'])


    return maxBins
        
# 把物品按宽度装到箱子中，排序
def fillFirst(big, group):
    sortedGroup = sortGroup(group)
    bins = []  # 初始需要的箱子列表
    currBin = Big(big.width, big.height)

    # 把小矩形全部装入大矩形中
    for small in sortedGroup:
        if currBin.bottomCanPack(small):
            currBin.bottomPack(small)
        else:
            bins.append(currBin)
            currBin.setNum(len(bins) - 1)

            currBin = Big(big.width, big.height)
            currBin.bottomPack(small)
    bins.append(currBin)
    currBin.setNum(len(bins) - 1)

    # 按高度排序
    for box in bins:
        box.sortByHeight()
    return bins


# 选择价值最大的箱子装满
def fillMaxValueBin(boxes):
    # printBoxValue(boxes,'before')
    result = {}
    maxIndex = 0
    for i in range(len(boxes)):
        if boxes[i].value > boxes[maxIndex].value:
            maxIndex = i
    maxBox = boxes[maxIndex]
    result['max'] = maxBox
    # print('maxIndex', maxIndex)
    # print(result['max'].value)
    del boxes[maxIndex]
    # printBoxValue(boxes,'after')

    unused = []
    for box in boxes:
        unused.extend(box.children)
    result['unused'] = unused


    # 替换价值更大的物品
    # print('------------')
    for index in range(len(maxBox.children)):
        child = maxBox.children[index]
        # print("child ", child.value)
        betterBox = None
        replaceIndex = -1
        for unusedIndex in range(len(unused)):
            unusedBox = unused[unusedIndex]
            if unusedBox.value > child.value:
                if unusedBox.width <= child.width + maxBox.bottomWidth:
                    # print(unusedBox.value, child.value)
                    if betterBox is None or (unusedBox.value > betterBox.value):
                        betterBox = unusedBox
                        replaceIndex = unusedIndex
                    # pass
        if betterBox != None:
            # print(betterBox.value, child.value)
            oldSub = maxBox.replace(index, betterBox)
            del unused[replaceIndex]
            unused.append(oldSub)
            # print("o value:", oldSub.value, 'n value:', betterBox.value)
    maxBox.sortByHeight()

    helper.sortByHeight(unused)
    # 剩余空间加塞
    packIndexes = []

    # 第一层加塞
    for unusedIndex in range(len(unused)):
        # if unusedIndex >= len(unused):
            # break  # unused 长度会改变
        unusedBox = unused[unusedIndex]
        if maxBox.bottomCanPack(unusedBox):
            maxBox.bottomPack(unusedBox)
            packIndexes.append(unusedIndex)
    while len(packIndexes) > 0:
        del unused[packIndexes[-1]]
        del packIndexes[-1]
    maxBox.sortByHeight()


    # print('space  box num', maxBox.num, '---------------')
    maxBox.spaceLevelUp()
    # 上层空间加塞
    insertToSpace(maxBox, unused)
    # print('01levelSpace', maxBox.levelWidth, 'maxWidth', maxBox.width)
    while maxBox.levelWidth < maxBox.width:
        maxBox.spaceLevelUp()
        insertToSpace(maxBox, unused)
        # print('02levelSpace', maxBox.levelWidth, 'maxWidth', maxBox.width)

    # 最后的未利用空间加塞
    insertToFreeSpace(maxBox, unused)



    return result

# 对一层空间加塞
def insertToSpace(maxBox, unused):
    packIndexes = []
    for unusedIndex in range(len(unused)):
        unusedBox = unused[unusedIndex]
        if maxBox.spaceCanPack(unusedBox):
            maxBox.spacePack(unusedBox)
            packIndexes.append(unusedIndex)
    while len(packIndexes) > 0:
        del unused[packIndexes[-1]]
        del packIndexes[-1]

# 对未利用空间加赛
def insertToFreeSpace(maxBox, unused):
    packIndexes = []
    for unusedIndex in range(len(unused)):
        unusedBox = unused[unusedIndex]
        if maxBox.freeSpaceCanPack(unusedBox):
            # print('before width', maxBox.levelWidth)
            maxBox.freeSpacePack(unusedBox)
            # print('after  width', maxBox.levelWidth)
            packIndexes.append(unusedIndex)
    while len(packIndexes) > 0:
        del unused[packIndexes[-1]]
        del packIndexes[-1]



# 对一组物品按宽度排序
def sortGroup(group):
    newGroup = []
    for i in range(len(group)):
        small = group[i]
        if len(newGroup) == 0:
            newGroup.append(small)
        else:
            inserted = False
            for j in range(len(newGroup)):
                if small.width > newGroup[j].width:
                    newGroup.insert(j, small)
                    inserted = True
                    break
            if not inserted:
                newGroup.append(small)
    # print('group:',len(group), " new:", len(newGroup))
    return newGroup


           

# 打印箱子的值
def printBoxValue(boxes, msg=''):
    print(msg, 'box value ---------')
    i = 0
    for b in boxes:
        i += 1
        print(b.value, end=' ')
        if i % 5 ==0:
            print()
    print()

# 打印物品数量
def printBoxCount(maxBins, unused):
    count = 0
    for b in maxBins:
        count += len(b.children)
    unCount = len(unused)
    print('used count', count, 'unusede count', unCount)

if __name__ == '__main__':
    # start()
    print(math.pow(2,2))
    print(math.pow(2,2.2))
    print(math.pow(2,2.5))
    print(math.pow(2,3))