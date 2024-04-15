'''
利用粒子群算法求函数极值
'''
import numpy as np
import matplotlib.pyplot as plt

# Input: bottom,up,n
#   bottom: the bottom of Particle Swarm
#   up:the up of Particle Swarm
#   n:number of Particle Swarm
# Output: X

def ParticleSwarm_generate(bottom,up,n):
    if n ==1:
        X= np.random.rand()
    else:
        X = np.random.uniform(bottom,up,[1,n])
    V = np.zeros((1,n))
    return X,V


def Fitness_Function(x):
    f = x**3-5*x**2-2*x+3
    return f
def Fitness_Function_reverse(x):
    f = -(x**3-5*x**2-2*x+3)
    return f

def PSO_algorithm(step_max,n):
    p_best = np.zeros(n)
    g_best = 0
    X_totol = []
    Position_ago = 0
    Fitness_totol = []
    X,V = ParticleSwarm_generate(bottom,up,n)
    step = 0
    while step < step_max:
        Fitness = Fitness_Function(X)
        Fitness_totol.append(Fitness)
        r1 = np.random.rand()
        r2 = np.random.rand()
        V = V+ 3 * r1 *(p_best-X)+2*r2*(g_best*np.ones((1,n))-X)
        X = X + V
        X = -2+7/(np.max(X)-np.min(X))*(X-np.min(X))
        if step == 0:
            X_totol = X
        else:
            X_totol = np.column_stack((X_totol, X))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
        g_best = X[0,np.argmax(Fitness)]

        # 保存每个粒子最大值的位置X
        p_best_value = np.max(Fitness_totol,axis=0)
        for i in range(n):
            p_best_pos = []
            pos = np.where(Fitness_totol==p_best_value[0][i])
            if len(pos)>1:
                p_best_pos.append(pos[1][0])
                p_best_pos.append(pos[2][0])
            else:
                p_best_pos.append(pos[1])
                p_best_pos.append(pos[2])
            p_best[i] = X_totol[p_best_pos[0],p_best_pos[1]]

        #终止条件（全局最优不变）
        if np.abs(Position_ago - g_best) > 0.001:
            Position_ago = g_best
            count = 0
            step = step + 1
        else:
            count = count + 1         
        if count >= 5:
            break

    return g_best

if __name__ == "__main__":
    bottom = -2
    up = 5
    #粒子数
    n = 50
    #迭代次数
    step_max = 50
    # scipy 实现
    from scipy.optimize import fmin_bfgs
    from sklearn.metrics import mean_squared_error
    x = np.linspace(-2, 5, 1000)
    y = x**3-5*x**2-2*x+3
    y_max = fmin_bfgs(Fitness_Function_reverse,0)
    print(y_max)
    g_best_totol = []
    # for num in range(n):
    #     g_best = PSO_algorithm(step_max,num+2)
    #     g_best_totol.append(g_best)    
    # y_max = np.ones(n)*y_max
    # Mse = (y_max-g_best_totol)**2/np.sum((y_max-g_best_totol)**2)
    # n_Particle_Swarm = np.linspace(2, n+2, n)
    # plt.xlabel('number of Particle Swarm')
    # plt.ylabel('Mse')
    # plt.plot(n_Particle_Swarm,Mse,'r', lw=2, label='MSE loss')
    # plt.legend()
    # plt.show()

    for step in range(step_max):
        g_best = PSO_algorithm(step+1,n)
        g_best_totol.append(g_best)
    y_max = np.ones(step_max)*y_max
    Mse = (y_max-g_best_totol)**2/np.sum((y_max-g_best_totol)**2)
    step_num = np.linspace(2, step_max+2, step_max)
    plt.xlabel('number of step')
    plt.ylabel('Mse')
    plt.plot(step_num,Mse,'r', lw=2, label='MSE loss')
    plt.legend()
    plt.show()        
    # 可视化
    # plt.plot(x, y, ls="-", lw=2, label="Function figure")
    # plt.legend()
    # plt.show()



