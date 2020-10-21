# -*- coding: utf-8 -*-
# created at 2018.2.14

import numpy as np
import os
import sys
import xml.etree.ElementTree as ET
import shutil
from PIL import Image
import skimage
import skimage.io
import time
import cv2
import threading

root_path = '/home/kenny/Projects/keras/steelyard'
xml_a = 'training.xml'
xml_b = 'testing.xml.rmempty.xml'
# img_folder = 'train'
img_folder = 'test'
# new_folder = 'train_small'
new_folder = 'train_II_orgin_size'
class_folder = sys.argv[1]


def extract_img_list(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    pics = []
    for y in root.iter('image'):
        file_ = y.get('file')
        file_ = file_.encode("iso-8859-1").decode('utf8')
        pics.append(file_)
    return pics


def list_img_from_folder(folder):
    pics = []
    for file_ in os.listdir(folder):
        pics.append(file_)
    return pics


def remove_file_path(file_list):
    pic_name_only = []
    for t in file_list:
        pic_name_only.append(t.split('/')[1])
    return pic_name_only


def involve_check(lsmall, lbig):
    count = 0
    for t in lsmall:
        if (t not in lbig):
            count = count + 1
    return count


def gen_img_folder(lsmall, lall, sumImgInOneFolder, folderNum):
    if (sumImgInOneFolder * folderNum > (len(lall) - len(lsmall))):
        print("overflow!!!")
        sys.exit()
    freshImg = []
    # print(len(lall))
    for t in lall:
        if (t not in lsmall):
            freshImg.append(t)
    # print(len(freshImg))
    src_folder = os.path.join(root_path, img_folder)
    for i in range(0, folderNum):
        new_img_folder = os.path.join(root_path, new_folder + '_' + str(i))
        os.mkdir(new_img_folder)
        # for j in range(0,sumImgInOneFolder):
        print("Generating %s folder." % new_img_folder)
        c = 0
        for j in freshImg:
            src_file = os.path.join(src_folder, j)
            des_file = os.path.join(new_img_folder, j)
            shutil.copy(src_file, des_file)
            freshImg.remove(j)
            c = c + 1
            if (c >= sumImgInOneFolder):
                break

    print("Generation img folder done!", len(freshImg))
def mv_img():
    print(" * Move images starts...")
    start = time.clock()
    classfolder = class_folder;
    folder_ = os.path.join(root_path, img_folder)
    folder_ = os.path.join(folder_, classfolder)
    des_folder = os.path.join(root_path,new_folder)
    if not os.path.exists(des_folder):
        os.mkdir(des_folder)
    des_folder = os.path.join(des_folder,classfolder)
    if not os.path.exists(des_folder):
        os.mkdir(des_folder)
    imgs = list_img_from_folder(folder_)
    c = 0
    for i in imgs:
        fname = classfolder + '-'+str(c)+'.jpg'
        src_img = os.path.join(folder_,i)
        des_img = os.path.join(des_folder,fname)
        shutil.copy(src_img,des_img)
        c = c+1
    end = time.clock()
    print(" * Copying Done! Time consume: ",end-start)
def check_img():
    print(" * Checking JPG format starts...")
    start = time.clock()
    folder = os.path.join(root_path,new_folder,class_folder)
    for file_ in os.listdir(folder):
        file_ = os.path.join(folder, file_)
        try:
            im = skimage.io.imread(file_)
        except:
            print("False Image found and deleted: ",file_)
            os.remove(file_)
    end = time.clock()
    print(" * JPG check done! Time consume: ",end-start)
def resize_img():
    print(" * Resize images starts...")
    start = time.clock()
    classfolder = class_folder;
    folder_ = os.path.join(root_path, new_folder,classfolder)
    for file_ in os.listdir(folder_):
        f = os.path.join(folder_,file_)
        im = Image.open(f)
        out = im.resize((224, 224), Image.ANTIALIAS)
        (fname,ext) = os.path.splitext(f)
        out.save(fname+'.png',"PNG")
        os.remove(f)
    end = time.clock()
    print(" * Resizing Done! Time consume: ",end-start)
def resize_img_to_path(path_,width,height):
    im = Image.open(path_)
    out = im.resize((width, height), Image.ANTIALIAS)
    out.save(path_, "JPEG")

def resize_img_cv2(width,height):
    print(" * Resize images with cv2 starts...")
    start = time.clock()
    classfolder = class_folder;
    folder_ = os.path.join(root_path, new_folder, classfolder)
    for file_ in os.listdir(folder_):
        f = os.path.join(folder_, file_)
        im = cv2.imread(f)
        pic = cv2.resize(im, (width, height), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite(f, pic,[int(cv2.IMWRITE_JPEG_QUALITY), 10])
    end = time.clock()
    print(" * Resizing Done! Time consume: ", end - start)
def resize_img_scaled(min_length):
    print(" * Resize images, shortest length is min_length, starts...")
    start = time.clock()
    classfolder = class_folder;
    folder_ = os.path.join(root_path, new_folder, classfolder)
    for file_ in os.listdir(folder_):
        f = os.path.join(folder_, file_)
        im = Image.open(f)
        (w, h) = im.size
        if w>h:
            x = (w*min_length)/h
            out = im.resize((x,min_length),Image.ANTIALIAS)
        if w<h:
            x = (h*min_length)/w
            out = im.resize((min_length,x),Image.ANTIALIAS)
        out.save(out, "JPEG")
    end = time.clock()
    print(" * Resizing Done! Time consume: ", end - start)

intro = '''This program will generate folderNum folders and each folder\n
will contain sumImgInOneFolder images. Images collected from only_vehicle_folder\n
and if one image is used in folder 1, then it will not be used in folder 2.\n
To run the programm you simply type: python h.py\n
However, because the problems various, you need to modify beginning of this\n
python code to adjust your solution.
'''
class check_img_t(threading.Thread):
    def __init__(self,root_,f_):
        threading.Thread.__init__(self)
        self.filename = f_
        self.f_root = root_
    def run(self):
        tmp_path = os.path.join(self.f_root,self.filename)
        print(" * Working on ",tmp_path)
        files = os.listdir(tmp_path)
        for ff in files:
            img = os.path.join(tmp_path,ff)
            try:
                # pass
                #im = skimage.io.imread(img)
                resize_img_to_path(img,299,299)
            except:
                # pass
                print("Can not resize: ", img)
        print("* Done ...",tmp_path)

def resize_img_rec():
    print(" * Using Theads to resize images recusivlly starts...")
    start = time.clock()

    print(" * all work will be done at root_folder")
    print(" * that means you should make a copy of source first")
    print(" * and save the folder name to root_folder")
    root_folder = '/home/kenny/Projects/keras/steelyard/train_III_299'
    folders = os.listdir(root_folder)
    for f in folders:
        check_img_t(root_folder,f).start()

    end = time.clock()
    print(" * Resizing Done! Time consume: ",end-start)



#mv_img()
#resize_img_rec()
#resize_img()
#
if "__main__" == __name__:
    ThreadList = []
    lock = threading.Lock()
    root_folder = '/home/kenny/Projects/keras/steelyard/train_IV_299'
    folders = os.listdir(root_folder)
    for f in folders:
        t = check_img_t(root_folder,f)
        ThreadList.append(t)
    start = time.clock()
    for t in ThreadList:
        t.start()
    for t in ThreadList:
        t.join()
    end = time.clock()
    print(" * Resizing Done! Time consume(Threading): ", end - start)

