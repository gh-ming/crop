import os
'''
输入欧空局购物车生成的meta文件所在的绝对路径；输出其中包含的url值。
'''
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
#重命名为txt文件,并生成url.txt文件
def rename_txt(path):
    for file in os.listdir(path):
        file_path = os.path.join(path,file)
        file_path_header = file_path.split('.')[0]
        file_path_new = file_path_header+".txt"
        os.rename(file_path,file_path_new)
        f = open(file_path_new,'r')
        string = f.readline()
        index1 = find_all(string,'<url>')
        index2 = find_all(string,'</url>')
        result = []
        for i in range(len(index1)):
            tempdata = string[index1[i]+5:index2[i]]
            result.append(tempdata)
        f.close()
        #写入url数据
        url_name = "url.txt"
        url_path = os.path.join(path,url_name)
        file_url = open(url_path,'w')
        for i in result:
            file_url.write(str(i)+'\n')  #\n为换行符
        file_url.close()








if __name__ == '__main__':
    path = r"D:\桌面\科研项目\毕业设计\new_data4"
    rename_txt(path)