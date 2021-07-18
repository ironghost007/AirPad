import cv2
import time
import HandTrackingModule as htm
import math
import numpy as np



scrW, scrH = 1280, 720
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, scrW)
cap.set(4, scrH)
canvas = cv2.imread("canvas.jpg")

tracking = htm.handDetector(detectionCon=0.8, maxHands=1)

actions = {'Draw': [1, 1, 1, 1, 1],
           'Erase All': [0, 0, 0, 1, 0],
           'Change Colour': [1, 1, 1, 1, 0],
           'Brush Size': [0, 0, 1, 1, 1]
           }

def f_status_indicator(R_lmList):
    f_tips = [20, 16, 12, 8, 4]
    action_status = []
    f_base = [17, 13, 9, 5, 1]
    wrist = [0]

    x3 = R_lmList[wrist[0]][1]
    y3 = R_lmList[wrist[0]][2]

    for finger in range(4):
        x1 = R_lmList[f_tips[finger]][1]
        y1 = R_lmList[f_tips[finger]][2]

        x2 = R_lmList[f_base[finger]][1]
        y2 = R_lmList[f_base[finger]][2]

        tip = math.sqrt(pow((x3 - x1), 2) + pow((y3 - y1), 2))
        base = math.sqrt(pow((x3 - x2), 2) + pow((y3 - y2), 2))

        if tip > base:
            action_status.append(1)
        else:
            action_status.append(0)

    a1, a2 = R_lmList[f_tips[-1]][1], R_lmList[f_tips[-1]][2]  # thumb tip
    b1, b2 = R_lmList[f_base[-2]][1], R_lmList[f_base[-2]][2]  # index base
    c1, c2 = R_lmList[f_base[-4]][1], R_lmList[f_base[-4]][2]  # ring base

    th_to_in = math.sqrt(pow((a1 - b1), 2) + pow((a2 - b2), 2))
    th_to_rg = math.sqrt(pow((a1 - c1), 2) + pow((a2 - c2), 2))

    if th_to_rg > th_to_in:
        action_status.append(1)
    else:
        action_status.append(0)

    return action_status


def cycle_color(curr_color, palette):
    i = 0
    while True:
        if curr_color == palette[i]:
            if i == len(palette) - 1:
                curr_color = palette[0]
                return curr_color
            else:
                curr_color = palette[i+1]
                return curr_color

        i += 1

def cycle_brush(curr_brush, stroke_size):
    i = 0
    while True:
        if curr_brush == stroke_size[i]:
            if i == len(stroke_size) - 1:
                curr_brush = stroke_size[0]
                return curr_brush
            else:
                curr_brush = stroke_size[i+1]
                return curr_brush

        i += 1

def draw_palette(canvas, img, palette, color, x1, x2):
    indi_colour = (0, 102, 102)
    for c in palette:
        cv2.rectangle(canvas, (x1, 5), (x2, 38), c, cv2.FILLED)
        cv2.rectangle(img, (x1, 5), (x2, 38), c, cv2.FILLED)

        if c == color:
            cv2.rectangle(canvas, (x1, 6), (x2 - 2, 36), indi_colour, 4)
            cv2.rectangle(img, (x1, 5), (x2 - 2, 38), indi_colour, 6)  # (0, 102, 102)

        x1 += 65
        x2 += 65

def draw_brush_size(canvas, img, strokes_size, brush, x):
    disp_colour = (226, 237, 5)
    indi_colour = (0, 102, 102)
    for b in strokes_size:
        cv2.circle(canvas, (x, 25), b, disp_colour, cv2.FILLED)
        cv2.circle(img, (x, 25), b, disp_colour, cv2.FILLED)                   # 5, 237, 226  bright blue

        if b == brush:                                                             # 136, 191, 242  cream colour
            cv2.circle(canvas, (x, 25), b + 3, indi_colour, 2)
            cv2.circle(img, (x, 25), b + 3, indi_colour, 2)

        x += 40


def main():
    strokes = []
    palette = [(255, 255, 255), (0, 0, 255), (0, 255, 0),  # white, red, green,
               (255, 0, 0), (0, 255, 255), (255, 0, 255)]  # blue, yellow, magenta

    strokes_size = [6, 10, 14, 16, 18]

    color = palette[0]
    brush = strokes_size[0]

    open_time = 0.0
    close_time = 0.0
    ch1 = 0
    ch2 = 0

    stroke_time = 0

    palette_box_start = 7  # 180
    palette_box_end = 72  # 245

    brush_start = 1080





    while True:
        success, img = cap.read()
        flipped = cv2.flip(img, 1)

        img = tracking.findHands(flipped, draw=False)
        lmList = tracking.findPosition(img, draw=False)
        hand = tracking.hand_LR()

        cv2.rectangle(canvas, (0, 0), (scrW, scrH), (0, 0, 0), cv2.FILLED)
        cv2.rectangle(img, (0, 0), (scrW, 50), (0, 0, 0), cv2.FILLED)

        cv2.line(canvas, (0, 50), (scrW, 50), (255, 255, 255), 4)
        cv2.line(img, (0, 50), (scrW, 50), (255, 255, 255), 4)

        if len(lmList) != 0 and hand == 'Right':
            status = f_status_indicator(lmList)

            for action, stat in actions.items():
                if stat == status and action == "Draw":
                    if lmList[8][2] > 60:
                        stroke_time = (time.time() * 1000)
                        strokes.append([lmList[8], color, brush, stroke_time])

                if stat == status and action == 'Erase All':
                    if len(strokes) != 0:
                        for st in strokes:
                            pt = st[0]
                            br = st[2]
                            cv2.circle(canvas, (pt[1], pt[2]), br, (0, 0, 0), cv2.FILLED)
                            cv2.circle(canvas, (pt[1] - 3, pt[2] - 2), br, (0, 0, 0), cv2.FILLED)
                            cv2.circle(canvas, (pt[1] + 2, pt[2] + 2), br, (0, 0, 0), cv2.FILLED)

                    cv2.rectangle(canvas, (0, 0), (scrW, scrH), (0, 0, 0), cv2.FILLED)
                    cv2.line(canvas, (0, 50), (scrW, 50), (255, 255, 255), 4)
                    del strokes[:]

                    # flag = 0

                if stat == status and action == 'Change Colour':
                    if ch1 == 0:
                        open_time = time.time()
                        color = cycle_color(color, palette)

                if stat == status and action == 'Brush Size':
                    if ch2 == 0:
                        open_time = time.time()
                        brush = cycle_brush(brush, strokes_size)


        draw_palette(canvas, img, palette, color, palette_box_start, palette_box_end)
        palette_box_start = 7  # 180
        palette_box_end = 72  # 245

        draw_brush_size(canvas, img, strokes_size, brush, brush_start)
        brush_start = 1080


        if len(strokes) != 0:
            i = 0
            for st in strokes:
                if i >= 1:
                    prev = strokes[i-1]
                    curr = strokes[i]
                    col1 = prev[1]
                    col2 = curr[1]
                    br1 = prev[2]
                    br2 = curr[2]
                    ti1 = prev[3]
                    ti2 = curr[3]

                    if br1 == br2 and col1 == col2 and (ti2 - ti1) < 200 or (abs(prev[0][1] - curr[0][1]) <= 10 \
                        or abs(prev[0][2] - curr[0][2]) <= 10):
                        cv2.line(img, (prev[0][1], prev[0][2]), (curr[0][1], curr[0][2]), col1, br1+9)
                        cv2.line(canvas, (prev[0][1], prev[0][2]), (curr[0][1], curr[0][2]), col1, br1+9)

                pt = st[0]
                col = st[1]
                br = st[2]

                cv2.circle(img, (pt[1], pt[2]), br, col, cv2.FILLED)
                cv2.circle(canvas, (pt[1], pt[2]), br, col, cv2.FILLED)

                i += 1

        if len(lmList) != 0 and hand == 'Right':
            temp = lmList[8]
            cv2.circle(img, (temp[1], temp[2]), 15, (255, 153, 204), 3)
            cv2.circle(canvas, (temp[1], temp[2]), 15, (255, 153, 204), 3)

        close_time = time.time()
        if close_time-open_time > 2.0:
            ch1 = 0
        else:
            ch1 = 1


        close_time = time.time()
        if close_time-open_time > 2.0:
            ch2 = 0
        else:
            ch2 = 1

        cv2.imshow("AirPad", img)
        cv2.imshow("Canvas", canvas)
        if cv2.waitKey(1) & 0xFF == 27:
            cv2.destroyAllWindows()
            break


main()



