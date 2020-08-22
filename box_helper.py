


# 按高度排序
def sortByHeight(boxes):
    count = len(boxes)
    # printHeight(boxes, 'before')
    for i in range(count):
        maxIndex = i
        for j in range(i + 1, count):
            if boxes[maxIndex].height < boxes[j].height:
                maxIndex = j
        # print("max is ", maxIndex, 'i is ', i)
        if i != maxIndex:
            temp = boxes[i]
            boxes[i] = boxes[maxIndex]
            boxes[maxIndex] = temp
        
        # printHeight(boxes, 'inner')

    # printHeight(boxes)
    return boxes
# 打印物品高度
def printHeight(boxes, msg=''):
    print(msg, 'box height ---------')
    for b in boxes:
        print(b.height, end=' ')
    print()

