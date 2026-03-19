"""粒子群优化（PSO）算法 - 优化路口通行效率参数"""
import numpy as np
import random
from typing import List, Dict, Tuple, Optional
from crossing_simulation import SimulationEngine, Config


class Particle:
    """粒子类 - 代表一组参数的候选解"""
    def __init__(self, param_ranges: List[Tuple[float, float]]):
        self.param_ranges = param_ranges
        self.position = self._initialize_position()
        self.velocity = self._initialize_velocity()
        self.best_position = np.copy(self.position)
        self.best_fitness = -float('inf')
    
    def _initialize_position(self) -> np.ndarray:
        """初始化粒子位置"""
        position = []
        for min_val, max_val in self.param_ranges:
            position.append(random.uniform(min_val, max_val))
        return np.array(position)
    
    def _initialize_velocity(self) -> np.ndarray:
        """初始化粒子速度"""
        velocity = []
        for min_val, max_val in self.param_ranges:
            range_size = max_val - min_val
            velocity.append(random.uniform(-range_size * 0.1, range_size * 0.1))
        return np.array(velocity)
    
    def update_position(self):
        """更新粒子位置"""
        self.position += self.velocity
        # 确保位置在参数范围内
        for i, (min_val, max_val) in enumerate(self.param_ranges):
            self.position[i] = max(min_val, min(max_val, self.position[i]))


class PSOOptimizer:
    """粒子群优化器"""
    def __init__(self,
                 param_ranges: List[Tuple[float, float]],
                 fitness_function,
                 population_size: int = 30,
                 max_iterations: int = 50,
                 w: float = 0.7,
                 c1: float = 1.5,
                 c2: float = 1.5):
        """
        初始化PSO优化器
        
        Args:
            param_ranges: 参数范围列表，每个元素是(min, max)元组
            fitness_function: 适应度函数
            population_size: 粒子群大小
            max_iterations: 最大迭代次数
            w: 惯性权重
            c1: 认知学习因子
            c2: 社会学习因子
        """
        self.param_ranges = param_ranges
        self.fitness_function = fitness_function
        self.population_size = population_size
        self.max_iterations = max_iterations
        self.w = w
        self.c1 = c1
        self.c2 = c2
        
        self.particles = [Particle(param_ranges) for _ in range(population_size)]
        self.global_best_position = None
        self.global_best_fitness = -float('inf')
    
    def optimize(self) -> Tuple[np.ndarray, float]:
        """运行PSO优化"""
        for iteration in range(self.max_iterations):
            # 评估每个粒子的适应度
            for particle in self.particles:
                fitness = self.fitness_function(particle.position)
                
                # 更新粒子的最佳位置
                if fitness > particle.best_fitness:
                    particle.best_fitness = fitness
                    particle.best_position = np.copy(particle.position)
                
                # 更新全局最佳位置
                if fitness > self.global_best_fitness:
                    self.global_best_fitness = fitness
                    self.global_best_position = np.copy(particle.position)
            
            # 更新每个粒子的速度和位置
            for particle in self.particles:
                r1 = random.random()
                r2 = random.random()
                
                # 计算新速度
                cognitive_component = self.c1 * r1 * (particle.best_position - particle.position)
                social_component = self.c2 * r2 * (self.global_best_position - particle.position)
                particle.velocity = self.w * particle.velocity + cognitive_component + social_component
                
                # 更新位置
                particle.update_position()
            
            # 打印迭代信息
            if (iteration + 1) % 5 == 0:
                print(f"迭代 {iteration + 1}/{self.max_iterations}, 最佳适应度: {self.global_best_fitness:.4f}")
        
        return self.global_best_position, self.global_best_fitness


def evaluate_fitness(params: np.ndarray) -> float:
    """评估适应度函数"""
    # 提取参数
    social_force_a = params[0]
    social_force_b = params[1]
    avoidance_distance_pp = params[2]
    avoidance_distance_pb = params[3]
    avoidance_distance_bb = params[4]
    avoidance_force_multiplier = params[5]
    
    # 更新配置参数
    Config.SOCIAL_FORCE_A = social_force_a
    Config.SOCIAL_FORCE_B = social_force_b
    Config.AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN = avoidance_distance_pp
    Config.AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE = avoidance_distance_pb
    Config.AVOIDANCE_DISTANCE_BICYCLE_BICYCLE = avoidance_distance_bb
    Config.AVOIDANCE_FORCE_MULTIPLIER = avoidance_force_multiplier
    
    # 运行仿真
    engine = SimulationEngine()
    engine.initialize()
    
    # 运行一定时间
    simulation_time = 30.0  # 运行30秒
    while engine.is_running and engine.time < simulation_time:
        engine.step()
    
    # 获取指标
    metrics = engine.get_detailed_metrics()
    
    # 计算适应度
    avg_travel_time = metrics['avg_travel_time'] or 1.0
    collisions = metrics['collisions']
    completed_entities = metrics['completed_entities']
    total_time = metrics['total_time'] or 1.0
    
    # 单位时间通过量
    throughput = completed_entities / total_time
    
    # 综合适应度
    # 1. 平均通行时间（越小越好）
    time_score = 1.0 / avg_travel_time
    
    # 2. 碰撞次数（越小越好）
    collision_score = 1.0 / (collisions + 1)
    
    # 3. 单位时间通过量（越大越好）
    throughput_score = throughput
    
    # 4. 加权综合
    fitness = time_score * 0.4 + collision_score * 0.3 + throughput_score * 0.3
    
    return fitness


def main():
    """主函数"""
    print("=== 粒子群优化（PSO）算法 - 路口通行效率参数优化 ===")
    
    # 定义参数范围
    param_ranges = [
        (1000.0, 10000.0),  # SOCIAL_FORCE_A: 社会力强度
        (0.05, 0.5),        # SOCIAL_FORCE_B: 社会力作用范围
        (0.005, 0.05),      # AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN: 行人-行人避让距离
        (0.02, 0.2),        # AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE: 行人-自行车避让距离
        (0.02, 0.2),        # AVOIDANCE_DISTANCE_BICYCLE_BICYCLE: 自行车-自行车避让距离
        (1.0, 5.0),          # AVOIDANCE_FORCE_MULTIPLIER: 避让力放大系数
    ]
    
    # 创建PSO优化器
    optimizer = PSOOptimizer(
        param_ranges=param_ranges,
        fitness_function=evaluate_fitness,
        population_size=30,
        max_iterations=50,
        w=0.7,
        c1=1.5,
        c2=1.5
    )
    
    # 运行优化
    print("开始优化...")
    best_params, best_fitness = optimizer.optimize()
    
    # 打印结果
    print("\n=== 优化结果 ===")
    print(f"最佳适应度: {best_fitness:.4f}")
    print("最佳参数:")
    print(f"  SOCIAL_FORCE_A: {best_params[0]:.2f}")
    print(f"  SOCIAL_FORCE_B: {best_params[1]:.3f}")
    print(f"  AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN: {best_params[2]:.3f}")
    print(f"  AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE: {best_params[3]:.3f}")
    print(f"  AVOIDANCE_DISTANCE_BICYCLE_BICYCLE: {best_params[4]:.3f}")
    print(f"  AVOIDANCE_FORCE_MULTIPLIER: {best_params[5]:.2f}")
    
    # 保存最佳参数
    with open('best_params.txt', 'w') as f:
        f.write(f"最佳适应度: {best_fitness:.4f}\n")
        f.write("最佳参数:\n")
        f.write(f"SOCIAL_FORCE_A = {best_params[0]:.2f}\n")
        f.write(f"SOCIAL_FORCE_B = {best_params[1]:.3f}\n")
        f.write(f"AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN = {best_params[2]:.3f}\n")
        f.write(f"AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE = {best_params[3]:.3f}\n")
        f.write(f"AVOIDANCE_DISTANCE_BICYCLE_BICYCLE = {best_params[4]:.3f}\n")
        f.write(f"AVOIDANCE_FORCE_MULTIPLIER = {best_params[5]:.2f}\n")
    
    print("\n最佳参数已保存到 best_params.txt 文件")


if __name__ == "__main__":
    main()
