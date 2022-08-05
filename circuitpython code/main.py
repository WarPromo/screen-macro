

######################################################



import time;
import usb_hid;
import board;
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode;
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS;


keyboard = Keyboard(usb_hid.devices);
layout = KeyboardLayoutUS(keyboard);

#Raspberry Pi Pico Version

import board,busio
from time import sleep
from adafruit_st7735r import ST7735R
from adafruit_display_text import label;
from adafruit_display_shapes.rect import Rect
import displayio
import zlib;
import json;
import terminalio
import adafruit_imageload
import digitalio
import zlib;
import os;
import usb_cdc;

mosi_pin = board.GP11
clk_pin = board.GP10
reset_pin = board.GP17
cs_pin = board.GP18
dc_pin = board.GP16
displayio.release_displays()
spi = busio.SPI(clock=clk_pin, MOSI=mosi_pin)
display_bus = displayio.FourWire(spi, command=dc_pin, chip_select=cs_pin, reset=reset_pin, baudrate=192000000)
display = ST7735R(display_bus, width=160, height=128, bgr = True, auto_refresh=False, native_frames_per_second=20, rotation=90)

group = displayio.Group();
display.show(group)

screenwidth = 160;
screenheight = 128;

icons = [];


panx = 0;
pany = 0;


targetpanx = 0;
targetpany = 0;

panaccel = 0.5;

xgap = 70;
ygap = 100;

outlinewidth = 1;
outlinecolor = 0xFFFFFF;

def loadicons():
    global icons,currentx,currenty;




    currentx = 0;
    currenty = 0
    with open("savedata.txt","r") as f:
        icons = json.load(f);

    while(len(group) > 0):
        group.pop();


    rect = Rect(-outlinewidth*2, -outlinewidth*2, 64 + outlinewidth*2, 64 + outlinewidth*2, outline=outlinecolor,stroke=outlinewidth)
    group.append(rect)

    yp = 0;
    for iconrow in icons:
        xp = 0;
        for icon in iconrow:

            image, palette = adafruit_imageload.load(icon["imagelocation"])

            icon["image"] = displayio.TileGrid(image, pixel_shader=palette)

            icon["x"] = xp;
            icon["y"] = yp;
            icon["image"].x = xp * xgap;
            icon["image"].y = yp * ygap;
            icon["textarea"] = [];

            group.append(icon["image"]);

            text = icon["name"];

            texts = text.split("ΰ");
            i = 0;
            for t in texts:


                text_area = label.Label(terminalio.FONT, text=t, color=0xFFFFFF)


                text_area.x = xp * xgap + (32 - int(text_area.width/2));
                text_area.y = yp * ygap + 70 + i * 14;



                icon["textarea"].append(text_area);

                group.append(text_area);

                i += 1;





            xp += 1;
        yp += 1;

def initializebutton(pin):

    btn1 = digitalio.DigitalInOut(pin);
    btn1.direction = digitalio.Direction.INPUT;
    btn1.pull = digitalio.Pull.DOWN;
    return btn1;

currentform = "Getform";
dontdelete = ["boot_out.txt"];

def writeback(string):
    usb_cdc.data.write(bytes(string, "utf-8"))

def checkloadfiles():
    global currentform;

    xs = b'';



    while usb_cdc.data.in_waiting > 0:



        ch = usb_cdc.data.read(1);
        xs += ch;



    if(len(xs) > 0):

        if(currentform != "Getform"):
            print("Write it.");
            writeback("Next");
            xs = zlib.decompress(xs);

            with open("./" + currentform, "wb") as f:
                thing2 = xs;
                f.write(thing2);
                f.close();

            currentform = "Getform";


            return;

        asciiform = xs.decode("utf-8");
        splits = asciiform.split(" ");

        if splits[0] == "Validfiles":

            files = os.listdir();

            for file in files:
                extensions = file.split(".");
                if(len(extensions[0]) == 0):
                    print("directory");
                    continue;
                if( (len(extensions) > 1) and (extensions[len(extensions)-1] != "py") and not (file in splits) and not (file in dontdelete)):
                    os.remove(file);
            print("Got valid files");
            writeback("Next")

            return;
        elif(currentform == "Getform"):

            if(asciiform == "Finished"):
                loadicons();
                return;

            currentform = asciiform;

            if(currentform in os.listdir() and currentform != "savedata.txt"):
                currentform = "Getform";
                writeback("Skip");
                print("Skip");
                return;
            print("Createfile: " + currentform);
            writeback("Next");
            return;

def sendstring(string):

    print(string);

    codelist = [];
    c = 0;



    for char in string:
        codes = layout.keycodes(char);

        if(len(codes) == 2):

            keyboard._keyboard_device.send_report(keyboard.report)
            keyboard.release_all();
            c = 0;

            for code in codes:
                keyboard._add_keycode_to_report(code)

            keyboard._keyboard_device.send_report(keyboard.report)
            keyboard.release_all();
            codelist = [];
            c = 0;
        else:
            if c == 6 or codes[0] in codelist:
                print("RELEASE ALL");
                keyboard._keyboard_device.send_report(keyboard.report)
                keyboard.release_all();
                c = 0;
                codelist = [];
                time.sleep(0.1);


            print("single code: " + char);
            keyboard._add_keycode_to_report(codes[0])
            codelist.append(codes[0]);
            c+=1;

    if len(codelist) > 0:
        keyboard._keyboard_device.send_report(keyboard.report)
        keyboard.release_all();


def dofunction(icon):
    option = icon["type"];

    data = open(icon["datalocation"], "r");

    if option == "Key-Combo":

        data = json.load(data);

        for action in data:

            print(action);

            if type(action) == int:

                print("SLEEP " + str(action));

                time.sleep(action/1000);

            if type(action) == str:

                action = action.upper();

                splits = action.split(" ");

                keycode = splits[0];

                if(keycode in keyreplace):
                    keycode = keyreplace[keycode];

                keycode = getattr(Keycode, keycode);

                print("PRESS " + str(keycode));

                if(splits[1] == "DOWN"):
                    keyboard.press(keycode);
                if(splits[1] == "UP"):
                    keyboard.release(keycode);

    if option == "Type Sentence":
        layout.write(data.read());

    if option == "Open file":
            keyboard.press(Keycode.GUI, Keycode.R);
            keyboard.release(Keycode.GUI, Keycode.R);
            time.sleep(0.2);
            layout.write(data.read().lower().replace("\\" + "\\", "\\"));
            keyboard.press(Keycode.ENTER);
            keyboard.release(Keycode.ENTER);

keyreplace = {

    "1": "ONE",
    "2": "TWO",
    "3": "THREE",
    "4": "FOUR",
    "5": "FIVE",
    "6": "SIX",
    "7": "SEVEN",
    "8": "EIGHT",
    "9": "NINE",
    "SLASH": "FORWARD_SLASH",
    "LCTRL": "LEFT_CONTROL",
    "LALT": "LEFT_ALT",
    "DOWN": "DOWN_ARROW",
    "LEFT": "LEFT_ARROW",
    "UP": "UP_ARROW",
    "RIGHT": "RIGHT_ARROW",
    "LSUPER": "GUI",
    "SUPER": "GUI"

}


home = initializebutton(board.GP0);
lastup = False;

left = initializebutton(board.GP1);
lasthome = False;

right = initializebutton(board.GP2);
lastleft = False;

down = initializebutton(board.GP3);
lastdown = False;

activate = initializebutton(board.GP4);
lastright = False;

up = initializebutton(board.GP5);
lastactivate = False;
currentx = 0;
currenty = 0;

loadicons();

while True:

    checkloadfiles();
    if(len(icons) == 0): continue;
    if(left.value and not lastleft):
        print("yuh ",currentx);
        currentx-=1;
    if(right.value and not lastright):
        print("yuh ",currentx);
        currentx+=1;
    if(up.value and not lastup):
        currenty-=1;
    if(down.value and not lastdown):
        print("yuh ",currentx);
        currenty+=1;
    if(home.value and not lasthome):
        print("yuh ",currentx);
        currenty = 0;
        currentx = 0;

    lastleft = left.value;
    lastright = right.value;
    lastup = up.value;
    lastdown = down.value;
    lasthome = home.value;


    if(currenty < 0): currenty = 0;
    if(currenty == len(icons)): currenty-=1;
    if(currentx < 0): currentx = 0;
    if(currentx >= len(icons[currenty])): currentx = len(icons[currenty])-1;


    if(activate.value and not lastactivate):

        print("RUNNING");
        dofunction(icons[currenty][currentx]);

    lastactivate = activate.value;


    targetpanx = currentx*xgap - (screenwidth/2 - 64/2);
    targetpany = currenty*ygap - (screenheight/2 - 64/2) + 15;

    if(len(group) == 0):

        print("append");

        for iconrow in icons:
            for icon in iconrow:
                group.append(icon["image"]);
                for area in icon["textarea"]:
                    group.append(area);




    panx = (targetpanx - panx) * panaccel + panx;
    pany = (targetpany - pany) * panaccel + pany;

    group.x = int(-targetpanx);
    group.y = int(-targetpany);

    group[0].x = currentx*xgap + int(panx - targetpanx) - outlinewidth;
    group[0].y = currenty*ygap + int(pany - targetpany) - outlinewidth;




    display.refresh();


    #sleep(1/20);
