import os
import shutil

from lxml import etree
import numpy as np
import requests
import cv2
import json
import threading

url_prefix = 'https://shuziwenwu-1259446244.cos.ap-beijing.myqcloud.com/relic/'
queryUrl   = 'https://digicol.dpm.org.cn/cultural/queryList'

sem = threading.Semaphore(10)

# class DownloadManager():
    # pass

class DigiColDownloader(threading.Thread):
    def __init__(self, uuid, name, relicnum):
        threading.Thread.__init__(self)
        self.uuid = uuid
        self.name = name
        self.relicnum = relicnum
        self.tmpPath = 'images/' + self.name + '/tmp-' + self.relicnum.replace('/', '-') + '/'
        self.fileName = 'images/' + self.name + '/' + self.relicnum.replace('/', '-') + '.jpg'
        sem.acquire()

    def run(self):
        if not os.path.isdir(self.tmpPath): 
            os.makedirs(self.tmpPath)
        if not os.path.isfile(self.fileName): 
            self.getItemImage(self.uuid)
        shutil.rmtree(self.tmpPath)
        sem.release()

    @staticmethod
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

    @staticmethod
    def getImageXY(id)->(int,int,int):
        print(id)
        x = y = w = 0
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

    def readSepImage(self, id, x, y, w):
        for j in range(0, x+1):
            for k in range(0, y + 1):
                if not os.path.isfile(self.tmpPath+str(k)+'_'+str(j)+'.jpg'): 
                    page = requests.get(url_prefix +id+ '/image-bundle/'+str(w)+'/'+ str(k) + '_'+ str(j) + '.jpg')
                    # with open('images/'+self.name+'/tmp' + self.relicnum.replace('/','-') + '/'+str(k)+'_'+str(j)+'.jpg', 'wb') as f:
                    with open(self.tmpPath + str(k)+'_'+str(j)+'.jpg', 'wb') as f:
                        f.write(page.content)
                        f.close()

    def mergeImage(self, x, y):
        vseg_image = []
        himage = []
        vimage = ''
        for i in range(0, y+1):
            for j in range(0, x+1):
                # vseg_image.append(cv2.imdecode(np.fromfile('images/'+self.name +'/tmp/'+str(i)+'_'+str(j)+'.jpg', dtype=np.uint8), -1))
                vseg_image.append(cv2.imdecode(np.fromfile(self.tmpPath +str(i)+'_'+str(j)+'.jpg', dtype=np.uint8), -1))
            vimage = cv2.vconcat(vseg_image)
            himage.append(vimage)
            vseg_image.clear() 

        print("himage len", len(himage))
        k = cv2.hconcat(himage)
        cv2.imencode('.jpg', k)[1].tofile(self.fileName)

    def getItemImage(self, uuid):
        self.getImage('https://digicol.dpm.org.cn/cultural/detail?id='+uuid)

    def getImage(self, url):
        id = self.readItemId(url)
        x,y,w = self.getImageXY(id)
        print('x,y,w:', x,y,w, id)
        # if os.curdir
        self.readSepImage(id, x,y,w)
        self.mergeImage(x,y)

def getItemUrls(cateUrl):
    pageCnt = -1 
    curPageIdx = 0
    data = {'page':'1', 'keyWord':'', 'authorizeStatus':'false', 'hasImage':'true', 'cateList':'16'}
    while pageCnt != curPageIdx:
        data['page'] = curPageIdx+1
        respData = requests.post(cateUrl, data)
        # print(respData.text)
        jsonData = json.loads(respData.text)
        pageCnt = jsonData["pagecount"]
        curPageIdx = jsonData["currentPage"]
        for item in jsonData['rows']:
            print(item['name'], item["uuid"], item["culturalRelicNo"])
            dl = DigiColDownloader(item['uuid'], item['name'], item['culturalRelicNo'])
            dl.start()

# getImage('https://digicol.dpm.org.cn/cultural/detail?id=d2f8727ae67e43e8bfc874b58cff5ab9')
getItemUrls(queryUrl)
