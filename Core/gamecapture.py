import numpy as np
import cv2
import pyautogui
from threading import Thread, Lock
from mss import mss

import win32gui
import win32ui
import win32con

class GameCapture:
    running = False
    lock = None
    screen_capture = None
    capture_area = None
    frame = None
    capture_frame = None
    windowname = None
    frame_number = 0
    frames_captured = 0
    w = 0
    h = 0

    def __init__(self, w = pyautogui.size()[0], h = pyautogui.size()[1], windowname = 'RuneScape Bot'):        

        self.screen_capture = mss()
        self.capture_frame = self.capture_frame_by_WIN32

        self.lock = Lock()
        self.capture_area = {"left": -30, "top": -30, "width": w, "height": h}
        self.w = w
        self.h = h
        self.windowname = windowname

    def start(self):
        self.running = True
        t = Thread(target=self.run)
        t.start()

    def stop(self):
        self.running = False

    def run(self):
        self.frame_number = 0

        while self.running:
            frame = self.capture_frame()
            self.lock.acquire()
            self.frame = frame
            self.frame_number += 1
            self.lock.release()


    def capture_frame_by_WIN32(self):
        self.frames_captured += 1
        try:
            hwnd = win32gui.FindWindow(None, 'RuneScape')
        except:
            hwnd = win32gui.GetDesktopWindow()
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj = win32ui.CreateDCFromHandle(wDC)

        cDC = dcObj.CreateCompatibleDC()
        bmp = win32ui.CreateBitmap()
        bmp.CreateCompatibleBitmap(dcObj, self.w, self.h)
        cDC.SelectObject(bmp)
        cDC.BitBlt((0,0), (self.w, self.h), dcObj, (0,0), win32con.SRCCOPY)
        
        signedIntsArray = bmp.GetBitmapBits(True)
        frame = np.fromstring(signedIntsArray, dtype='uint8')
        frame.shape = (self.h, self.w, 4)

        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(bmp.GetHandle())

        return cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

