import os
import glob
from osgeo import gdal
from math import ceil
from tqdm import tqdm
# os.environ['PROJ_LIB'] = '/home/mahui/miniconda3/envs/tensorflow/share/proj'

def GetExtent(infile):
    ds = gdal.Open(infile)
    geotrans = ds.GetGeoTransform()
    xsize = ds.RasterXSize
    ysize = ds.RasterYSize
    min_x, max_y = geotrans[0], geotrans[3]
    max_x, min_y = geotrans[0] + xsize * geotrans[1], geotrans[3] + ysize * geotrans[5]
    ds = None
    return min_x, max_y, max_x, min_y


def RasterMosaic(file_list, outpath):
    Open = gdal.Open
    min_x, max_y, max_x, min_y = GetExtent(file_list[0])
    for infile in file_list:
        minx, maxy, maxx, miny = GetExtent(infile)
        min_x, min_y = min(min_x, minx), min(min_y, miny)
        max_x, max_y = max(max_x, maxx), max(max_y, maxy)

    in_ds = Open(file_list[0])
    in_band = in_ds.GetRasterBand(1)

    geotrans = list(in_ds.GetGeoTransform())
    width, height = geotrans[1], geotrans[5]
    columns = ceil((max_x - min_x) / width)  # 列数
    rows = ceil((max_y - min_y) / (-height))  # 行数

    driver = gdal.GetDriverByName('GTiff')
    out_ds = driver.Create(outpath, columns, rows, 1, in_band.DataType, options=["TILED=YES", "COMPRESS=LZW", "BIGTIFF=YES"])
    out_ds.SetProjection(in_ds.GetProjection())
    geotrans[0] = min_x  # 更正左上角坐标
    geotrans[3] = max_y
    out_ds.SetGeoTransform(geotrans)
    inv_geotrans = gdal.InvGeoTransform(geotrans)
    for in_fn in tqdm(file_list):
        in_ds = Open(in_fn)
        in_gt = in_ds.GetGeoTransform()
        offset = gdal.ApplyGeoTransform(inv_geotrans, in_gt[0], in_gt[3])
        x, y = map(int, offset)

        data = in_ds.GetRasterBand(1).ReadAsArray()
        out_ds.GetRasterBand(1).WriteArray(data, x, y)  # x，y是开始写入时左上角像元行列号
    del in_ds, out_ds


if __name__ == '__main__':

    name = 2
    path = '/mnt/e/sanbei/worldcover_cropland2021/sanbei_worldcover_cropland2021'
    '''
    image_pre = path + '/image_pre'
    num = len(os.listdir(image_pre))
    for i in range(1, num + 1, 1):
        image_path = path+"/result"+str(i)   #待拼接图片路径
        result_path = path+"/mosaic"  #拼接结果路径
        if not os.path.exists(result_path):
            os.mkdir(result_path)
        imageList = glob.glob(image_path + "/*.tif")
        result = os.path.join(result_path, "result"+str(i)+".tif")
        RasterMosaic(imageList, result)
    '''
    image_path = r'D:\桌面\科研项目\农业项目\2024河南冬小麦分类\第二版结果'   # 待拼接图片路径23+99
    result_path =r'D:\桌面\科研项目\农业项目\2024河南冬小麦分类\第二版结果'  # 拼接结果路径
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    imageList = glob.glob(image_path + "/*.tif")
    result = os.path.join(result_path, "mosaic_v3.tif")
    RasterMosaic(imageList, result)
    dst_ds = gdal.Open(result)     
    dst_ds.BuildOverviews('nearest',[2,4,8,16,32,64,128]) 
