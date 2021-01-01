import requests, json,re, time,urllib
from bs4 import BeautifulSoup as bs
import os, sys

import pandas as pd
pd.set_option('display.max_columns', None)


#多线程
from multiprocessing import Pool
'''
#链接谷歌云盘
from google.colab import files
from google.colab import drive
drive.mount('/content/drive',force_remount=True)
'''


header = {
        "Content-Type": "application/json",
        "Charset": "UTF-8",
        'cache-control':"no-cache"
}

def download_file(url,file_name,file_dir):
    u = urllib.request.urlopen(url)
    f = open(file_dir + '/' +file_name, 'wb')
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break
        f.write(buffer)
    f.close()
    print ("Sucessful to download" + " " + file_name)

def get_ali_fileurl(id = 1001006541914027,type = "solution"):
    if type == "solution":
        # 内容页的接口访问，已注释掉的是
        # SLurl = "https://linkmarket.aliyun.com/api/solution/getSolutionList"
        # SLdata = {"supplierInfoId":2216,"start":0,"num":99}
        # info = requests.get(SLurl, data = SLdata)
        # SLcon = json.loads(info.text)["data"][0]["overview"]  
        url = "https://linkmarket.aliyun.com/api/solution/getSolution"
        data = {"solutionId":id,"getDetail":True}
        

    elif type == "hardware":
        url = "https://linkmarket.aliyun.com/api/hardware/getHardware"
        data = {"hardwareId":id,"getDetail":True}
        
    info = requests.get(url, data = data)   
    con = json.loads(info.text)
    #print (con)
    if con['code'] == 200 :
        b = con["data"]["data"]["overview"]
        return json.loads(b)
    else:

        print (id)
        return None

url ="https://linkmarket.aliyun.com/api/search/searchByConditions"
pageNo = 1
solutions = []
while pageNo < 2:
    data = {"targetTypes":["solution","hardware"],"pageNo":pageNo,"pageSize":100}  #pageSize<1000
    info = requests.get(url, data = data)
    a = json.loads(info.text)
    print ("pageNo=",pageNo)
    if a["data"]["data"] != []:
        solutions = solutions + a["data"]["data"]
        pageNo+=1
    else:
        break
df = pd.DataFrame(solutions)

# 附加pdf的url到df
df['pdfUrl']  = ""
for index, row in df.iterrows():
    try:
        b = get_ali_fileurl(row.targetId,row.targetType)
        if b:
            try:
                row.pdfUrl = "https:" + b["pdfUrl"]
                print (index,row.targetId,row.title)
            except: continue
    except: continue
    if index >1000000:
        break

df.to_csv('./solution_ali.csv', sep=",")


#加载谷歌驱动器中csv文件为df
df = pd.read_csv('./solution_ali.csv', sep=',')
print (df.head(10))



#遍历产品列表
def get_f(row, s = "ali"):
# for index,i in df.iterrows():
    index,i = row[0], row[1]
    print(i["title"])
    file_dir = "./solution_ali/"+s+"/" + str(i["title"]).replace("/","-")
    if not os.path.isdir(file_dir):
        try:
            os.mkdir(file_dir)
        except:
            return
    #遍历文件中的产品列表
    file_url = i["pdfUrl"]
    file_name = i["title"]
    print(index,file_url)
    try:
        print (index,file_url)
        download_file(file_url,file_name,file_dir)
        time.sleep(1)
    except:
        print ("file url error")
        time.sleep(10)
        return
    return index



pool = Pool(2)
pool.map(get_f, df.head(10).iterrows())
