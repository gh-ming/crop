import os
import shutil
def check_path(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
        print(pathname + ' has been created!')

root = r'G:/data/OData/henan/'           #S2A_MSIL2A_20231106T031921_N0509_R118_T49SEA_20231106T070555.SAFE.zip
match_path = r'G:/data/OData/henan/B1/'  #S2A_MSIL2A_20231106T031921_N0509_R118_T49SEU_20231106T070555.SAFE_B2.jp2
out_path = r'G:/data/OData/henan/B1/selected/'
check_path(match_path)
check_path(out_path)
file_list = os.listdir(match_path)
match_list = []
for filename in file_list:
    if 'jp2' in filename:
        match_list.append(filename[:-len(filename.split('_')[-1])-1]+'.zip')
print(len(match_list))
for file in match_list:
    source_path = os.path.join(root,file)
    shutil.copy(source_path, out_path + file)          # 复制文件
    print ("copy %s -> %s"%(source_path,out_path + file))

