import os,sys
from osgeo import gdal
from tqdm import tqdm
import yimage
import zipfile

_debug_flag = False

def _debug(*param):
    if not _debug_flag:
        return
    _param = [str(item) for item in param]
    param_str = ' # '.join(_param)
    print('##### DEBUG ##### {} #####'.format(param_str))

def check_file(filename):
    if os.path.isfile(filename):
        os.remove(filename)
        print(filename + ' has been removed!')
    else:
        print(filename + ' will be created!')


def check_path(pathname):
    if not os.path.exists(pathname):
        os.makedirs(pathname)
        print(pathname + ' has been created!')

def generate_baselist(file_path, suffix):
    suffix_length = len(suffix)
    basename_list = []
    listfile = os.listdir(file_path)
    listfile.sort()
    for basename in listfile:
        if basename[(-suffix_length):] != suffix:
            continue
        basename_list.append(basename[:(-suffix_length)])

    return basename_list

def generate_folderlist(file_path):
    basename_list = []
    listfile = os.listdir(file_path)
    listfile.sort()
    for basename in listfile:
        if '.' in basename:
            continue
        basename = file_path + '/' + basename
        basename_list.append(basename)
    return basename_list

def generate_list(file_path, basename_list, suffix):
    filename_list = []
    for basename in basename_list:
        filename = file_path + '/' + basename + suffix
        filename_list.append(filename)

    return filename_list

def generate_list_by_filelist(filelist):
    filename_list = []
    listfile = open(filelist)
    for line in listfile.readlines():
        filename_list.append(line.rstrip('\n'))
    
    return filename_list


def mosaic(file_list, out_path):
    proj = gdal.Open(file_list[0], gdal.GA_ReadOnly).GetProjection()
    options = gdal.WarpOptions(srcSRS=proj, dstSRS=proj, format='GTiff', resampleAlg=gdal.GRIORA_Bilinear,multithread = True,warpOptions = ['NUM_THREADS=ALL_CPUS'], srcNodata=0)
    gdal.Warp(out_path, file_list, options=options)

def mosaic_float(file_list, out_path):
    proj = gdal.Open(file_list[0], gdal.GA_ReadOnly).GetProjection()
    options = gdal.WarpOptions(srcSRS=proj, dstSRS=proj, format='GTiff', resampleAlg=gdal.GRIORA_Bilinear,multithread = True,warpOptions = ['NUM_THREADS=ALL_CPUS'], srcNodata=0, outputType=gdal.GDT_Float32)
    gdal.Warp(out_path, file_list, options=options)

def run():
    folder_path, out_path= process_arguments(sys.argv)
    file_list = os.listdir(folder_path)
    # zip_list = []
    # for filename in file_list:
    #     filepath = os.path.join(folder_path,filename)
    #     # if not zipfile.is_zipfile(filepath):
    #     #     continue
    #     zip_list.append(filename)
    # name_list = []
    # for zipname in tqdm(zip_list):
    #     name,extension = os.path.splitext(zipname)
    #     os.makedirs(os.path.join(folder_path,name),exist_ok=True)
    #     prefix_list = zipname.split("_")
    #     filepath = os.path.join(folder_path,zipname)
    #     if os.path.exists(os.path.join(out_path,"{}_processing.txt".format(name))):
    #         continue
    #     try:
    #         with open(os.path.join(out_path,"{}_processing.txt".format(name)), 'w') as f:
    #             f.write('processing')
    #             f.close()
    #         if os.path.exists(filepath):
    #             zf = zipfile.ZipFile(filepath,'r')
    #             for zipped in zf.namelist():
    #                 zf.extract(zipped,os.path.join(folder_path,name))
    #         name_list.append(name)
    #     except BaseException:
    #         print("{} is a bad zip file /n".format(zipname))
    #         continue
    # print('all zipped files have benn extracted')
    folder_list = generate_folderlist(folder_path)
    for folder in tqdm(folder_list):
        if folder.split('/')[-1] not in name_list:
            continue
        basename_list = generate_baselist(folder, '.tif')
        file_list = generate_list(folder, basename_list, '.tif')
        out_name = out_path + '/' + basename_list[0][:-2]+'.tif'
        temp = gdal.Open(file_list[0])
        band = temp.GetRasterBand(1)
        data_type = band.DataType
        # print(data_type)
        # import ipdb;ipdb.set_trace()
        del temp
        if data_type == gdal.GDT_UInt16 or data_type == gdal.GDT_Byte or data_type == gdal.GDT_Int16 or data_type == gdal.GDT_UInt32 or data_type == gdal.GDT_Int32:
            mosaic(file_list, out_name)
            img, geo = yimage.io.read_image(out_name, with_geo_info=True)
            color_table = [(255,255,255),(255,0,0),(0,0,255),(0,255,0)]
            yimage.io.write_image(out_name, img, geo_info=geo, color_table=color_table, compress='LZW')
            dst_ds = gdal.Open(out_name)     
            dst_ds.BuildOverviews('nearest',[2,4,8,16,32,64,128])  

            del dst_ds
        else:
            mosaic_float(file_list, out_name)
            img, geo = yimage.io.read_image(out_name, with_geo_info=True)
            img[img>1] = 1
            img[img<0] = 0
            yimage.io.write_image(out_name, img, geo_info=geo, compress='LZW' , dtype='float16')
            dst_ds = gdal.Open(out_name)     
            dst_ds.BuildOverviews('nearest',[2,4,8,16,32,64,128])  

            del dst_ds

 



def process_arguments(argv):
    # if len(argv) < 3:
    #     help()
    # src_path=argv[0]
    # dst_path=argv[1]
    src_path=r'D:\桌面\科研项目\农业项目\2024河南冬小麦分类\第二版结果'
    dst_path=r'D:\桌面\科研项目\农业项目\2024河南冬小麦分类\第二版结果'
    return src_path, dst_path

def help():
    print('Usage: python mosaic.py src_path dst_path')
    exit()

if __name__ == '__main__':
    run()
