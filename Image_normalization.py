import yimage
import os
import numpy as np
data_dir = r"D:\桌面\科研项目\农业项目\henan_各种指数\TVDI\henan_TVDI_2022_06_\henan_TVDI_2022_06_0.tif"
image = yimage.io.read_image(data_dir,driver='GDAL')
print(image)
image = np.where(image>1,1,image)
max = np.max(image[:,0])
min = np.min(image[:,0])
print(image)
print(max)
print(min)
# file_path = r"D:\桌面\科研项目\农业项目\henan_各种指数\test\henan_TVDI_2022_06_-20230209T105939Z-001"
# listfile = []
# index = []
# for filepath,dirnames,filenames in os.walk(file_path):
#     for filename in filenames:
#         if len(filename) == 24:
#             # filename.insert(-6,'0')
#             # 字符串转列表
#             str_list = list(filename)
#             # 插入0保证字符串长度一致，便于调取sort函数
#             str_list.insert(-5,'0')
#             filename = ''.join(str_list)
#         listfile.append(filename)
# print(listfile)
# listfile.sort()
# print(listfile)


