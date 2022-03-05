import pydirectinput

from pyHM import mouse
import keyboard as kb
import cv2
import random
import win32gui
import psutil

from time import time, sleep
from threading import Thread, Lock

from gamecapture import GameCapture
from detect import Detection
from vision import Vision

x_min, x_max, y_min, y_max = 177, 202, 402, 855

class WoodCutter:
    capture = None
    detector = None
    vision = None

    is_running = False
    is_active = False
    lock = None
    state = None

    frame = None
    active_targets = None
    action_history = None
    mirror_ratio = 1
    start_time = 0
    trees_chopped = 0
    

    def __init__(self, mr=1):
        self.lock = Lock()
        self.active_targets = []
        self.action_history = []
        self.mirror_ratio = 1 / mr
        self.camMoveCount = 0
        self.back_track_count = 0

        self.capture = GameCapture()
        self.detector = Detection()
        self.vision = Vision()
        self.tree_tooltip = cv2.imread('./Core/ingame_images/tree_tooltip.jpg', cv2.IMREAD_UNCHANGED)
        self.full = cv2.imread('./Core/ingame_images/full.jpg', cv2.IMREAD_UNCHANGED)
        self.logs = cv2.imread('./Core/ingame_images/logs.jpg', cv2.IMREAD_UNCHANGED)
        self.chopped = cv2.imread('./Core/ingame_images/chopped.jpg', cv2.IMREAD_UNCHANGED)
        self.backpack = cv2.imread('./Core/ingame_images/backpack.jpg',cv2.IMREAD_UNCHANGED)
        self.trees_chopped = 0
        self.chopped_tree = False
        self.click_history = []

    def user_kill_signal(self):
        if kb.is_pressed('='):
            self.stop()
            return True
        return False

    def choosePhrase(self):
        num = random.randint(0, 20)
        if num == 0:
            return "i already cut down {} trees".format(self.trees_chopped)
        elif num == 2:
            return "im a woodcutting god i already cut down {} trees".format(self.trees_chopped)
        elif num == 3:
            return "{} trees cut down and {} trees to go".format(self.trees_chopped, self.trees_chopped+int(random.randint(0,10000)))
        else:
            return None

    def monitor_toggle_actions(self):
        while self.is_running:
            self.user_kill_signal()
           
    def display(self, frame):
        print('Trees Chopped: {}'.format(self.trees_chopped))
        ### Uncomment the below line to see what the bot detects
        #cv2.imshow('MIRROR: ' + self.capture.windowname, cv2.resize(frame, (0,0), fx=self.mirror_ratio, fy=self.mirror_ratio))
        if cv2.waitKey(1) & 0xFF == ord('='):
            self.stop()

    def randomPhrases(self):
        s = self.choosePhrase()
        if s is not None:
            pydirectinput.press('enter')
            sleep(0.2)
            pydirectinput.typewrite(s, interval=0.1)
            pydirectinput.press('enter')
            sleep(0.2)

    def run_single_thread(self):
        while self.is_running:
            try:
                if self.user_kill_signal():
                    break
                frame = self.capture.capture_frame()

                if self.is_active:
                    predictions = self.detector.detect(frame)
                    target = self.vision.get_priority_target(predictions)
                    frame = self.vision.draw_bounding_boxes(frame, predictions)
                    
                    if target is not None:
                        self.chopTree(target)
                    else:
                        if(len(self.click_history) > 0 and self.back_track_count < 3):
                            self.backTrack()
                        else:
                            self.moveCamera(2)
                            print("Moving Camera")
                            self.back_track_count = 0

                self.display(frame)
                
            except Exception as e:
                print(e)
                pass

        #out.release()
        cv2.destroyAllWindows()
        print('Chopped down {} trees'.format(self.trees_chopped))

    def chopTree(self, target):
        try:
            if (target[0] < self.capture.w - 20 and target[0] > 20) \
                and (target[1] < self.capture.h - 20 and target[1] > 20):
                cleared_inv = False
                mouse.move(target[0], target[1])
                sleep(0.8)
                if(self.isTree()):
                    mouse.click()
                    self.click_history.append((target[0], target[1]))
                    if random.randint(0,2)==1: self.randomMouseMovement()
                    a = 0
                    while a < 8:
                        if(self.invFull()):
                            self.clearInv()
                            cleared_inv = True
                            print("Inventory Cleared")
                            break
                        a+=1
                        sleep(1)
                    self.action_history.append((time() - self.start_time, target))
                    sleep(2)
                    if not cleared_inv:
                        if not self.chopped_tree:
                            self.isChopping(0.8)
                    
                            sleep(1)

                        self.trees_chopped += 1
                        self.chopped_tree = False
                        self.randomPhrases()
                else:
                    self.moveCamera(0.3)
                    target = None
                    sleep(1)
            else:
                raise Exception('Target out of screen bounds.')
        except Exception as e:
            mouse.move(self.capture.w/2, self.capture.h/2)
            self.action_history.append((time() - self.start_time, ('OOB')))

    def isTree(self):
        sc = self.capture.capture_frame()
        result = cv2.matchTemplate(sc, self.tree_tooltip, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val > 0.45:
            return True
        return False

    def invFull(self):
        sc = self.capture.capture_frame()
        result = cv2.matchTemplate(sc, self.full, cv2.TM_CCOEFF_NORMED)
        min_val2, max_val2, min_loc2, max_loc2 = cv2.minMaxLoc(result)
        if max_val2 >= 0.40:
            if not self.backpackOpen():
                pydirectinput.press('b')
            sleep(0.2)
            return True
        return False

    def backpackOpen(self):
        sc = self.capture.capture_frame()
        result = cv2.matchTemplate(sc, self.backpack, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= 0.8:
            return True
        return False


    def clearInv(self):
        sc = self.capture.capture_frame()
        result = cv2.matchTemplate(sc, self.logs, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if(max_val >= 0.60):
            mouse.move(max_loc[0]+random.randint(5,8), max_loc[1]+random.randint(5,8))
            sleep(self.randomDelay(0,1))
            mouse.down()
            mouse.move(max_loc[0]-random.randint(100,300), max_loc[1]-random.randint(100,300))
            sleep(self.randomDelay(0,1))
            mouse.up()
            sleep(0.8)
            self.clearInv()

    def isChopping(self, thresh):
        sc = self.capture.capture_frame()
        self.randomMouseMovement()
        result = cv2.matchTemplate(sc, self.chopped, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val < thresh:
            sleep(1.2)
            self.isChopping(thresh-0.02)
        elif thresh <= 0.38:
            self.trees_chopped -= 1
        self.chopped_tree = True

    def moveCharacter(self):

        screen_x = random.randint(x_min, x_max)
        screen_y = random.randint(y_min, y_max)
        
        print('Moving to x:{} y:{}'.format(screen_x, screen_y))
        mouse.move(screen_x, screen_y)

        sleep(self.randomDelay(0, 1))
        #print(screen_x, screen_y)
        mouse.click()
        sleep(0.2)

    def moveCamera(self, max):
        r = random.randint(0,2)
        if(r == 2):
            pydirectinput.keyDown('a')
            sleep(self.randomDelay(0.2,max))
            pydirectinput.keyUp('a')
            sleep(self.randomDelay(0.2,max))
        else:
            pydirectinput.keyDown('d')
            sleep(self.randomDelay(0.2,max))
            pydirectinput.keyUp('d')
            sleep(self.randomDelay(0.2,max))
        self.camMoveCount += 1
        sleep(self.randomDelay(0.5,1.4))

    def randomDelay(self, a, b):
        new_a = a * 100
        new_b = b * 100
        out = random.randint(new_a, new_b)/100.0
        return out

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.start_time = time()
            t = Thread(target=self.run_single_thread)
            t.start()

    def stop(self):
        self.lock.acquire()
        self.is_running = False
        self.is_active = False
        self.lock.release()
    
    def update(self, frame):
        self.lock.acquire()
        self.frame = frame
        self.lock.release()

    def is_active(self):
        active = 0
        self.lock.acquire()
        active = self.is_active
        self.lock.release()
        return active

    def backTrack(self):
        prev_click = self.click_history.pop()
        #print('Prev: {}'.format(prev_click))
        pos = (int(self.capture.w/2), int(self.capture.h/2))
        #print('pos: {}'.format(pos))
        mirror_x = pos[0] - (prev_click[0]-pos[0])
        mirror_y = pos[1] - (prev_click[1]-pos[1])

        mouse.move(mirror_x, mirror_y)
        #print(mirror_x, mirror_y)
        sleep(self.randomDelay(1,2))
        mouse.click()
        self.back_track_count += 1
        print('Backtracking: {}'.format(self.back_track_count))
        sleep(self.randomDelay(4,5))

    def randomMouseMovement(self):
        x = random.randint(100,1820)
        y = random.randint(100, 980)
        mouse.move(x, y)
        sleep(0.1)

def _windowEnumHandler(hwnd, top_windows):
    top_windows.append((hwnd, win32gui.GetWindowText(hwnd)))

def openGame(window_name):
    top_windows = []
    win32gui.EnumWindows(_windowEnumHandler, top_windows)
    for i in top_windows:
        #print(i[1])
        if window_name.lower() in i[1].lower():
            #print("found", window_name)
            try:
                #win32gui.ShowWindow(i[0], win32con.SW_SHOWNORMAL)
                win32gui.SetForegroundWindow(i[0])
            except:
                print("Can't open {}".format(window_name))
            break

def checkIfGameOpen():
    for proc in psutil.process_iter():
        try:   
            if "RuneScape.exe".lower() in proc.name().lower():
                return True 
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def main():
    if not checkIfGameOpen():
        print("Please open RuneScape")
    else:
        openGame('RuneScape')
        aimbot = WoodCutter(mr=3)
        aimbot.start()


gui = pydirectinput
if __name__ == '__main__':
    gui.PAUSE = 0

    print("Press '=' to stop.")
    main()