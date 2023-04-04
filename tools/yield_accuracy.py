import yimage
import shapefile
import numpy as np
from tqdm import tqdm, trange
'''
实现对样本点中sjcl属性和对应预测的影像像素值进行计算R方
'''
def load_shp(filepath):
    '''
    读取shp的几何数据和属性数据
    '''
    polygon_bbox_list = []
    polygon_coordinate_list = []
    # 所需要的属性数据
    sjcl_list = []
    sf = shapefile.Reader(filepath)
    for i in range(len(sf.shapes())):
        #访问shp中的几何数据
        s = sf.shape(i)
        # polygon_bbox_list.append(s.bbox)
        polygon_coordinate_list.append(s.points)
        # 访问shp中的属性数据
        r = sf.record(i)
        sjcl_list.append(r[0])
    return polygon_coordinate_list,sjcl_list

def get_pixel_by_coordinate(point_coord,image_path):
    '''
    :param coordinates:
    :param image_path:
    :return: 点对应的像素行列位置/像元值
    image_geo_info['coord']
    0 左上像素左上角的x坐标。
    1 w-e像素分辨率/像素宽度。
    2 行旋转（通常为零）。
    3 左上像素左上角的y坐标。
    4 列旋转（通常为零）。
    5 n-s像素分辨率/像素高度
    '''
    HWC,image_geo_info = yimage.io.read_image(image_path,with_geo_info = True,only_image_info = True)
    #像元位置
    px = int((point_coord[0][0]-image_geo_info['coord'][0])/image_geo_info['coord'][1])
    py = int((point_coord[0][1]-image_geo_info['coord'][3])/image_geo_info['coord'][5])
    #像元值
    pixel = yimage.io.read_image(image_path,read_range=(px,py,1,1))[0,0]

    return pixel

def R_squared(y_pred,y_true):
    y_mean = np.mean(y_true)
    var1 = 0
    var2 = 0
    for i in trange(len(y_pred),desc="R方计算"):
        diff1 = y_pred[i] - y_true[i]
        diff2 = y_true[i] - y_mean
        var1 += diff1**2
        var2 += diff2**2
    r_squared = 1 - var1/var2
    return r_squared


if __name__ == '__main__':
    shp_path = r'G:\农业项目\农业估产\实际产量\corn_84.shp'
    img_path = r'G:\农业项目\农业估产\henan_SJCL_corn.tif'
    coordinate,sjcl = load_shp(shp_path)
    point_pixel_list = []
    for i in trange(len(coordinate),desc="坐标反算计算"):
        point = coordinate[i]
        point_pixel = get_pixel_by_coordinate(point, img_path)
        flag = np.isnan(point_pixel)
        if flag == True:
            continue
        point_pixel_list.append(point_pixel)
    r_squared = R_squared(point_pixel_list,sjcl)
    print(r_squared)






