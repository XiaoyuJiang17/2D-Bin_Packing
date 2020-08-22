
import random
import math


import box_helper as helper


# 各个数据包装类型

# 大矩形
class Big():
    pos = (0,0)  # 位置
    width = 0   # 宽度
    height = 0  # 高度
    children = [] # 包含的小矩形
    bottomWidth = 0  #底层剩余宽度
    num = 0  # 队列编号
    w = 0 # 数值乘10，方便显示
    h = 0 # 数值乘10， 方便显示
    value = 0  # 总价值

    levelWidth = 0 # 加塞时剩余宽度
    currLevel = 0  # 加塞层数

    freeSpace = [] # 跳过未使用的空间



    def __init__(self, w=0, h=0):
        self.children = []
        self.width = w
        self.height = h
        self.bottomWidth = w
        self.num = 0
        self.w = w 
        self.h = h 

        self.levelWidth = 0
        self.currLevel = 0
        self.currTailPos = None

        self.freeSpace = []

    def __str__(self):
        return 'c:%d p:%d %d w:%d h:%d' % (len(self.children), self.pos[0], self.pos[1], self.width, self.height)

    # 底层加入一个物品
    def bottomPack(self, small):
        small.pos = (self.width - self.bottomWidth, 0)
        small.spacePos = (small.pos[0], small.height)
        # print('small pos:', small.pos)
        self.bottomWidth -= small.width

        self.children.append(small)
        small.parent = self
        self.value += small.value

    # 清空箱子
    def clear(self):
        self.children = []
        self.bottomWidth = self.width

        self.value = 0

    # 设置序号，并计算在画布的位置
    def setNum(self, num):
        self.num = num
        x = 30
        y = (self.h + 20)*(num + 1)
        self.pos = (x, y)
    
    # 判断底层还能不能放入
    def bottomCanPack(self, small):
        return self.bottomWidth >= small.width

    # 替换一个物品
    def replace(self, index, newSub):
        subs = self.children
        oldSub = subs[index]
        del subs[index]
        oldSubs = subs
        self.clear()
        for sub in oldSubs:
            self.bottomPack(sub)
        self.bottomPack(newSub)
        return oldSub

    # children 按高度排序
    def sortByHeight(self):
        helper.sortByHeight(self.children)

        children = self.children
        self.clear()
        for subBox in children:
            self.bottomPack(subBox)
    # 在画布上画出自己
    def draw(self, canvas):
        width = self.w
        height = self.h
        x = self.pos[0]
        y = self.pos[1]
        # print(x, y, x+ width, y-height)
        bw = 3  # 边框粗细的一半
        # 画矩形
        canvas.create_rectangle(x-bw, y+bw, x+width+bw, y-height-bw, fill='#121212', outline='blue', stipple='gray12', width=5)
        canvas.create_text(x - 20, y - 10, text=str(self.num))

        for child in self.children:
            child.draw(canvas)
    
    # 从上部剩余空间加塞
    def spacePack(self, small):
        p = self.getSpacePos(small)
        small.pos = p
        small.spacePos = (small.pos[0], small.pos[1] + small.height)
        self.levelWidth = self.width - p[0] - small.width
        self.currTailPos = (small.pos[0] + small.width, small.pos[1])

        small.level = self.currLevel

        self.children.append(small)
        small.parent = self
        self.value += small.value
    # 判断剩余空间能否加塞
    def spaceCanPack(self, small):
        p = self.getSpacePos(small)
        # print("get ", p)
        return p
    # 取新物品能放的位置
    def getSpacePos(self, small):
        result = None
        # print('curLevel', self.currLevel)

        skipPos = []

        # 从下一层的顶部取可放入的位置
        for child in self.children:
            if child.level != self.currLevel - 1:
                continue
            p = child.spacePos
            if self.width - p[0] <= self.levelWidth:
                if self.width - p[0] >= small.width and self.height - p[1] >= small.height:
                    result = p
                    break
                else:
                    skipPos.append(p)


        # 检查上个物品的结束点
        useTailPos = False   # 记录是不是贴着上一个物体
        if self.currTailPos:
            p = self.currTailPos
            if self.width - p[0] >= small.width and self.height - p[1] >= small.height:
                if result is None:
                    result = p
                else:
                    # 比较一下，取面积大的起始点
                    resultArea = (self.width-result[0]) * (self.height - result[1])
                    tailArea = (self.width - p[0]) * (self.height - p[1])
                    if tailArea > resultArea:
                        result = p
                        useTailPos = True

        # 记录未使用的空间
        if result and not useTailPos:
            if self.currTailPos:
                skipPos.insert(0, self.currTailPos)
            skipPos.append(result)

            # 有空间的记录下来
            if len(skipPos) > 1:
                self.freeSpace.append(skipPos)
        return result

    # 设置加塞高一级
    def spaceLevelUp(self):
        self.currLevel += 1
        self.levelWidth = self.width
        self.currTailPos = None

    # 剩余空间加塞
    def freeSpacePack(self, small):
        p = self.getFreeSpacePos(small)
        small.pos = p
        small.spacePos = (small.pos[0], small.pos[1] + small.height)

        self.children.append(small)
        small.parent = self
        self.value += small.value


    # 判断剩余空间是否可加塞
    def freeSpaceCanPack(self, small):
        pos = self.getFreeSpacePos(small)
        return pos
    
    # 获取剩余空间的加塞位置
    def getFreeSpacePos(self, small):
        result = None
        for sIndex in range(len(self.freeSpace)):
            space = self.freeSpace[sIndex]
            getPos = False
            for pIndex in range(len(space) - 1):
                point = space[pIndex]
                end = space[-1]
                width = end[0] - point[0]
                height = self.height - point[1]
                if width >= small.width and height >= small.height:
                    result = point
                    getPos = True
                    del self.freeSpace[sIndex]
                    break
            if getPos:
                break

        return result



# 小矩形
class Small(Big):
    big = None # 箱子
    parent = None # 小矩形所在的大矩形
    spacePos = (0,0) # 物品顶部位置
    level = 0 # 所在层

    def __init__(self, w=0, h=0, big=None):
        super().__init__(w, h)
        self.big = big
        value = self.calculateValue()

    # 计算物品价值
    def calculateValue(self):
        w = self.width
        h = self.height
        rou = self.calculateRou()
        value = rou * math.pow(w * h, 1.2) * h / w
        self.value = value

    # 计算物品的 ρ 值
    def calculateRou(self):
        w = self.width
        h = self.height
        bw = self.big.width * 0.5
        bh = self.big.height * 0.5
        if (w > bw) and (h > bw):
            return 2
        elif (h > bh and w <= bw) or (w>bh and h<=bw) or (h>bw and w<=bh) or (w>bw and h < bh):
            return 1.5
        else:
            return 1

    def __str__(self):
        return 'i:%d p:%d %d w:%d h:%d' % (self.num, self.pos[0], self.pos[1], self.width, self.height)

    def draw(self, canvas):
        # print('pos', self.pos)
        pPos = self.parent.pos
        x = pPos[0] + self.pos[0] 
        y = pPos[1] - self.pos[1] 

        color = '#' + ''.join(random.sample('0123456789', 6))
        canvas.create_rectangle(x, y, x+self.w, y-self.h, fill=color)
        canvas.create_text(x + 10, y - 10, text=str(self.num))

class DataBox():
    bin = None   # 大矩形
    datas = []   # 数据组