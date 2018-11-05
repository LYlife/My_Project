import requests  # requests库
import re        # 正则表达式库
import os        # 文件模块
import time
import threading
from bs4 import BeautifulSoup  # BeautifulSoup 库


# import GModel
basic_url = 'http://www.gmgmba.in/guomoba/guomosipai/'
first_url = 'http://www.gmgmba.in/guomoba/guomosipai/index.html'
singlepage_url = ''
file_path = 'F:\pic'
Log_path = 'F:\pic\Log'
SLog_path = 'F:\pic\Log\漏存日志.txt'
RLog_path = 'F:\pic\Log\未解析日志.txt'
threads = []
threadLock = threading.Lock()

class GMThread(threading.Thread):
    def __init__(self, func, url, path, result, sf, rf):
        threading.Thread.__init__(self)
        self.func = func
        self.url = url
        self.path = path
        self.result = result
        self.sf = sf
        self.rf = rf
    def run(self):
        threadLock.acquire()
        self.func(self.url, self.path, self.result, self.sf, self.rf)
        threadLock.release()


class GModel(object):
     def __int__(self,  name, cover, route, url):
        self.name = name
        self.cover = cover
        self.route = url + route[18:]
        self.url = url

# 获取网址页面代码
def getSoup(url):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
    r = requests.get(url, headers=header)
    r.encoding = 'gb2312'
    soup = BeautifulSoup(r.text, 'lxml')
    return soup

# 获取图片链接的图片
def getPic(url):
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'}
    r = requests.get(url, headers=header)
    return r

# 获取网页所有图集页数
def getPageNum(url):
    soup = getSoup(url)
    sop_pagenum = soup.find_all('a')
    pagenum = int(sop_pagenum[-2].text)
    return pagenum

#获得当前图集页数
def getpicNum(url):
    soup = getSoup(url)
    all_div = soup.find('div', class_='pages')
    picnum = 0
    if all_div is None:
        all_div = soup.find_all('div', class_=re.compile("^[A-Za-z0-9]{8}$"))
        a_pagenum = all_div[-1].find_all('a')
        try:
            picnum = int(a_pagenum[-2].text)
        except:
            a_pagenum = all_div[-2].find_all('a')
            picnum = int(a_pagenum[-2].text)
            return picnum
    else:
        a_pagenum = all_div.find_all('a')
        picnum = int(a_pagenum[-2].text)

    # picnum = int(a_pagenum[-2].text)
    return picnum

# 获取单页图片
def getSinglePtr(url, path, result, sf, rf):
    soup = getSoup(url)
    result = result * 2
    all_img = []
    try:
        all_imgs = soup.find_all('div',class_=re.compile("^[A-Za-z]{8}$"))
        if len(all_imgs)> 0:
            for div in all_imgs:
                all_img = div.find_all('img')
                if len(all_img) > 1:
                    break
                else:
                    continue
        # all_img = soup.find('div',class_=re.compile("^[A-Za-z]{8}$")).find_all('img')
    except:
        # 匹配失败，写入未解析日志
        rf.write(url + '\r\n')
        return


    if all_img is None:
        return
    else:
        for img in all_img:
            try:
                temppath = path + "\\" + img['alt'].strip() + "\\" + str(result - 1) + ".jpg"
                print("获取图片地址: " + img['src'])
                print("存入路径:" + temppath)
                if not os.path.exists(temppath):
                    saveImg(img['src'], temppath)
                    print('存储'+ img['alt'] + str(result - 1))
                    result = result + 1
                else:
                    continue
            except:
                # 存储图片失败，写入漏存日志
                sf.write(img['alt'] + '|' + img['src'] + '|' + path + "\\" + img['alt'] + "\\" + str(result - 1) + ".jpg" + '\r\n')
                result = result + 1
                continue
        return

# 获取当前页面图集信息列表
def getAtlasList(url, AtlasList):
    soup = getSoup(url)
    all_atlas = soup.find('ul', class_='ulphoto').find_all('a')
    for atla in all_atlas:
        gm = GModel()  # 实例化Model
        gm.Name = atla['title']
        gm.Covert = atla['href'][20:]
        gm.Route = (atla.find('img'))['src']
        gm.Url = url
        AtlasList.append(gm)


def searchFolder(path, foldername):
    bl = False;
    for dirs in os.walk(path):
        if not dirs == foldername:
            bl = True
        else:
            bl = False

    return bl



def createFolder(path):
    path = path.strip()   # 去掉首位空格
    path = path.rstrip("\\")   # 去掉尾部\符号
    isExists = os.path.exists(path)  # 判断是否存在此文件夹

    if not isExists:
        os.makedirs(path)
        return True
    else:
        return False


def saveImg(url, path):
    img = getPic(url)
    time.sleep(0.5)
    f = open(path, 'ab')
    f.write(img.content)
    f.close()


#格式化字符串
def formatstr(strs, isfirstpage, pagnum):
    strs = strs.strip()
    strs = strs.rstrip("\\")

    if '_' in strs:
       strs = strs.split('_:')[-1] + '.html'

    if not isfirstpage:
       strs = strs.rstrip(".html") + '_' + str(pagnum)
       strs = strs + '.html'
    return strs




try:
    AtlasNum = getPageNum(first_url)   # 获取所有图集页数
except:
    print("主页网址访问错误")
    os._exit(0)


AtlasNo = 1
AtlasList = list()
dirs = list()
sf = open(SLog_path, 'a+')
rf = open(RLog_path, 'a+')
filename_list = os.listdir(file_path)
for i in range(len(filename_list)):
    dirs.append(filename_list[i])


while AtlasNo <= AtlasNum:
    if AtlasNo == 1:
        getAtlasList(first_url, AtlasList)
    else:
        getAtlasList(first_url.rstrip("index.html") + str(AtlasNo) + ".html", AtlasList)

    AtlasNo = AtlasNo + 1
    print("获取第" + str(AtlasNo) + "图集完成")


print("获取图集资料完毕，获取个数:" + str(len(AtlasList)))
# for Atlas in AtlasList:
#     createFolder(file_path + '\\' + Atlas.Name)
# print ('生成当前页图集文件夹完毕')

for Atlas in AtlasList:
    foldercount = dirs.count(Atlas.Name.strip())
    if foldercount == 0:
        createFolder(file_path + '\\' + Atlas.Name)
        singlepage_url = basic_url + formatstr(Atlas.Covert, True, 0)
        picnum = getpicNum(singlepage_url)
        result = 0
        while result < picnum:
            if result == 0:
                g = GMThread(getSinglePtr, singlepage_url, file_path, result + 1, sf, rf)
                # getSinglePtr(singlepage_url, file_path, result + 1)
            else:
                g = GMThread(getSinglePtr, formatstr(singlepage_url, False, result + 1), file_path, result + 1, sf, rf)
                # getSinglePtr(formatstr(singlepage_url, False, result + 1), file_path, result + 1)

            g.start()
            g.join()
            result = result + 1

    else:
        continue


