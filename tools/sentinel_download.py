from datetime import date

from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import pandas as pd

api = SentinelAPI('xp10-101', '123456aatxy', 'https://scihub.copernicus.eu/dhus')

# search by polygon, time, and SciHub query keywords
footprint = geojson_to_wkt(read_geojson('jalol.geojson'))
products = api.query(footprint,
                     date=(date(2022, 8, 1), date(2022, 8, 30)),  # 1.10
                     producttype='S2MSI2A',
                     platformname='Sentinel-2',
                     cloudcoverpercentage=(0, 20))
api.to_dataframe(products).to_csv('data.csv')
# data = pd.read_csv('yingzhou_20220701_20220731_cloud_10_S2A.csv')
# name_list = []
# with open('sentinel.txt') as f:
#     for line in f:
#         name_list.append(line.rstrip('\n'))
#
# name_list_2 = []
# for i in range(len(data['title'])):
#     name = str(data['title'][i]).split('_')[5]
#     name_list_2.append(name)
# num = 0
# for names in name_list:
#     if names not in name_list_2:
#         num = num + 1
# print(len(name_list_2))
# print((len(name_list) - num) / len(name_list))

# import shapefile
# import re
#
# def load_shapefile(filename):
#     type_list = []
#     label_list = []
#     polygon_bbox_list = []
#     polygon_lonlat_list = []
#     sf = shapefile.Reader(filename)
#     for i in range(len(sf.shapes())):
#         s = sf.shape(i)
#         polygon_bbox_list.append(s.bbox)
#         polygon_lonlat_list.append(s.points)
#         # r = sf.record(i)
#         # label_list.append(r[1])
#         # if r[1] not in type_list:
#         #     type_list.append(r[1])
#     for i in range(len(label_list)):
#         label_list[i] = type_list.index(label_list[i]) + 1
#     return polygon_lonlat_list
#
#
# shpfile = '../New_Shapefile(2).shp'
#
# polygon = load_shapefile(shpfile)
# for i in range(len(polygon)):
#     # print(polygon[i])
#     # tt = str(polygon[i]).replace('(','[').replace(')',']')
#     tt = polygon[i]
#     for j in range(len(tt)):
#         result = str(tt[j]).replace('(','[').replace(')',']')
#         print(result + ',')
#     if i // 30 == 0:
#         print(tt)
#         print('\n')
