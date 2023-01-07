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


# root, out_path = process_arguments(sys.argv)
root = r'D:\桌面\科研项目\农业项目\data_anhui\多余\2021_3'
out_path = r'D:\桌面\科研项目\农业项目\data_anhui\多余\2021_3\jp2'
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
for zipname in zip_list:
    print("{} is processing".format(zipname))
    print("There are {} zips left".format(zip_id))
    name, extension = os.path.splitext(zipname)
    prefix_list = zipname.split("_")
    filepath = os.path.join(root, zipname)
    try:
        if os.path.exists(filepath):
            zf = zipfile.ZipFile(filepath, 'r')
            for zipped in zf.namelist():
                if 'R60m' in zipped:
                    zf.extract(zipped, out_path)
    except BaseException:
        print("{} is a bad zip file \n".format(zipname))
        zip_id = zip_id - 1
        continue
    mid_folder = os.listdir(os.path.join(out_path, "{}.SAFE/GRANULE".format(name)))[0]
    image = os.path.join(out_path,
                         "{}.SAFE/GRANULE/{}/IMG_DATA/R60m/{}_{}_B{}_{}0m.jp2".format(name, mid_folder,
                                                                                      prefix_list[5],
                                                                                      prefix_list[2],
                                                                                      '01',
                                                                                      6))
    out_image = os.path.join(out_path, '{}_B1.jp2'.format(name))
    shutil.move(image, out_image)
    extracted_path = os.path.join(out_path, "{}.SAFE".format(name))
    shutil.rmtree(extracted_path)
    zip_id = zip_id - 1
