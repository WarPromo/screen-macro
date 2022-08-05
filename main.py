import pygame, sys
import time
import os.path;
import os;
import numpy
import json;
import base64
import serial;
import threading
import zlib;
from PIL import Image;


print(time.time());


filesuploading = -1;
filesuploadinglength = -1;


def readfile(name):
    with open("./save/" + name) as f:
        return f.read();

def writefile(name, data):
    with open("./save/" + name, "w") as f:
        f.write(data);
        f.close();

def deletefile(name):
    os.remove("./save/" + name);

def getid():
    return int(time.time() * 10000000);

def uploadfile(dir, output, ser):
    thebytes = bytes(output, "utf-8");
    print("Uploading " + output + " from " + dir)
    ser.write(thebytes);





    thing = "";
    while(len(thing) == 0):
        thing = ser.read(10000)
        if thing == b'\r\n': thing = "";





    if(thing != b'Next'):

        print(thing);
        return;

    currenttime = time.time();
    imagebase64 = "";
    with open(dir, 'rb') as fp:
        imagebase64 = fp.read();

    print("bytes");


    imagebase64 = zlib.compress(imagebase64);


    print(imagebase64)

    ser.write(imagebase64);

    print("written in " + str(time.time() - currenttime));

    thing = "";
    while(len(thing) == 0):
        thing = ser.read(10000)


#ser = serial.Serial('COM7', 38400, timeout=0.01, parity=serial.PARITY_EVEN, rtscts=False)
#uploadfile("yuhgucci.zip", "yuhgucci.zip", ser);

def uploadsavedirectory():
    global filesuploading;
    global filesuploadinglength;

    ser = serial.Serial('COM7', 38400, timeout=0.01, parity=serial.PARITY_EVEN, rtscts=False)

    print("connected to port");

    dir_list = os.listdir("./save");

    filesuploading = 0;
    filesuploadinglength = len(dir_list);



    valids = "Validfiles " + " ".join(dir_list);

    thebytes = bytes(valids, "utf-8");
    ser.write(thebytes);


    thing = "";
    while(len(thing) == 0):
        thing = ser.read(10000)

    print("Told valid files " + valids);


    for file in dir_list:
        uploadfile("./save/" + file, file, ser)
        filesuploading += 1;
        print("Uploaded " + file);



    thebytes = bytes("Finished", "utf-8");
    ser.write(thebytes);

    print("Finished uploading");
    filesuploading = -1;

    ser.close();

def beginupload():
    t1 = threading.Thread(target=uploadsavedirectory)
    t1.start();


class macro():

    def __init__(self, imagelocation="emptyimage.bmp", datalocation="empty.txt",name="empty", temp = False, type="empty"):


        self.imagelocation = imagelocation;
        self.image = pygame.image.load("./save/" + imagelocation);
        self.image = pygame.transform.scale(self.image, (64,64));

        print(datalocation);

        with open("./save/" + datalocation) as f:
            self.data = json.loads(f.read());
            self.datalocation = datalocation;

        self.name = name;
        self.temp = temp;
        self.type = type;

    def initimage():
        if(imagelocation == "empty"):
            self.image = pygame.image.load("./save/emptyimage.bmp")
            self.image = pygame.transform.scale(self.image, (64,64));
            self.imagelocation = "emptyimage.bmp";
        else:
            self.image = pygame.image.load("./save/" + imagelocation);
            self.image = pygame.transform.scale(self.image, (64,64));
            self.imagelocation = imagelocation;

    def initdata():
        if(datalocation == "empty"):
            self.data = [];
            self.datalocation = "empty";
        else:
            with open("./save/" + datalocation) as f:
                self.data = json.loads(f.read());
                self.datalocation = datalocation;


def iconlist_to_string(icons,savedir):
    list = [];

    safefiles = ["savedata.txt", "emptyimage.bmp", "empty.txt"];

    n = 0;
    for iconrow in icons:
        list.append([]);
        index = len(list)-1;
        for icon in iconrow:
            n += 1;
            list[index].append(macro_to_obj(icon,savedir));
            safefiles.append(icon.imagelocation);
            safefiles.append(icon.datalocation);

    dir_list = os.listdir(savedir);

    print(safefiles);

    for file in dir_list:

        if not (file in safefiles):
            print("DELETE " + file);
            deletefile(file);

    return json.dumps(list);

def string_to_iconlist(icons,savedir):

    icons = json.loads(icons);

    list = [];

    for iconrow in icons:
        list.append([]);
        index = len(list)-1;
        for icon in iconrow:
            list[index].append(obj_to_macro(icon,savedir));

    return list

def macro_to_obj(macro, savedir):

    toreturn = {
        "imagelocation":"",
        "name":"",
        "type":"",
        "datalocation":"",
        "sizex":"",
        "sizey":"",
    }

    surfacesize = macro.image.get_size();

    toreturn["sizex"] = 64;
    toreturn["sizey"] = 64;
    toreturn["datalocation"] = macro.datalocation;
    toreturn["type"] = macro.type;
    toreturn["name"] = macro.name;
    toreturn["imagelocation"] = macro.imagelocation;

    if(os.path.exists("./save/" + macro.imagelocation) == False ):

        scaled = pygame.transform.scale(macro.image, (toreturn["sizex"], toreturn["sizey"]) );
        pygame.image.save(scaled, savedir + "/temp" + macro.imagelocation);
        img = Image.open(savedir + "/temp" + macro.imagelocation)
        newimg = img.convert(mode='P', colors=15);
        newimg.save(savedir + "/" + macro.imagelocation)


    if(os.path.exists("./save/" + macro.datalocation) == False ): writefile(macro.datalocation, json.dumps(macro.data));

    return toreturn;

def obj_to_macro(obj, savedir):
    toreturn = macro(imagelocation = obj["imagelocation"], name=obj["name"], temp=False, type=obj["type"], datalocation=obj["datalocation"]);
    return toreturn;

def saveicons_to_file(filename,savedir,icons):
    file = open(savedir + "/" + filename, 'w');
    string = iconlist_to_string(icons, savedir);
    file.write(string);
    file.close();

def loadicons_from_file(filename,savedir):
    string = "nothing";
    with open(savedir + "/" + filename) as f:
        string = f.read()
    return string_to_iconlist(string,savedir);



mainClock = pygame.time.Clock();
pygame.init();

events = "none";

pygame.font.init()

arialfont = pygame.font.SysFont('Arial', 30);
arialfontsmall = pygame.font.SysFont('Arial', 17);
arialfonticon = pygame.font.SysFont('Arial', 13);

pygame.display.set_caption("Simplecro");
screen = pygame.display.set_mode((1000,700));

panx = 0;
pany = 0;


savedir = "./save";

def mousetocoord(mousex, mousey):
    return ( mousex+panx, mousey+pany );


backgroundimage = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/background.png");
backgroundimage.set_alpha(100);

recordicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/recordicon.png");
recordholdingicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/recordholdingicon.png");
recordhovericon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/recordhovericon.png");
recordnothingicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/recordnothingicon.png");
uparrow = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/uparrow.png");
downarrow = pygame.transform.flip(uparrow, False, True);
addicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/addiconhover.png");
settingsicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/settingsicon.png");
dragicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/dragicon.png");
closeicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/closeiconhover.png");
saveicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/saveicon.png");
garbageicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/garbageicon.png");
cloneicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/copyicon.png");
uploadicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/uploadicon.png");
savediconsicon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/savedicons.png");
restarticon = pygame.image.load("C:/Users/Ritik/Desktop/macro 3key/restarticon.png");

icons = [
            [macro(name="shit"), macro(name="shithit"), macro(name="shitht")],
            [macro(name="shit"), macro(name="shithit"), macro(name="shitht")],
            [macro(name="shit"), macro(name="shithit"), macro(name="shitht")]
        ]

icons = loadicons_from_file("savedata.txt", savedir);

heldicon = "empty"

justclicked = False;
justreleased = False;

holding = False;

framedraw = False;
framedragging = False;

framex = 100;
framey = 100;
framewidth = 400;
frameheight = 400;

iconsx = 200;
iconsy = 100;

frameselectedicon = "empty";
frameoptions = ["Key-Combo", "Type Sentence", "Open file"];
frameoption = "Key-Combo";
framedropdown = False;

framekeycombo = [];
framekeycombostart = 1;
framekeycomborec = False;
framekeycombolast = 0;
framekeycombowaitdragy = "none";
framekeycombowaitindex = "none";
framekeycombokeyedit = -1;
framekeycombokeydrag = -1;

framesentence = [];

framefilelocation = [];

frameicon = "";

textediting = "empty"

filedrop = "empty";
textfiledrop = "empty";
anyfiledrop = "empty";

setfileempty = -1;


mousex = 0;
mousey = 0;


capturedscroll = False;

nothoveringanything = True;
panmode = "empty";

saveiconsdone = 0;

cursor = pygame.SYSTEM_CURSOR_ARROW;

lastmousefocus = True;

def drawrect(a,b,c,d=-1):
    c.x -= panx;
    c.y -= pany;
    if d != -1:
        pygame.draw.rect(a,b,c,d)
    else:
        pygame.draw.rect(a,b,c)


def screenblit(a,b,c):
    a.blit(b,(c[0]-panx,c[1]-pany));





def resetframe():

    global framedragging
    global frameselectedicon
    global framekeycombo
    global framekeycombostart
    global framekeycomborec
    global framekeycombolast
    global framekeycombowaitdragy
    global framekeycombowaitindex
    global framekeycombokeyedit
    global framekeycombokeydrag
    global framesentence
    global framefilelocation
    global frameicon
    global textediting

    framedragging = False;
    frameselectedicon = "empty";
    framekeycombo = [];
    framekeycombostart = 1;
    framekeycomborec = False;
    framekeycombolast = 0;
    framekeycombowaitdragy = "none";
    framekeycombowaitindex = "none";
    framekeycombokeyedit = -1;
    framekeycombokeydrag = -1;
    framesentence = "";
    framefilelocation = "";
    frameicon = "";
    textediting = "empty"






def update():

    global holding
    global justclicked
    global justreleased
    global heldicon
    global textediting
    global framedraw;
    global framex;
    global framey;
    global filedrop;
    global textfiledrop
    global anyfiledrop;
    global events;
    global setfileempty;
    global frameicon;
    global framekeycombo;
    global framesentence;
    global framefilelocation;
    global frameoption;
    global uparrow;
    global mousex,mousey;
    global zoom;
    global panx;
    global pany;
    global nothoveringanything;
    global saveiconsdone;
    global restarticon
    global icons;

    global cursor;
    global lastmousefocus
    global savedir


    while True:


        cursor = pygame.SYSTEM_CURSOR_ARROW;

        screen.fill((0,0,0));


        nothoveringanything = True;

        truemousex, truemousey = pygame.mouse.get_pos()
        mousex, mousey = mousetocoord(truemousex, truemousey);

        events = pygame.event.get();

        keys = pygame.key.get_pressed()

        screenblit(screen, backgroundimage, (0, 200))

        for event in events:

            if(event.type == pygame.QUIT):

                sys.exit();

            if(event.type == pygame.MOUSEBUTTONDOWN ):

                if(event.button == 1):
                    justclicked = True;
                    holding = True;

            if(event.type == pygame.MOUSEBUTTONUP):
                if(event.button == 1):
                    holding = False;
                    justreleased = True;

            if(event.type == pygame.DROPFILE):
                file_extension = os.path.splitext(event.file)[1]
                if file_extension in [".bmp", ".jpg", ".png"]:
                    filedrop = event.file;
                    print("file dropped " + event.file)

                if file_extension in [".txt"]:
                    textfiledrop = event.file;
                    print("text file dropped " + event.file)

                anyfiledrop = event.file;
                print(anyfiledrop);
                setfileempty = 2;






        yr = iconsy;
        i = 0


        alphastage = [0.35,1];


        if filesuploading >= 0: alphastage = [0.15,0.15,0.15];

        saveicons = drawbutton(iconsx,yr,64,64,image=saveicon, alphastages=alphastage)
        restarticons = drawbutton(iconsx+70,yr,64,64,image=restarticon, alphastages=alphastage)
        uploadicons = drawbutton(iconsx+140,yr,64,64,image=uploadicon, alphastages=alphastage)




        if(filesuploading >= 0):
            drawrect(screen, (0,0,255), pygame.Rect(iconsx+140, yr, 64 * (filesuploading / filesuploadinglength), 5));
            drawrect(screen, (255,255,255), pygame.Rect(iconsx+140+ 64*(filesuploading / filesuploadinglength), yr, 64 - 64 * (filesuploading / filesuploadinglength), 5));
        elif uploadicons:
            beginupload();
        elif saveicons:
            drawbutton(iconsx,yr,64,64,image=saveicon, alphastages=[0.5,0.5])

            print("icons saved");

            saveicons_to_file("savedata.txt",savedir,icons);
            saveiconsdone = 30;

        elif restarticons:
            icons = loadicons_from_file("savedata.txt",savedir);
            if framedraw:
                framedraw = False;

        if saveiconsdone > 0:
            drawbutton(iconsx,yr,64,64,image=savediconsicon, alphastages=[0.5,0.5])

        yr += 80

        while i < len(icons):

            iconrow = icons[i];
            xr = iconsx;
            j = 0

            templast = False;




            framecollision = framedraw and colliding(framex,framey,framewidth,frameheight,mousex,mousey)

            deleterow = drawbutton(xr,yr+17,30,30,image=garbageicon, alphastages=[0.2,1]);

            if(deleterow):
                icons.pop(i);
                justclicked = False;
                continue;


            xr += 34

            up = drawbutton(xr, yr, 20, 30, image=uparrow, alphastages=[0.5,1]);
            down = drawbutton(xr, yr + 34, 20, 30, image=downarrow, alphastages=[0.5,1]);

            if not framecollision:

                if up and i > 0:
                    icons[i], icons[i-1] = icons[i-1], icons[i]
                if down and i < len(icons)-1:
                    icons[i], icons[i+1] = icons[i+1], icons[i]


            xr += 24;

            if framecollision:
                nothoveringanything = False;


            while j < len(iconrow):

                icon = iconrow[j];

                collision = colliding(xr, yr, 68, 64, mousex, mousey);
                macrocollision = colliding(xr + 40, yr + 5, 20, 20,mousex,mousey);
                garbagecollision = colliding(xr+40, yr + 64 - 25, 20, 20,mousex,mousey);




                if framecollision:
                    collision = False;
                    macrocollision = False;
                    garbagecollision = False;



                templast = icon.temp;

                if heldicon != "empty":

                    if heldicon[0] == i and heldicon[1] == j:
                        j+=1;
                        continue;

                    if icon.temp and collision == False:
                        iconrow.pop(j)

                        if heldicon[0] == i and j < heldicon[1]:
                            heldicon[1] -= 1;

                        continue;

                    if holding == False and icon.temp and collision != False:

                        icons[i][j] = icons[heldicon[0]][heldicon[1]]
                        icons[heldicon[0]].pop(heldicon[1])
                        if(i == heldicon and j > heldicon[1]): j-=1;
                        heldicon = "empty";


                    if holding and collision != False and icon.temp == False:

                        tempicon = macro(imagelocation=heldicon[4].imagelocation, name=heldicon[4].name, temp=True)

                        if heldicon[0] == i and j <= heldicon[1]:
                            heldicon[1] += 1;

                        iconrow.insert(j, tempicon)

                        icon = iconrow[j];
                elif icon.temp == False and macrocollision and justclicked:

                    resetframe();

                    framedraw = True;
                    frameicon = icons[i][j];

                    if frameicon.type != "empty":
                        frameoption = frameicon.type;

                        print("it's not empty ");
                        print(frameicon.data);

                        if frameicon.type == "Type Sentence":
                            framesentence = frameicon.data;
                        if frameicon.type == "Open file":
                            framefilelocation = frameicon.data;
                        if frameicon.type == "Key-Combo":
                            framekeycombo = frameicon.data[:];

                        print("yuh two")
                        print(framekeycombo);

                    framex = xr + 80;
                    framey = yr - frameheight / 4;
                elif icon.temp == False and garbagecollision and justclicked:
                    iconrow.pop(j);
                    justclicked = False;
                    continue;
                elif collision != False and justclicked:
                    heldicon = [i,j, collision[0], collision[1], icons[i][j]]

                if filedrop != "empty" and collision != False:
                    print("load it");
                    #icon.image = pygame.transform.scale(pygame.image.load(filedrop), (32,32));
                    icon.image = pygame.transform.scale(pygame.image.load(filedrop), (64,64));
                    icon.imagelocation = str(getid()) + ".bmp";
                    print(icon.imagelocation);

                texts = icon.name.split("ΰ")
                textsurfaces = [];
                for text in texts:
                    textsurfaces.append( arialfonticon.render(text, False, (255, 255, 255)) );
                texti = 0;

                if textediting[0] == i and textediting[1] == j:

                    millis = time.time() * 1000

                    lastwidth = textsurfaces[len(texts)-1].get_size()[0];
                    endx = lastwidth/2 + 32;

                    if millis % 1500 > 1500/2:
                        drawrect(screen, (255,255,255), pygame.Rect(xr+endx+1, yr+64 + (len(texts)-1)*14, 2, 15));

                if framecollision == False and colliding(xr,yr+60,64,30,mousex,mousey):
                    if textediting[0] != i or textediting[1] != j: drawrect(screen, (105,105,0), pygame.Rect(xr, yr+60, 64, 30))
                    if justclicked:
                        print("clicekd me");
                        textediting = [i,j];
                elif textediting[0] == i and textediting[1] == j and justclicked:
                    textediting = "empty";






                for surface in textsurfaces:
                    dx = 32 - surface.get_size()[0]/2;
                    screenblit(screen,surface,(xr + dx,yr+64+texti*14));
                    texti+=1;


                col = (255,255,255)

                if(icon.image == "empty"): drawrect(screen, col, pygame.Rect(xr, yr, 64, 64))
                else:
                    screenblit(screen,icon.image, (xr, yr))

                if collision and not macrocollision and not garbagecollision:
                    drawbutton(xr, yr, 64, 64, image = dragicon, alphastages = [0.35,0.35]);

                if icon.temp == False and collision != False:
                    drawbutton(xr + 40, yr + 5, 20, 20, image=settingsicon, alphastages=[0.5,1]);
                    drawbutton(xr + 40, yr + 64 - 25, 20, 20, image=garbageicon, alphastages=[0.5,1]);







                xr += 68;
                j+=1


            collision = colliding(xr, yr, 68, 64, mousex, mousey);

            if heldicon != "empty" and collision != False and templast == False:
                tempicon = macro(temp=True);
                tempicon.image = heldicon[4].image;

                iconrow.append(tempicon)

                xr += 68


            createnew = drawbutton(xr, yr, 64, 64, image=addicon, alphastages=[0.5,1]);

            if createnew and framecollision == False:
                toappend = macro()
                iconrow.append(toappend);


            yr = yr + 100
            i = i + 1

        createnew = drawbutton(iconsx, yr - 6, 64, 64, image=addicon, alphastages=[0.5,1]);

        if createnew and framecollision == False:
            icons.append([]);



        if framedraw:
            drawframe();

        if holding == False:
            heldicon = "empty";

        if heldicon != "empty":

            if(heldicon[4].image == "empty"): drawrect(screen, (175, 175, 175), pygame.Rect(mousex - heldicon[2], mousey - heldicon[3], 64, 64))
            else:
                heldicon[4].image.set_alpha(150)
                screenblit(screen,heldicon[4].image,(mousex - heldicon[2], mousey - heldicon[3]));
                heldicon[4].image.set_alpha(255)

        if textediting != "empty":

            for event in events:

                if event.type == pygame.KEYDOWN:



                    if event.key == pygame.K_BACKSPACE:
                        icons[textediting[0]][textediting[1]].name = icons[textediting[0]][textediting[1]].name[:-1]
                    elif event.key == pygame.K_RETURN:
                        icons[textediting[0]][textediting[1]].name += "ΰ";
                    else:

                        icons[textediting[0]][textediting[1]].name += event.unicode



        if setfileempty > 0:
            setfileempty -= 1;
        if setfileempty <= 0:
            textfiledrop = "empty";
            filedrop = "empty";
            anyfiledrop = "empty";

        if saveiconsdone > 0:
            saveiconsdone -= 1;



        if heldicon != "empty":
            cursor = pygame.SYSTEM_CURSOR_SIZEALL

        if justclicked and nothoveringanything:
            print("we good");
            panmode = [truemousex, truemousey, panx+0, pany+0];


        if not holding:
            panmode = "empty";

        if holding and panmode != "empty":



            panx = -truemousex + panmode[0] + panmode[2]
            pany = -truemousey + panmode[1] + panmode[3]
            cursor = pygame.SYSTEM_CURSOR_SIZEALL

#        if(panx < 0):
#            panmode[0] = truemousex;
#            panmode[2] = 0;
#            panx = 0;
#        if(pany < 0):
#            panmode[1] = truemousey;
#            panmode[3] = 0;
#            pany = 0;
#
#
#       if(panx < 0): print(panx);

        pygame.mouse.set_cursor(cursor);

        lastmousefocus =  pygame.mouse.get_focused()

        mainClock.tick(120)
        pygame.display.update();
        justclicked = False;
        justreleased = False;






def drawframe():

    global framex;
    global framey;
    global framewidth
    global frameheight
    global framedragging
    global framedraw;
    global framedropdown
    global frameoption
    global frameicon;
    global framekeycombo
    global framekeycombostart
    global framekeycombolast
    global framekeycombowaitdragy;
    global framekeycombowaitindex;
    global framekeycombokeyedit;
    global framekeycombokeydrag;
    global framefilelocation;
    global textfiledrop;
    global anyfiledrop;
    global framesentence;
    global mousex;
    global mousey;


    def gettime():
        return (int(time.time() * 1000));


    dropdownx = framex+30;
    dropdowny = framey+50;



    drawrect(screen, (30,30,30), pygame.Rect(framex, framey, framewidth, frameheight))

    frameicon.image.set_alpha(80);

    screenblit(screen,frameicon.image, (framex, framey))

    frameicon.image.set_alpha(255);

    chosentext = arialfont.render(frameicon.name, False, (255,255,255))

    textwidth = 150;

    tw = chosentext.get_size()[0];
    th = chosentext.get_size()[1];

    if(tw > textwidth):
        scale = (textwidth / tw);
        tw *= scale;
        th *= scale;
    chosentext = pygame.transform.scale(chosentext, (tw, th));

    screenblit(screen,chosentext, (dropdownx, framey + 9));

    datasynced = False;

    if(frameicon.type != frameoption):
        datasynced = False;
    elif(frameoption == "Open file"):
        datasynced = str(frameicon.data) == str(framefilelocation);
    elif(frameoption == "Key-Combo"):
        datasynced = str(frameicon.data) == str(framekeycombo);
    elif(frameoption == "Type Sentence"):
        datasynced = str(frameicon.data) == str(framesentence);

    savestages = [0.5,0.5];

    if not datasynced: savestages = [1,1];

    closed = drawbutton(framex + framewidth - 30 - 10, framey + 10, 30, 30, image=closeicon, alphastages = [0.5, 1])
    clicked = drawbutton(framex + framewidth - 60 - 10 - 6, framey + 10, 30, 30, image=dragicon, alphastages = [0.5, 1])
    savemacro = drawbutton(framex + framewidth - 90 - 10 - 6 - 6, framey + 10, 30, 30, image=saveicon, alphastages = savestages)



    if(savemacro):

        print("saving stuff");

        frameicon.type = frameoption;
        frameicon.datalocation = str(getid()) + ".txt";

        if(frameoption == "Open file"):
            frameicon.data = framefilelocation;
        if(frameoption == "Key-Combo"):
            frameicon.data = framekeycombo[:];
        if(frameoption == "Type Sentence"):
            frameicon.data = framesentence;

        print(frameicon.data);





    if(closed):
        toggleon.pop("key-combo1", None)
        framekeycombolast = gettime();
        framedraw = False;
        return;

    if(clicked):
        framedragging = [mousex - framex, mousey - framey];

    if(holding == False):
        framedragging = False;

    if framedragging != False:
        framex = mousex - framedragging[0]
        framey = mousey - framedragging[1]

    if frameoption == "Open file":

        textsurface = pygame.Surface((200, 200));
        textsurface.fill((55,55,55));

        if anyfiledrop != "empty":
            print("opening file");

            framefilelocation = anyfiledrop;
        else:
            if len(framefilelocation) != 0:
                blit_text(textsurface, framefilelocation, (0,0), arialfontsmall)
            else:
                framefilelocation = [];
                blit_text(textsurface, "Drag and drop any file here, and the location will be copied", (0,0), arialfontsmall)
        screenblit(screen,textsurface, (dropdownx, framey+ 100));

    if frameoption == "Type Sentence":

        textsurface = pygame.Surface((200, 200));
        textsurface.fill((50,50,50));




        if textfiledrop != "empty":
            print("opening file");

            with open(textfiledrop) as f:
                framesentence = f.read()
        else:
            if len(framesentence) != 0:
                blit_text(textsurface, framesentence, (0,0), arialfontsmall)
            else:
                framesentence = [];
                blit_text(textsurface, "Drag and drop .txt file into this box, and that file will be copied", (0,0), arialfontsmall)
        screenblit(screen,textsurface, (dropdownx, framey+ 100));





    if frameoption == "Key-Combo":


        recy = framey + 100;
        fontheight = 19;
        textheight = 230;
        thekey = "empty";


        rec = drawtoggle(dropdownx, recy, 30, 30, "key-combo1", image=[recordnothingicon,recordhovericon,recordholdingicon,recordicon], outline=0);
        collision = colliding(dropdownx,recy,30,30,mousex,mousey)

        cleartable = drawbutton(dropdownx, recy + 30, 30, 30, image=garbageicon, alphastages = [0.5, 1], outline=0);
        if cleartable:
            framekeycombo = [];
            framekeycombostart = 1;

        def updateframekeycombo():
            global framekeycombostart;

            if(len(framekeycombo) > int(textheight / fontheight)):
                framekeycombostart = len(framekeycombo) - int(textheight / fontheight) + 1;


        if justclicked and collision != False:
            print("set last");
            framekeycombolast = gettime();

        scroll_y = 0;
        for e in events:
            if e.type == pygame.MOUSEWHEEL:

                framekeycombostart -= e.y;
                if framekeycombostart < 1: framekeycombostart = 1;
                if framekeycombostart > len(framekeycombo): framekeycombostart = len(framekeycombo)

        if framekeycombokeyedit != -1:
            for event in events:
                if(event.type == pygame.KEYDOWN):
                    thekey = keymodifiers[event.key] + " DOWN"
                if(event.type == pygame.KEYUP):
                    thekey = keymodifiers[event.key] + " UP"

        elif rec:

            for event in events:
                currenttime = gettime();
                if(event.type == pygame.KEYDOWN):
                    framekeycombo.append(currenttime - framekeycombolast);
                    framekeycombo.append(keymodifiers[event.key] + " DOWN")
                    framekeycombolast = currenttime;
                    updateframekeycombo();
                if(event.type == pygame.KEYUP):
                    framekeycombo.append(currenttime - framekeycombolast);
                    framekeycombo.append(keymodifiers[event.key] + " UP")
                    framekeycombolast = currenttime;
                    updateframekeycombo();



        textrenders = [];
        framekeycombostring = "";

        level = 0;
        counter = 0;

        combolistx = dropdownx + 60;

        for event in framekeycombo:
            counter+=1;
            if(framekeycombostart > counter): continue;
            if(level * fontheight > textheight): break;

            chosentext = "nada";


            isdots = False
            numberonly = arialfont.render(str(counter)+": ", False, (255,255,255));

            if((level + 1) * fontheight > textheight):
                chosentext = arialfont.render("...", False, (255,255,255))
                isdots = True;
            else:
                if type(event) == int:
                    chosentext = arialfont.render(str(event) + "ms", False, (255,255,255))
                else:
                    chosentext = arialfont.render(event.upper(), False, (255,255,255))

            tw = chosentext.get_size()[0];
            th = chosentext.get_size()[1];
            twn = numberonly.get_size()[0];
            thn = numberonly.get_size()[1];
            scale = (fontheight / th);
            tw *= scale;
            th *= scale;
            twn *= scale;
            thn *= scale;



            chosentext = pygame.transform.scale(chosentext, (tw, th));
            numberonly = pygame.transform.scale(numberonly, (twn, thn));


            if isdots:
                screenblit(screen,chosentext, (combolistx, recy + level * fontheight - fontheight/4))
                continue;
            editbutton = False;

            ylevel = recy + level*fontheight;

            if framekeycombokeydrag != -1 and counter-1 == framekeycombokeydrag[0]:
                ylevel = mousey + framekeycombokeydrag[1];

            screenblit(screen,numberonly, (combolistx, ylevel))

            movebutton = drawbutton(combolistx, ylevel, twn, th, image=dragicon,alphastages=[0.1,1],outline=0)
            editbutton = drawbutton(combolistx + twn, ylevel, tw, th, "y", (120,120,0), 0, False, defaultcolor=(30,30,30))
            deletebutton = drawbutton(combolistx + twn + tw, ylevel, 15, th, image=garbageicon, outline=0, alphastages=[0.1,1])
            clonebutton = drawbutton(combolistx + twn + tw + 15, ylevel, 15, th, image=cloneicon, outline=0, alphastages=[0.1,1])





            if clonebutton:
                framekeycombo.insert(counter-1, framekeycombo[counter-1]);

            if deletebutton:
                framekeycombo.pop(counter-1);
                level+=1;
                continue;

            if movebutton:
                framekeycombokeydrag = [counter-1, recy + level*fontheight - mousey];

            if framekeycombokeydrag != -1 and counter-1 != framekeycombokeydrag[0]:
                mousecolliding = colliding(combolistx, ylevel, 205, th, mousex, mousey);
                if mousecolliding != False:
                    framekeycombo[counter-1], framekeycombo[framekeycombokeydrag[0]] = framekeycombo[framekeycombokeydrag[0]], framekeycombo[counter-1];
                    framekeycombokeydrag[0] = counter-1;



            if(framekeycombowaitindex == counter-1 or framekeycombokeyedit == counter-1):
                editbutton = drawbutton(combolistx + twn, recy + level*fontheight, tw + 5, th, "y", (255,0,0), 0, True)

            if(framekeycombokeyedit == counter-1 and thekey != "empty"):
                framekeycombo[framekeycombokeyedit] = thekey;

            if editbutton and type(event) == int:
                framekeycombowaitdragy = [mousey, event];
                framekeycombowaitindex = counter-1;
            elif editbutton:
                if framekeycombokeyedit == -1:
                    framekeycombokeyedit = counter-1;
                else:
                    framekeycombokeyedit = -1;

            if counter-1 == framekeycombokeyedit and justclicked and not editbutton:
                    framekeycombokeyedit = -1;



            if( holding == False):
                framekeycombowaitdragy = "none";
                framekeycombowaitindex = -1;
                framekeycombokeydrag = -1;

            if framekeycombowaitdragy != "none":
                num = framekeycombo[framekeycombowaitindex];

                dx = ( (framekeycombowaitdragy[0] - mousey) * 0.2 )**3;

                if framekeycombowaitdragy[0] < mousey and dx > 0: dx *= -1;
                dx = int(dx);
                num = framekeycombowaitdragy[1] + dx;



                if num < 1: num = 1;

                framekeycombo[framekeycombowaitindex] = num;


            screenblit(screen,chosentext, (combolistx + twn, ylevel))
            level = level + 1;

        drawrect(screen, (0,0,0), pygame.Rect(combolistx - 10, recy - 3, 270, textheight + fontheight + 10), 2)


    chosentext = arialfont.render(frameoption, False, (255,255,255))
    textheight = 30
    th = chosentext.get_size()[1];
    tw = chosentext.get_size()[0];
    scale = textheight / th;
    tw *= scale;
    th *= scale;

    chosentext = pygame.transform.scale(chosentext, (tw, th));

    dropdown = drawbutton(dropdownx, dropdowny, tw, th, "f", defaultcolor=(50,50,50));
    #dropdown = dropdown or drawbutton(dropdownx-19, dropdowny, 20, th, "f")

    screenblit(screen,chosentext, (dropdownx, dropdowny))

    if dropdown:
        framedropdown = framedropdown == False

    if framedropdown:
        currenty = textheight + dropdowny
        for option in frameoptions:
            if option != frameoption:
                chosentext = arialfont.render(option, False, (255,255,255))
                th = chosentext.get_size()[1];
                tw = chosentext.get_size()[0];
                scale = textheight / th;
                tw *= scale;
                th *= scale;
                chosentext = pygame.transform.scale(chosentext, (tw, th));
                pressed = drawbutton(dropdownx, currenty, tw, th, "f", defaultcolor=(75,75,0));


                screenblit(screen,chosentext, (dropdownx, currenty))
                currenty += textheight;

                if pressed:
                    framedropdown = False;
                    frameoption = option;


def renderfont(text, x, y, height):
    chosentext = arialfont.render(text, False, (255,255,255))

    th = chosentext.get_size()[1];
    tw = chosentext.get_size()[0];
    scale = height / th;
    tw *= scale;
    th *= scale;

    screenblit(screen,chosentext, (x,y) )




def drawbutton(x, y, w, h, image="empty", hovercolor=(255,0,0), outline=2, hover=False, alphastages=[0.5,1], defaultcolor=(255,255,255)):

    global mousex;
    global mousey;
    global nothoveringanything;
    global cursor;

    collision = colliding(x,y,w,h,mousex,mousey)
    col = defaultcolor;
    hoverstage = 0;


    if(collision != False or hover):
        nothoveringanything = False;
        cursor = pygame.SYSTEM_CURSOR_HAND;
        hoverstage = 1;

    if type(image) == str:
        if hoverstage == 1: col = hovercolor;
        drawrect(screen, col, pygame.Rect(x, y, w, h))
    else:
        image.set_alpha(alphastages[hoverstage] * 255)
        image = pygame.transform.scale(image, (w,h))
        screenblit(screen,image, (x,y))

    if(outline > 0): drawrect(screen, (0,0,0), pygame.Rect(x, y, w, h), outline)



    if collision != False and justclicked:
        return True;


toggleon = {};

def drawtoggle(x, y, w, h, id, fullcol=(255,0,0), image="none", alphastages=[0.1,0.1,0.40,1], outline=2):

    global mousex;
    global mousey;
    global nothoveringanything;
    global cursor;

    collision = colliding(x,y,w,h,mousex,mousey)

    col = (255,255,255);

    holdstage = 0;

    if(collision != False):
        nothoveringanything = False;
        holdstage = 1;
        cursor = pygame.SYSTEM_CURSOR_HAND;

    if(collision != False and justreleased):
        if id in toggleon:
            toggleon.pop(id);
        else:
            toggleon[id] = True;

    if(id in toggleon):
        holdstage = 3;

    if(collision != False and holding): holdstage = 2;

    if image=="none":
        r = col[0] + (fullcol[0] - col[0]) * alphastages[holdstage];
        g = col[1] + (fullcol[1] - col[1]) * alphastages[holdstage];
        b = col[2] + (fullcol[2] - col[2]) * alphastages[holdstage];
        col = (r,g,b);

        drawrect(screen, col, pygame.Rect(x, y, w, h))
    else:
        screenblit(screen,pygame.transform.scale(image[holdstage], (w,h)), (x,y));
    if(outline > 0): drawrect(screen, (0,0,0), pygame.Rect(x, y, w, h), outline)

    return id in toggleon;


def colliding(x, y, w, h, x2, y2):



    if (x <= x2 < x + w) and (y <= y2 < y + h):

        return [x2 - x, y2 - y]
    else:
        return False;

def blit_text(surface, text, pos, font, color=pygame.Color('white')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.





keymodifiers = {
    pygame.K_BACKSPACE:"BACKSPACE",
pygame.K_TAB:"TAB",
pygame.K_CLEAR:"CLEAR",
pygame.K_RETURN:"RETURN",
pygame.K_PAUSE:"PAUSE",
pygame.K_ESCAPE:"ESCAPE",
pygame.K_SPACE:"SPACE",
pygame.K_EXCLAIM:"EXCLAIM",
pygame.K_QUOTEDBL:"QUOTEDBL",
pygame.K_HASH:"HASH",
pygame.K_DOLLAR:"DOLLAR",
pygame.K_AMPERSAND:"AMPERSAND",
pygame.K_QUOTE:"QUOTE",
pygame.K_LEFTPAREN:"LEFTPAREN",
pygame.K_RIGHTPAREN:"RIGHTPAREN",
pygame.K_ASTERISK:"ASTERISK",
pygame.K_PLUS:"PLUS",
pygame.K_COMMA:"COMMA",
pygame.K_MINUS:"MINUS",
pygame.K_PERIOD:"PERIOD",
pygame.K_SLASH:"SLASH",
pygame.K_0:"0",
pygame.K_1:"1",
pygame.K_2:"2",
pygame.K_3:"3",
pygame.K_4:"4",
pygame.K_5:"5",
pygame.K_6:"6",
pygame.K_7:"7",
pygame.K_8:"8",
pygame.K_9:"9",
pygame.K_COLON:"COLON",
pygame.K_SEMICOLON:"SEMICOLON",
pygame.K_LESS:"LESS",
pygame.K_EQUALS:"EQUALS",
pygame.K_GREATER:"GREATER",
pygame.K_QUESTION:"QUESTION",
pygame.K_AT:"AT",
pygame.K_LEFTBRACKET:"LEFTBRACKET",
pygame.K_BACKSLASH:"BACKSLASH",
pygame.K_RIGHTBRACKET:"RIGHTBRACKET",
pygame.K_CARET:"CARET",
pygame.K_UNDERSCORE:"UNDERSCORE",
pygame.K_BACKQUOTE:"BACKQUOTE",
pygame.K_a:"a",
pygame.K_b:"b",
pygame.K_c:"c",
pygame.K_d:"d",
pygame.K_e:"e",
pygame.K_f:"f",
pygame.K_g:"g",
pygame.K_h:"h",
pygame.K_i:"i",
pygame.K_j:"j",
pygame.K_k:"k",
pygame.K_l:"l",
pygame.K_m:"m",
pygame.K_n:"n",
pygame.K_o:"o",
pygame.K_p:"p",
pygame.K_q:"q",
pygame.K_r:"r",
pygame.K_s:"s",
pygame.K_t:"t",
pygame.K_u:"u",
pygame.K_v:"v",
pygame.K_w:"w",
pygame.K_x:"x",
pygame.K_y:"y",
pygame.K_z:"z",
pygame.K_DELETE:"DELETE",
pygame.K_KP0:"KP0",
pygame.K_KP1:"KP1",
pygame.K_KP2:"KP2",
pygame.K_KP3:"KP3",
pygame.K_KP4:"KP4",
pygame.K_KP5:"KP5",
pygame.K_KP6:"KP6",
pygame.K_KP7:"KP7",
pygame.K_KP8:"KP8",
pygame.K_KP9:"KP9",
pygame.K_KP_PERIOD:"KP_PERIOD",
pygame.K_KP_DIVIDE:"KP_DIVIDE",
pygame.K_KP_MULTIPLY:"KP_MULTIPLY",
pygame.K_KP_MINUS:"KP_MINUS",
pygame.K_KP_PLUS:"KP_PLUS",
pygame.K_KP_ENTER:"KP_ENTER",
pygame.K_KP_EQUALS:"KP_EQUALS",
pygame.K_UP:"UP",
pygame.K_DOWN:"DOWN",
pygame.K_RIGHT:"RIGHT",
pygame.K_LEFT:"LEFT",
pygame.K_INSERT:"INSERT",
pygame.K_HOME:"HOME",
pygame.K_END:"END",
pygame.K_PAGEUP:"PAGEUP",
pygame.K_PAGEDOWN:"PAGEDOWN",
pygame.K_F1:"F1",
pygame.K_F2:"F2",
pygame.K_F3:"F3",
pygame.K_F4:"F4",
pygame.K_F5:"F5",
pygame.K_F6:"F6",
pygame.K_F7:"F7",
pygame.K_F8:"F8",
pygame.K_F9:"F9",
pygame.K_F10:"F10",
pygame.K_F11:"F11",
pygame.K_F12:"F12",
pygame.K_F13:"F13",
pygame.K_F14:"F14",
pygame.K_F15:"F15",
pygame.K_NUMLOCK:"NUMLOCK",
pygame.K_CAPSLOCK:"CAPSLOCK",
pygame.K_SCROLLOCK:"SCROLLOCK",
pygame.K_RSHIFT:"RSHIFT",
pygame.K_LSHIFT:"LSHIFT",
pygame.K_RCTRL:"RCTRL",
pygame.K_LCTRL:"LCTRL",
pygame.K_RALT:"RALT",
pygame.K_LALT:"LALT",
pygame.K_RMETA:"RMETA",
pygame.K_LMETA:"LMETA",
pygame.K_LSUPER:"LSUPER",
pygame.K_RSUPER:"RSUPER",
pygame.K_MODE:"MODE",
pygame.K_HELP:"HELP",
pygame.K_PRINT:"PRINT",
pygame.K_SYSREQ:"SYSREQ",
pygame.K_BREAK:"BREAK",
pygame.K_MENU:"MENU",
pygame.K_POWER:"POWER",
pygame.K_EURO:"EURO",
pygame.K_AC_BACK:"AC_BACK"
}


update();
