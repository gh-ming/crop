############################################################################
# 需求：
# 下载2023年全国区域的L2A影像
# 方法：
# 尝试使用Odata api进行条件筛选，再进行下载。
# 存在的问题
# 1.token只有十分钟，refresh后也只有60min，需要设置一个定期获取token的函数，嵌套到数据下载的代码部分  >>每景影像重新获取token；最大sessions为100，一次获取token算一次session.
# 2.下载使用wget容易多次请求，不稳定（弹出HTTP request sent, awaiting response... 429 Too Many Requests）；使用request目前存在断开连接的问题（requests.exceptions.ChunkedEncodingError: ("Connection broken: ConnectionResetError(10054, '远程主机强迫关闭了一个现有的连接。', None, 10054, None)"）   >>貌似被修复，官方让我重新试一下，确实没报错了
# 3.筛选：  >>目前还未完成
# 1）影像的完整性，如何得到影像的完整度？
# 通过经纬度坐标计算面积与矩形面积比较（经纬度坐标可通过GeoFootprint的json数据得到）
# 2）如何对同一地区的影像进行筛选（缺失部分相互弥补）？
# 获取不同影像的经纬度坐标，进行矢量融合再判断。
############################################################################
#使用修改基础设置即可
############################################################################
import os
import sys
import pandas as pd
import requests
import json
import subprocess
import datetime
from tqdm import tqdm

def check_path(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
        print(pathname + ' has been created!')
#基础设置
############################################################################
# 1 起始日期(包含起始)
startDate='2024-04-10'
endDate  ='2024-04-23'

# 2 所需卫星数据
satellite='SENTINEL-2'

# 3 检索时文件名需包括的字符串  对于哨兵2 可以用来筛选区块或者产品等级
contains_str='L2A'

# 4 检索区域 可在该网站绘制geojson文件 https://geojson.io/#map=5.12/34.13/122.8
roi_geojson='G:/data/OData/map.geojson'

# 5 数据保存路径
output_dir='G:/data/OData/henan_20240410_20240423/'
check_path(output_dir)

# 6 新版哥白尼数据中心账号密码 即这个网站的账号密码 https://dataspace.copernicus.eu/
email="ghming048@gmail.com"
password="Fighti1205&@"

# 7 属性设置
cloudCoverPercentage = "20.00"

########################################################################
# 从geojson文件中读取坐标，以字符串'x y,...,x y'组织。
with open(roi_geojson, 'r') as f:
    data = f.read()
geojson_data = json.loads(data)
coordinates=geojson_data['features'][0]['geometry']['coordinates'][0]
coordinates_str=''
for i in range(len(coordinates)):
    coordinates_str=coordinates_str+str(coordinates[i][0])+' '+str(coordinates[i][1])+', '
coordinates_str=coordinates_str[:-2]

# 生成检索链接
#基础前缀
base_prefix="https://catalogue.dataspace.copernicus.eu/odata/v1/Products?$filter="
#检索条件 记得检索条件之间要加 and 
str_in_name="contains(Name,'"+contains_str+"')"
collection="Collection/Name eq '"+satellite+"'"
roi="OData.CSC.Intersects(area=geography'SRID=4326;POLYGON(("+coordinates_str+"))') "
time_range="ContentDate/Start ge "+startDate+"T00:00:00.000Z and ContentDate/Start le "+endDate+"T00:00:00.000Z"

#检索属性
search_lim="&$top=1000"
expand_assets="&$expand=Assets"
cloudCover = "Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value le "+cloudCoverPercentage+")"

##OrderBy(默认升序)
#OrderBy ="&$orderby=ContentDate/Start desc"

#最终的检索链接 
#判断卫星产品类型
if satellite=='SENTINEL-1':
    request_url=base_prefix+str_in_name+" and "+collection+" and "+roi+" and "+time_range+search_lim+expand_assets
else:
    request_url=base_prefix+str_in_name+" and "+collection+" and "+roi+" and "+cloudCover+" and "+time_range+search_lim+expand_assets

# print("检索条件：{}".format(request_url))
#开始检索

JSON = requests.get(request_url).json()
df = pd.DataFrame.from_dict(JSON['value'])
if len(df)==0:
    print('未查询到数据')
    sys.exit()

try:  
    if len(df)>999:
        raise Exception("检索数量超出1000，请重新设置检索条件")  
    print("查询数据条数：{}".format(len(df)))
except Exception as e:  
    print("Program stopped:", e)


#原始数据id列表
data_id_list=df.Id
data_name_list=df.Name
# 快视图下载链接 
# quickview_url=[file[0]['DownloadLink'] for file in df.Assets]
# quickview_url_txt = open(output_dir+"quickview_url.txt", "w")
# for id in range(len(df.Name)):
#     quickview_url_txt.write(df.Name[id]+" "+quickview_url[id]+"\n")
# quickview_url_txt.close()

# 获取Access token
def get_access_token(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
        }
    try:
        r = requests.post("https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data=data,
        )
        r.raise_for_status()
    except Exception as e:
        raise Exception(
            f"Access token creation failed. Reponse from the server was: {r.json()}"
            )
    return r.json()["access_token"]

# 中断下载后继续下载 
# 存储未下载文件id的列表  
downloaded_false = []  
# 检查文件是否已下载的函数  
def is_file_downloaded(file_id):  
    file_name = f"{output_dir}{file_id}.txt"  
    return os.path.exists(file_name)  
  
wget_str=[]
part1='''wget --header "Authorization: Bearer '''
part2='''" "http://catalogue.dataspace.copernicus.eu/odata/v1/Products('''
part3=''')/$value" -O '''
for i in tqdm(range(len(data_id_list))):
    file_id = data_name_list[i]
    file_name = f"{output_dir}{file_id}.txt"
    if not is_file_downloaded(file_id):
        access_token = get_access_token(email, password)
        command=part1+access_token+part2+data_id_list[i]+part3+output_dir+data_name_list[i]+'.zip'
        # print(command)
        wget_str.append(command)
        try:
            print('[',datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S'),'] '+'开始下载: '+data_name_list[i])
            # subprocess.run(command, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            subprocess.run(command, shell=True, check=True)
            with open(file_name, "w") as file:  
                file.write('file downloaded successfully.')
            print('[',datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S'),'] '+'下载成功: '+data_name_list[i])
        except:
            print('[',datetime.datetime.strftime(datetime.datetime.now(),'%H:%M:%S'),'] '+'下载失败: '+data_name_list[i])
            downloaded_false.append(file_id)

if downloaded_false:
    print("Files that have not been downloaded：\n")    
    print(downloaded_false)
    file_false = f"{output_dir}downloadfalse.txt"
    with open(file_false,"w") as f:
        f.truncate(0)
        f.write("Files that have not been downloaded：\n")
        f.write(downloaded_false)   
else:   
    print("All files downloaded successfully.")


#方法二：
# Access token有效期仅为十分钟 可以在每次下载数据前都申请一个新的Access token
# access_token = get_access_token(email, password)
# print(access_token)

# for i in tqdm(range(len(data_id_list))):
#     local_dir = output_dir+data_name_list[i]+'.zip'
#     url = f"https://zipper.dataspace.copernicus.eu/odata/v1/Products({data_id_list[i]})/$value"
#     headers = {"Authorization": f"Bearer {access_token}"}
#     session = requests.Session()
#     session.headers.update(headers)
#     response = session.get(url, headers=headers, stream=True)  
#     #chunk_size 是每次迭代读取的字节数  
#     chunk_size = 8192    
#     with open(local_dir, "wb") as file:  
#         for chunk in tqdm(response.iter_content(chunk_size=chunk_size)):  
#             if chunk:  
#                 file.write(chunk)




# "HTTP request sent, awaiting response... 429 Too Many Requests"
# --wait 10 --random-wait --continue