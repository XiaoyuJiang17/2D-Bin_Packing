import tkinter.simpledialog as dialog
from tkinter.simpledialog import askinteger, askfloat, askstring
import tkinter.messagebox as msgbox
from tkinter.messagebox import showinfo, showwarning, showerror




def showErr(msg):
    showerror("错误", msg)
# 显示提示信息
def showInfo(msg):
    showinfo("提示", msg)