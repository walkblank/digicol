import os
import requests
import cv2
import numpy as np
from lxml import etree
import retry

url_prefix = 'https://shuziwenwu-1259446244.cos.ap-beijing.myqcloud.com/relic/'

def readItemId(url):
    page = requests.get(url)
    # print(page.text)
    pageHtml = etree.HTML(page.text)
    idUrl = pageHtml.xpath('//div[@id="picBox"]/ul/li/a/img/@src')
    if idUrl:
        id = idUrl[0].split('//')[1].split('/')[2]
    else:
        id = ''
        print("not found")
    return id


def getImageXY(id)->(int,int,int):
    x = y = x = 0
    for i in range(0, 1000):
        page = requests.get(url_prefix +id+ '/image-bundle/'+str(i)+ '/0_0.jpg')
        if page.status_code == 404:
            print("max w = ", i -1)
            w = i -1
            break
    for i in range(0, 1000):
        page = requests.get(url_prefix +id+ '/image-bundle/'+str(w) + '/'+ str(i) +'_0.jpg')
        # print(page.status_code)
        if page.status_code == 404:
            print("yindex = ", i-1)
            y = i-1
            break
    for i in range(0, 1000):
        page = requests.get(url_prefix +id+ '/image-bundle/'+str(w)+'/0_'+ str(i) + '.jpg')
        # print(page.status_code)
        if(page.status_code == 404):
            print("xindex = ", i-1)
            x = i-1
            break
    return x,y,w

def readSepImage(id, x, y, w):
    for j in range(0, x+1):
        for k in range(0, y + 1):
            page = requests.get(url_prefix +id+ '/image-bundle/'+str(w)+'/'+ str(k) + '_'+ str(j) + '.jpg')
            with open(str(k)+'_'+str(j)+'.jpg', 'wb') as f:
                f.write(page.content)
                f.close()

def readAndMergeImage(id, x, y, w):
    vseg_image = []
    himage = []
    vimage = '' 
    for j in range(0, y+1):
        for k in range(0, x+1):
            page = requests.get(url_prefix +id+ '/image-bundle/'+str(w)+'/'+ str(j) + '_'+ str(k) + '.jpg')
            vseg_image.append(cv2.imdecode(np.asarray(bytearray(page.content), dtype='uint8'), cv2.IMREAD_COLOR))
        vimage = cv2.vconcat(vseg_image)
        himage.append(vimage)
        vseg_image.clear()
    fullImg = cv2.hconcat(himage)
    cv2.imwrite(id+'.jpg', fullImg)


def mergeImage(x, y):
    vseg_image = []
    himage = []
    vimage = ''
    for i in range(0, y+1):
        for j in range(0, x+1):
            vseg_image.append(cv2.imread(str(i)+'_'+str(j)+'.jpg'))
        vimage = cv2.vconcat(vseg_image)
        himage.append(vimage)
        vseg_image.clear() 

    print("himage len", len(himage))
    k = cv2.hconcat(himage)
    cv2.imwrite('full.jpg', k)


def getImage(url):
    id = readItemId(url)
    if id:
        x,y,w = getImageXY(id)
        print('x,y,w:', x,y,w, id)
        if not os.path.exists(id): os.mkdir(id)
        os.chdir(id)
        readAndMergeImage(id, x,y,w)
        os.chdir('..')

getImage('https://digicol.dpm.org.cn/cultural/detail?id=a73efc637f364c11be6a4261ee269ba7')