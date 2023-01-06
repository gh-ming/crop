import sys
from io import BytesIO
import os
import zipfile
import shutil


def check_path(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
        print(pathname + ' has been created!')


def process_arguments(argv):
    root = argv[1]
    out_path = argv[2]

    return root, out_path

#字符串搜索，并返回全部字串位置的下表，string是输入字符串，sub是子串
def find_all(string, sub):
    start = 0
    pos = []
    while True:
        start = string.find(sub, start)
        if start == -1:
            return pos
        pos.append(start)
        start += len(sub)

root, out_path = process_arguments(sys.argv)
# root = r'D:\桌面\科研项目\农业项目\data_anhui\成果\2020_3_21_anhui'
# out_path = r'D:\桌面\科研项目\农业项目\data_anhui\成果\2020_3_21_anhui\xml'
check_path(out_path)
if os.path.isfile(root):
    file_list = []
    file_list.append(root.split('/')[-1])
    root = root[:-len(root.split('/')[-1])]
else:
    file_list = os.listdir(root)
zip_list = []
for filename in file_list:
    name, extension = os.path.splitext(filename)
    prefix_list = filename.split("_")
    filepath = os.path.join(root, filename)
    if not zipfile.is_zipfile(filepath):
        continue
    if "zipB2" in filename:
        continue
    if not "MSIL2A" in filename:
        continue
    zip_list.append(filename)
print('find {} zips'.format(len(zip_list)))
zip_id = len(zip_list)
zip_name_sum = []
for zipname in zip_list:
    print("{} is processing".format(zipname))
    print("There are {} zips left".format(zip_id))
    zip_name_sum.append(zipname)
    name, extension = os.path.splitext(zipname)
    prefix_list = zipname.split("_")
    filepath = os.path.join(root, zipname)
    try:
        if os.path.exists(filepath):
            zf = zipfile.ZipFile(filepath, 'r')
            for zipped in zf.namelist():
                if 'MTD_MSIL2A' in zipped:
                    zf.extract(zipped, out_path)
    except BaseException:
        print("{} is a bad zip file \n".format(zipname))
        zip_id = zip_id - 1
        continue
    # mid_folder = os.listdir(os.path.join(out_path, "{}.SAFE/GRANULE".format(name)))[0]
    image = os.path.join(out_path,
                         "{}.SAFE/MTD_MSIL2A.xml".format(name))
    out_image = os.path.join(out_path, '{}_MTD_MSIL2A.xml'.format(name))
    shutil.move(image, out_image)
    extracted_path = os.path.join(out_path, "{}.SAFE".format(name))
    shutil.rmtree(extracted_path)
    zip_id = zip_id - 1

#重命名为txt文件,并生成table.txt文件
result = []
for file in os.listdir(out_path):
    file_path = os.path.join(out_path,file)
    file_path_header = file_path.split('.')[0]
    file_path_new = file_path_header+".txt"
    os.rename(file_path,file_path_new)
    f = open(file_path_new,'r')
    xml_list = f.readlines()
    # 使用列表推导式把列表中的单个元素全部转化为str类型
    xml_list_str = [str(i) for i in xml_list]
    # 把列表中的元素放在空串中，元素间用空格隔开
    string = " ".join(xml_list_str)
    index1 = find_all(string,'<Cloud_Coverage_Assessment>')
    index2 = find_all(string,'</Cloud_Coverage_Assessment>')
    time = file.split("_")[2][0:8]
    year = time[0:4]
    file_name = file[:60]+".zip"
    other = (year,time,file_name)
    result.extend(other)
    for i in range(len(index1)):
        tempdata = string[index1[i]+27:index2[i]]
        result.append(tempdata)
    f.close()
#写入数据
url_name = "table.txt"
url_path = os.path.join(out_path,url_name)
file_url = open(url_path,'w')
count = 0
for i in result:
    count = count+1
    if count%4==0:
        file_url.write(str(i)+'\n')
    else:
        file_url.write(str(i) + ' ')
file_url.close()

#生成xlsx文件，得到表格形式数据
import xlwt #需要的模块
f = open(url_path,encoding = "UTF-8")
xls=xlwt.Workbook()
#生成excel的方法，声明excel
sheet = xls.add_sheet('sheet1',cell_overwrite_ok=True)
x = 0
while True:
    #按行循环，读取文本文件
    line = f.readline()
    if not line:
        break  #如果没有内容，则退出循环
    for i in range(len(line.split(' '))):
        item=line.split(' ')[i]
        sheet.write(x,i,item) #x单元格经度，i 单元格纬度
    x += 1 #excel另起一行
f.close()
xlsname = "table.xls"
xlspath = os.path.join(out_path,xlsname)
xls.save(xlspath) #保存xls文件
print("所有文件已生成完毕！")

        
