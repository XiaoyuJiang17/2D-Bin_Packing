from tkinter import *
from tkinter import ttk
import tkinter
# from PIL import Image, ImageTk
# import PIL

from base_win import BaseWin
from gui_util import *
import config as c
import file_util as fu
import manager 

class AppWin(BaseWin):
    def __init__(self):
        super().__init__(c.winTitle, c.winWidth, c.winHeight)

        manager.readData()
        self.initFrame()
        self.initCanvas()

        fun = self.processGroup(3)
        fun()
    
    # 初始化控制部分的界面
    def initFrame(self):
        self.top= ttk.Frame(self.main, padding="3 3 12 12")
        self.top.grid(column=0, row=0, sticky=(N, W, E, S))
        self.main.columnconfigure(0, weight=1)
        self.main.rowconfigure(0, weight=1)	

        self.top2 = ttk.Frame(self.main, padding = '3 3 3 3')
        self.top2.grid(column=0, row=1, sticky=(N, W, E, S))
        self.main.rowconfigure(1, weight=1)	

        p = self.top
        i = 0
        for data in manager.dataBox.datas:
            i += 1
            btn = Button(p, text='第' + str(i) + '组', command=self.processGroup(i-1))
            self.grid(p, btn)
        
        self.top3 = ttk.Frame(self.main, padding = '3 3 3 3')
        self.top3.grid(column=0, row=2, sticky=(N, W, E, S))
        self.main.rowconfigure(2, weight=1)	
        big = manager.dataBox.bin
        boxInfo = '箱子大小 宽:' + str(big.width) + ' 高:' + str(big.height)
        infoL = Label(self.top3, text=boxInfo)
        self.grid(self.top3, infoL)
        dataL01 = Label(self.top3, text='当前数据第')
        self.grid(self.top3, dataL01)
        self.dataNumL = Label(self.top3, text='0')
        self.grid(self.top3, self.dataNumL)
        dataL02 = Label(self.top3, text='组  共使用箱子')
        self.grid(self.top3, dataL02)
        self.boxNumL= Label(self.top3, text='0')
        self.grid(self.top3, self.boxNumL)
        dataL04 = Label(self.top3, text='个')
        self.grid(self.top3, dataL04)


    # 显示并处理指定组的数据
    def processGroup(self, index):
        def innerFun():
            p = self.top2
            for widget in p.winfo_children():
                widget.destroy()
            boxes = manager.dataBox.datas[index]
            self.dataNumL['text'] = str(index + 1)
            i = 0
            # 显示一组数据内容
            for box in boxes:
                newRow = i % 10 == 0
                text = str(i) + ':(' + str(box.width) + ',' + str(box.height) + ')'
                label = Label(p, text=text)
                self.grid(p, label, nextRow=newRow)
                i += 1

            result = manager.packingGroup(manager.dataBox.bin, boxes)
            self.boxNumL['text'] = str(len(result))
            self.drawBins(result)
        return innerFun

        

    # 初始化画布控件
    def initCanvas(self):
        # manager.start()

        frame = Frame(self.main)
        frame.grid(column=0, row = 3, sticky = (N, W, E, S))
        self.main.rowconfigure(3, weight=2)
        cv = Canvas(frame)
        self.canvas = cv



        # cv.config(width=100, height=200) # display area size
        cv.config(scrollregion=(0, 0, 100, 1000)) # canvas size corners
        # cv.config(highlightthickness=0) # no pixels to border
        # cv.create_rectangle(10, 10, 110, 810)


        sbar = Scrollbar(frame)
        sbar.config(command=cv.yview)                   # xlink sbar and canv
        cv.config(yscrollcommand=sbar.set)              # move one moves other
        sbar.pack(side=RIGHT, fill=Y)                     # pack first=clip last
        cv.pack(side=LEFT, expand=YES, fill=BOTH)       # canv clipped first

        # self.drawBins(manager.packingResults[0])

    # 画出矩形状态
    def drawBins(self, boxes):
        singleHeight = manager.dataBox.bin.height + 2*10
        totalHeight = len(boxes) * singleHeight
        # print('single:',singleHeight, 'size:', len(boxes), 'total:', totalHeight)
        self.canvas.config(scrollregion=(0, 0, 100, totalHeight + 50))
        self.canvas.delete('all')


        cv = self.canvas

        for box in boxes:
            box.draw(self.canvas)


        


if __name__ == "__main__":
    app = AppWin()
    app.start()


    