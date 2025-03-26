import tkinter as tk
from tkinter import messagebox

def on_closing():
    messagebox.showwarning("警告", "请勿关闭此窗口！程序正在运行中！")

def force_exit(event):
    root.destroy()

root = tk.Tk()
root.title("重要提示")
root.attributes("-fullscreen", True)  # 全屏显示
root.attributes("-topmost", True)     # 始终置顶
root.configure(bg='red')              # 红色背景更醒目
root.bind("<F12>", force_exit)

# 创建文字标签
label = tk.Label(
    root,
    text="别关电脑，\n程序运行中！",  # 使用换行符加大显示
    font=('Arial Black', 100, 'bold'),
    fg='white',
    bg='red',
    justify='center'
)
label.pack(expand=True, fill='both')

# 禁用Alt+F4和窗口关闭按钮
root.protocol("WM_DELETE_WINDOW", on_closing)
root.bind("<Alt-F4>", lambda event: on_closing())

root.mainloop()