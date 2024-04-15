'''
利用粒子群算法求函数极值
'''
import numpy as np
import matplotlib.pyplot as plt
import numpy.random as random
import time


#定义一个求解类以及初始化方法
class PSO:
    def __init__(self,D, N, M, p_low, p_up, v_low, v_high, w = 1., c1 = 2., c2 = 2.) :
        self.w = w  # 惯性权值
        self.c1 = c1  # 个体学习因子
        self.c2 = c2  # 群体学习因子
        self.D = D  # 粒子维度
        self.N = N  # 粒子群规模，初始化种群个数
        self.M = M  # 最大迭代次数
        self.p_range = [p_low, p_up]  # 粒子位置的约束范围          如果没有约束，会导致位置“爆炸”或消失，速度也是
        self.v_range = [v_low, v_high]  # 粒子速度的约束范围
        self.x = np.zeros((self.N, self.D))  # 所有粒子的位置
        self.v = np.zeros((self.N, self.D))  # 所有粒子的速度
        self.p_best = np.zeros((self.N, self.D))  # 每个粒子的最优位置
        self.g_best = np.zeros((1, self.D))[0]  # 种群（全局）的最优位置
        self.p_bestFit = np.zeros(self.N)  # 每个粒子的最优适应值
        self.g_bestFit = float('Inf')  # float('-Inf')，始化种群（全局）的最优适应值，由于求极小值，故初始值给大，向下收敛，这里默认优化问题中只有一个全局最优解

        # 初始化所有个体和全局信息
        for i in range(self.N):
            for j in range(self.D):
                self.x[i][j] = random.uniform(self.p_range[0][j], self.p_range[1][j])
                self.v[i][j] = random.uniform(self.v_range[0], self.v_range[1])
            self.p_best[i] = self.x[i]  # 保存个体历史最优位置，初始默认第0代为最优
            fit = self.fitness(self.p_best[i])
            self.p_bestFit[i] = fit  # 保存个体历史最优适应值
            if fit < self.g_bestFit:  # 寻找并保存全局最优位置和适应值
                self.g_best = self.p_best[i]
                self.g_bestFit = fit

    def fitness(self,x):
        """
        根据粒子位置计算适应值，可根据问题情况自定义
        """
        return x[0] * np.exp(x[1]) + x[2] * np.sin(x[1]) + x[3] * x[4]

    def update(self):
        for i in range(self.N):
            # 更新速度(核心公式)
            self.v[i] = self.w * self.v[i] + self.c1 * random.uniform(0, 1) * (self.p_best[i] - self.x[i]) + self.c2 * random.uniform(0, 1) * (self.g_best - self.x[i])

            # 对比我之前实现的max-min归一化，这样对于超限的值设置为边界值更合理。
            # 速度限制
            for j in range(self.D):
                if self.v[i][j] < self.v_range[0]:
                    self.v[i][j] = self.v_range[0]
                if self.v[i][j] > self.v_range[1]:
                    self.v[i][j] = self.v_range[1]
            # 更新位置
            self.x[i] = self.x[i] + self.v[i]
            # 位置限制
            for j in range(self.D):
                if self.x[i][j] < self.p_range[0][j]:
                    self.x[i][j] = self.p_range[0][j]
                if self.x[i][j] > self.p_range[1][j]:
                    self.x[i][j] = self.p_range[1][j]
            # 更新个体和全局历史最优位置及适应值
            ## 对于个体历史最优，无需将粒子所有的值保存后求最值，迭代求解即可
            _fit = self.fitness(self.x[i])
            if _fit < self.p_bestFit[i]:
                self.p_best[i] = self.x[i]
                self.p_bestFit[i] = _fit
            if _fit < self.g_bestFit:
                self.g_best = self.x[i]
                self.g_bestFit = _fit

    def pso(self, draw = 1):
        best_fit = []  # 记录每轮迭代的最佳适应度，用于绘图
        w_range = None
        #使用惯性权重线性衰减迭代
        if isinstance(self.w, tuple):
            w_range = self.w[1] - self.w[0]
            self.w = self.w[1]
        time_start = time.time()  # 记录迭代寻优开始时间
        for i in range(self.M):
            self.update()  # 更新主要参数和信息
            if w_range:
                self.w -= w_range / self.M  # 惯性权重线性递减
            print("\rIter: {:d}/{:d} fitness: {:.4f} ".format(i, self.M, self.g_bestFit, end = '\n'))
            best_fit.append(self.g_bestFit.copy())
        time_end = time.time()  # 记录迭代寻优结束时间
        print(f'Algorithm takes {time_end - time_start} seconds')  # 打印算法总运行时间，单位为秒/s
        if draw:
            plt.figure()
            plt.plot([i for i in range(self.M)], best_fit)
            plt.xlabel("iter")
            plt.ylabel("fitness")
            plt.title("Iter process")
            plt.show()

if __name__ == '__main__':
    low = [1, 1, 1, 1, 1]
    up = [25, 25, 25, 25, 25]
    pso = PSO(5, 100, 50, low, up, -1, 1, w = (0.6,0.9))
    pso.pso()



