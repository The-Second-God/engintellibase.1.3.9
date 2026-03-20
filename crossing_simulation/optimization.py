"""
优化模块 - 实现PSO算法自动优化系统参数
"""
import numpy as np
from typing import Dict, List, Any
from .simulation import SimulationEngine
from .config import Config


def load_best_params():
    """
    加载之前的最优参数
    """
    try:
        with open('best_params.txt', 'r') as f:
            params = {}
            for line in f:
                key, value = line.strip().split(': ')
                params[key] = float(value)
            return params
    except:
        return None


class PSOOptimizer:
    """
    粒子群优化器
    """
    def __init__(self, param_ranges, population_size=30, max_iterations=50):
        """
        初始化粒子群优化器
        
        Args:
            param_ranges: 参数范围字典
            population_size: 粒子数量
            max_iterations: 最大迭代次数
        """
        self.param_ranges = param_ranges
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.params = list(param_ranges.keys())
        self.dimensions = len(self.params)
        
        # 初始化粒子群
        self.positions = np.zeros((population_size, self.dimensions))
        self.velocities = np.zeros((population_size, self.dimensions))
        self.pbest_positions = np.zeros((population_size, self.dimensions))
        self.pbest_fitness = np.zeros(population_size)
        self.gbest_position = np.zeros(self.dimensions)
        self.gbest_fitness = -np.inf
        
        # 初始化参数
        for i in range(population_size):
            for j, param in enumerate(self.params):
                min_val, max_val = param_ranges[param]
                self.positions[i, j] = np.random.uniform(min_val, max_val)
                self.velocities[i, j] = np.random.uniform(-(max_val - min_val), max_val - min_val)
            self.pbest_positions[i] = self.positions[i].copy()
            self.pbest_fitness[i] = self.evaluate_fitness(self.positions[i])
            
            if self.pbest_fitness[i] > self.gbest_fitness:
                self.gbest_fitness = self.pbest_fitness[i]
                self.gbest_position = self.positions[i].copy()
        
        # 尝试加载之前的最优参数
        loaded_params = load_best_params()
        if loaded_params:
            # 检查加载的参数是否在当前参数空间中
            valid = True
            for param in self.params:
                if param not in loaded_params:
                    valid = False
                    break
            
            if valid:
                # 将加载的参数转换为数组
                loaded_pos = np.array([loaded_params[param] for param in self.params])
                # 设置第一个粒子为加载的参数
                self.positions[0] = loaded_pos
                # 评估适应度
                fitness = self.evaluate_fitness(loaded_pos)
                self.pbest_fitness[0] = fitness
                self.pbest_positions[0] = loaded_pos.copy()
                # 更新gbest
                if fitness > self.gbest_fitness:
                    self.gbest_fitness = fitness
                    self.gbest_position = loaded_pos.copy()
                print(f"Loaded best params from file, fitness: {fitness:.4f}")
    
    def evaluate_fitness(self, params):
        """
        评估参数组合的适应度
        
        Args:
            params: 参数数组
            
        Returns:
            适应度值
        """
        # 将参数数组转换为字典
        param_dict = {self.params[j]: params[j] for j in range(self.dimensions)}
        
        # 更新配置
        Config.update(**param_dict)
        
        # 运行仿真
        engine = SimulationEngine()
        engine.initialize()
        
        # 运行固定时间
        while engine.time < 30.0 and engine.is_running:
            engine.step()
        
        # 返回适应度
        return engine.get_fitness()
    
    def optimize(self):
        """
        执行PSO优化过程
        
        Returns:
            最优参数字典
        """
        w = 0.7  # 惯性权重
        c1 = 1.5  # 认知因子
        c2 = 1.5  # 社会因子
        
        # 记录优化过程
        fitness_history = []
        best_params_history = []
        
        # 记录每个粒子的初始数据和最终反馈结果
        particles_data = []
        
        for iteration in range(self.max_iterations):
            # 记录当前迭代的粒子数据
            iteration_particles = []
            
            for i in range(self.population_size):
                # 记录初始位置
                initial_position = self.positions[i].copy()
                
                # 更新速度
                r1 = np.random.random(self.dimensions)
                r2 = np.random.random(self.dimensions)
                self.velocities[i] = (w * self.velocities[i] +
                                     c1 * r1 * (self.pbest_positions[i] - self.positions[i]) +
                                     c2 * r2 * (self.gbest_position - self.positions[i]))
                
                # 更新位置
                self.positions[i] += self.velocities[i]
                
                # 边界处理
                for j, param in enumerate(self.params):
                    min_val, max_val = self.param_ranges[param]
                    self.positions[i, j] = np.clip(self.positions[i, j], min_val, max_val)
                
                # 评估适应度
                fitness = self.evaluate_fitness(self.positions[i])
                
                # 更新pbest
                if fitness > self.pbest_fitness[i]:
                    self.pbest_fitness[i] = fitness
                    self.pbest_positions[i] = self.positions[i].copy()
                
                # 更新gbest
                if fitness > self.gbest_fitness:
                    self.gbest_fitness = fitness
                    self.gbest_position = self.positions[i].copy()
                
                # 记录粒子数据
                particle_data = {
                    'iteration': iteration + 1,
                    'particle_id': i + 1,
                    'initial_position': initial_position.copy(),
                    'final_position': self.positions[i].copy(),
                    'fitness': fitness
                }
                iteration_particles.append(particle_data)
            
            # 记录当前迭代的所有粒子数据
            particles_data.extend(iteration_particles)
            
            # 记录历史
            fitness_history.append(self.gbest_fitness)
            best_params = {self.params[j]: self.gbest_position[j] for j in range(self.dimensions)}
            best_params_history.append(best_params)
            
            # 打印进度
            print(f"Iteration {iteration+1}/{self.max_iterations}, Best Fitness: {self.gbest_fitness:.4f}")
            print(f"Best Params: {best_params}")
        
        # 保存最优参数
        best_params = {self.params[j]: self.gbest_position[j] for j in range(self.dimensions)}
        with open('best_params.txt', 'w') as f:
            for key, value in best_params.items():
                f.write(f"{key}: {value}\n")
        
        # 保存优化过程
        with open('optimization_results.txt', 'w') as f:
            f.write("Iteration,Fitness,Params\n")
            for i, (fitness, params) in enumerate(zip(fitness_history, best_params_history)):
                f.write(f"{i+1},{fitness},{params}\n")
        
        # 保存每个粒子的初始数据和最终反馈结果
        with open('particles_data.txt', 'w') as f:
            f.write("Iteration,ParticleID,InitialPosition,FinalPosition,Fitness\n")
            for data in particles_data:
                initial_pos = ",".join([f"{x:.4f}" for x in data['initial_position']])
                final_pos = ",".join([f"{x:.4f}" for x in data['final_position']])
                f.write(f"{data['iteration']},{data['particle_id']},{initial_pos},{final_pos},{data['fitness']:.4f}\n")
        
        # 保存每一次迭代的最佳参数和适应度
        with open('iteration_best_results.txt', 'w') as f:
            f.write("Iteration,BestFitness,BestParams\n")
            for i, (fitness, params) in enumerate(zip(fitness_history, best_params_history)):
                f.write(f"{i+1},{fitness},{params}\n")
        
        # 生成适应度演化图表
        try:
            import matplotlib.pyplot as plt
            plt.figure(figsize=(10, 6))
            plt.plot(range(1, self.max_iterations + 1), fitness_history)
            plt.title('Fitness Evolution')
            plt.xlabel('Iteration')
            plt.ylabel('Fitness')
            plt.grid(True)
            plt.savefig('fitness_evolution.png')
            plt.close()
        except:
            print("Matplotlib not available, skipping fitness evolution plot")
        
        return best_params