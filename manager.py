
import math
import json
import time
import threading

from data_type import Big, Small, DataBox
import file_util as fu
import config as c
import box_helper as helper

dataBox = None   # 存储读入的数据
packingResults = [] # 存储结果
maxBins = []        # 存储最后的箱子结果

running = True  # 
debug = True    # 


def addBreakPoint():
    print('into break point')
    if not debug:
        return
    global running
    running = False
    while not running:
        # print('thread running')
        time.sleep(1)


# 读取保存的矩形数据
def readData():
    global dataBox
    dataBox = DataBox()
    data_file_content = fu.readFile(c.dataFile)
    box_data = json.loads(data_file_content)
    dataBox.bin = Big(box_data['big']['width'], box_data['big']['height'])
    for box_group in box_data['small_boxes']:
        new_group = []
        for box in box_group:
            small = Small(box['width'], box['height'], dataBox.bin)
            new_group.append(small)
            small.num = len(new_group)
        dataBox.datas.append(new_group)
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


# 对一组盒子的装箱进行处理
def packingGroup(big, group):
    # 按照宽度排序后全部放入箱子中
    bins = fillFirst(big, group)
    global maxBins
    maxBins = [] # 值最大化后的箱子列表  
    # 选择价值最大的箱子装满
    fillResult = fillMaxValueBin(bins)
    maxBins.append(fillResult['max'])
    fillResult['max'].setNum(len(maxBins) - 1)
    while len(fillResult['unused']) > 0:
        addBreakPoint()
        bins = fillFirst(big, fillResult['unused'])
        fillResult = fillMaxValueBin(bins)
        maxBins.append(fillResult['max'])
        fillResult['max'].setNum(len(maxBins) - 1)
        # print('fillMaxOver len:', len(maxBins), '------------------')
        # printBoxCount(maxBins, fillResult['unused'])
    print('finally packingGroup over.')


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

    # 挑选出价值最大的箱子
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

    # 没装到第一个箱子中的物品重新组到一个列表中
    unused = []
    for box in boxes:
        for child in box.children:
            if len(child.children) > 0:
                # 组合过的箱子再拆开
                unused.extend(child.children)
            else:
                unused.append(child)
    unused = sortGroupByWidth(unused) # 根据宽度排一下序
    # unused = sortGroupByHeight(unused) # 根据高度排一下序
    # unused = sortGroupByValue(unused) # 根据价值排一下序
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
# 宽度相同的物品组合到一起，堆起来

def sortGroup(group):
    newGroup = sortGroupByWidth(group)
    packedGroup = packSameWidth(newGroup)
    newGroup = sortGroupByWidth(packedGroup)
    return newGroup

def sortGroupByWidth(group):
    newGroup = []

    # 按照宽度排序
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

def packSameWidth(newGroup):
    # 宽度相同的堆起来，高度不能超过大箱子高度
    big = dataBox.bin
    multiGroup = []
    currBox = None
    processedIndex = 0 # 处理过的最大索引
    for i in range(len(newGroup)):
        if i < processedIndex:  # 处理过的跳过
            continue
        if i == len(newGroup) - 1: # 最后一个直接结束
            multiGroup.append(newGroup[i])
            continue
        if currBox == None:
            currBox = newGroup[i]
        nextBox = newGroup[i+1]
        if currBox.width == nextBox.width and currBox.height + nextBox.height < big.height:
            if len(currBox.children) == 0:
                currBox = Small(newGroup[i].width, newGroup[i].height, big=big)
                currBox.addSub(newGroup[i])
                currBox.addSub(newGroup[i+1])
            else:
                currBox.addSub(newGroup[i+1])
            
            processedIndex = i + 1
        else:
            multiGroup.append(currBox)
            currBox = None

    return multiGroup

def sortGroupByValue(group):
    newGroup = []

    # 按照宽度排序
    for i in range(len(group)):
        small = group[i]
        if len(newGroup) == 0:
            newGroup.append(small)
        else:
            inserted = False
            for j in range(len(newGroup)):
                if small.value > newGroup[j].value:
                    newGroup.insert(j, small)
                    inserted = True
                    break
            if not inserted:
                newGroup.append(small)
    # print('group:',len(group), " new:", len(newGroup))
    return newGroup

def sortGroupByHeight(group):
    newGroup = []

    # 按照宽度排序
    for i in range(len(group)):
        small = group[i]
        if len(newGroup) == 0:
            newGroup.append(small)
        else:
            inserted = False
            for j in range(len(newGroup)):
                if small.height > newGroup[j].height:
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