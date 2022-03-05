from tkinter import *
import os
from ctypes import windll


def set_appwindow(mainWindow): # to display the window icon on the taskbar, 
                               # even when using root.overrideredirect(True)

    # Some WindowsOS styles, required for task bar integration
    GWL_EXSTYLE = -20
    WS_EX_APPWINDOW = 0x00040000
    WS_EX_TOOLWINDOW = 0x00000080
    # Magic
    hwnd = windll.user32.GetParent(mainWindow.winfo_id())
    stylew = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    stylew = stylew & ~WS_EX_TOOLWINDOW
    stylew = stylew | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, stylew)
   
    mainWindow.wm_withdraw()
    mainWindow.after(10, lambda: mainWindow.wm_deiconify())


def startWoodcutter():
    os.system("python ./Core/startBot.py")


def minimize_me():
    root.attributes("-alpha",0)
    root.minimized = True       

def deminimize(event):

    root.focus() 
    root.attributes("-alpha",1)
    if root.minimized == True:
        root.minimized = False                              
    
def maximize_me():

    if root.maximized == False:
        root.normal_size = root.geometry()

        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0")
        root.maximized = not root.maximized 

    else: 
        root.geometry(root.normal_size)
        root.maximized = not root.maximized

tk_title = "RS-MB" 

root=Tk() 
root.title(tk_title) 
root.overrideredirect(True) 
root.geometry("600x545+650+250")

canvas = Canvas(
    root,
    bg = "#ffffff",
    height = 561,
    width = 602,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge")
    
canvas.place(x = 0, y = 0) 
background_img = PhotoImage(file = "./images/background.png")
background = canvas.create_image(
    304.5, 308.5,
    image=background_img)


root.minimized = False # only to know if root is minimized
root.maximized = False # only to know if root is maximized


LGRAY = '#DAB700' # button color effects in the title bar
DGRAY = '#202020' # window background color               
RGRAY = '#FAD200' # title bar color                       


root.config(bg="#25292e")


img0 = PhotoImage(file = "./images/img0.png")
b0 = Button(
    image = img0,
    borderwidth = 0,
    highlightthickness = 0,
    relief = "flat")

b0.place(
    x = 36, y = 484,
    width = 86,
    height = 28)

img1 = PhotoImage(file = "./images/img1.png")
b1 = Button(
    image = img1,
    borderwidth = 0,
    highlightthickness = 0,
    relief = "flat")

b1.place(
    x = 37, y = 366,
    width = 82,
    height = 28)

img2 = PhotoImage(file = "./images/img2.png")
b2 = Button(
    image = img2,
    borderwidth = 0,
    highlightthickness = 0,
    command = startWoodcutter,
    relief = "flat")

b2.place(
    x = 32, y = 249,
    width = 95,
    height = 29)

title_bar = Frame(root, bg=RGRAY, relief='sunken', bd=0,highlightthickness=0)
close_button = Button(title_bar, text='  x  ', command=root.destroy,bg=RGRAY,padx=2,pady=2,font=("calibri", 13),bd=0,fg='black',highlightthickness=0)
minimize_button = Button(title_bar, text=' _ ',command=minimize_me,bg=RGRAY,padx=2,pady=2,bd=0,fg='black',font=("calibri", 13),highlightthickness=0)
title_bar_title = Label(title_bar, text=tk_title, bg=RGRAY,bd=0,fg='black',font=("helvetica", 10),highlightthickness=0)

title_bar.pack(fill=X)
close_button.pack(side=RIGHT,ipadx=7,ipady=1)
minimize_button.pack(side=RIGHT,ipadx=7,ipady=1)
title_bar_title.pack(side=LEFT, padx=10)

def changex_on_hovering(event):
    global close_button
    close_button['bg']='red'
def returnx_to_normalstate(event):
    global close_button
    close_button['bg']=RGRAY


def changem_size_on_hovering(event):
    global minimize_button
    minimize_button['bg']=LGRAY
def returnm_size_on_hovering(event):
    global minimize_button
    minimize_button['bg']=RGRAY


def get_pos(event): 

    if root.maximized == False:
        
        xwin = root.winfo_x()
        ywin = root.winfo_y()
        startx = event.x_root
        starty = event.y_root

        ywin = ywin - starty
        xwin = xwin - startx

        def move_window(event):
            root.config(cursor="fleur")
            root.geometry(f'+{event.x_root + xwin}+{event.y_root + ywin}')


        def release_window(event): 
            root.config(cursor="arrow")
            
        title_bar.bind('<B1-Motion>', move_window)
        title_bar.bind('<ButtonRelease-1>', release_window)
        title_bar_title.bind('<B1-Motion>', move_window)
        title_bar_title.bind('<ButtonRelease-1>', release_window)
    else:
        root.maximized = not root.maximized
        
        
title_bar.bind('<Button-1>', get_pos) 
title_bar_title.bind('<Button-1>', get_pos)  


close_button.bind('<Enter>',changex_on_hovering)
close_button.bind('<Leave>',returnx_to_normalstate)
minimize_button.bind('<Enter>', changem_size_on_hovering)
minimize_button.bind('<Leave>', returnm_size_on_hovering)

root.bind("<FocusIn>",deminimize) 
root.after(10, lambda: set_appwindow(root)) 

def btn_clicked():
    b1['state']='disabled'
    print("Button Clicked")


root.resizable(False, False)
root.mainloop()