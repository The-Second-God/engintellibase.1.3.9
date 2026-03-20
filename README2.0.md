# 十字路口行人通行仿真系统 - PSO参数优化方案

## 1. 系统概述

本项目是一个基于社会力模型的十字路口行人通行仿真系统，用于模拟行人和自行车在十字路口的行为和交互。系统通过空间分区和向量化计算优化了性能，现在引入PSO（粒子群优化）算法来自动优化系统参数。

## 2. PSO算法原理

### 2.1 基本概念

粒子群优化（Particle Swarm Optimization, PSO）是一种基于群体智能的优化算法，灵感来源于鸟群觅食行为。其核心思想是通过群体中个体之间的信息共享和协作来寻找最优解。

### 2.2 数学模型

- **速度更新公式**：
  ```
  v_i(t+1) = w·v_i(t) + c1·r1·(pbest_i - x_i(t)) + c2·r2·(gbest - x_i(t))
  ```
  - `w`：惯性权重，控制粒子保持原有运动趋势的能力
  - `c1, c2`：学习因子，分别控制粒子向自身最优和全局最优学习的能力
  - `r1, r2`：随机数，增加搜索的随机性
  - `pbest_i`：粒子i的历史最优位置
  - `gbest`：群体的全局最优位置

- **位置更新公式**：
  ```
  x_i(t+1) = x_i(t) + v_i(t+1)
  ```

### 2.3 工作流程

1. **初始化**：随机生成初始粒子群（参数组合）
2. **评估适应度**：计算每个粒子的适应度值
3. **更新pbest和gbest**：记录每个粒子的历史最优和群体全局最优
4. **更新速度和位置**：根据公式调整粒子的速度和位置
5. **终止条件**：达到最大迭代次数或适应度不再显著改善

## 3. PSO优化方案

### 3.1 优化目标

- 最大化通行效率（减少平均通行时间）
- 最小化碰撞次数
- 平衡行人和自行车的通行体验

### 3.2 优化参数

| 参数名称 | 描述 | 范围 |
|---------|------|------|
| DESIRED_FORCE_FACTOR | 目标吸引力因子 | [0.5, 2.0] |
| SOCIAL_FORCE_A | 社交力强度 | [1000.0, 5000.0] |
| SOCIAL_FORCE_B | 社交力作用范围 | [0.1, 0.3] |
| VISION_RANGE | 视野范围 | [2.0, 6.0] |
| PEDESTRIAN_SPAWN_PROBABILITY | 行人生成概率 | [0.1, 0.5] |
| BICYCLE_SPAWN_PROBABILITY | 自行车生成概率 | [0.05, 0.2] |

### 3.3 适应度函数

使用系统现有的`get_fitness()`方法作为适应度函数：

```python
def get_fitness(self) -> float:
    completed = [e for e in self.entity_manager.all_entities if not e.is_active]
    
    if not completed:
        return 0.0
    
    avg_time = sum(e.travel_time for e in completed) / len(completed)
    
    collision_penalty = self.collision_count * 10.0
    
    efficiency = 1.0 / (avg_time + 0.1)
    
    fitness = efficiency - collision_penalty * 0.01
    
    return max(0, fitness)
```

### 3.4 实现方案

#### 3.4.1 代码结构

```
crossing_simulation/
├── __init__.py
├── config.py
├── entity.py
├── environment.py
├── simulation.py
├── social_force.py
├── visualization.py
└── optimization.py  # 新增：PSO优化模块
```

#### 3.4.2 PSO优化器实现

```python
# crossing_simulation/optimization.py
import numpy as np
from .simulation import SimulationEngine
from .config import Config

class PSOOptimizer:
    def __init__(self, param_ranges, population_size=50, max_iterations=100):
        self.param_ranges = param_ranges  # 参数范围字典
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
    
    def evaluate_fitness(self, params):
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
        w = 0.7  # 惯性权重
        c1 = 1.5  # 认知因子
        c2 = 1.5  # 社会因子
        
        for iteration in range(self.max_iterations):
            for i in range(self.population_size):
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
            
            print(f"Iteration {iteration+1}/{self.max_iterations}, Best Fitness: {self.gbest_fitness:.4f}")
        
        # 返回最优参数
        return {self.params[j]: self.gbest_position[j] for j in range(self.dimensions)}
```

#### 3.4.3 优化运行脚本

```python
# run_optimization.py
from crossing_simulation.optimization import PSOOptimizer
from crossing_simulation.config import Config

# 定义参数范围
param_ranges = {
    'DESIRED_FORCE_FACTOR': (0.5, 2.0),
    'SOCIAL_FORCE_A': (1000.0, 5000.0),
    'SOCIAL_FORCE_B': (0.1, 0.3),
    'VISION_RANGE': (2.0, 6.0),
    'PEDESTRIAN_SPAWN_PROBABILITY': (0.1, 0.5),
    'BICYCLE_SPAWN_PROBABILITY': (0.05, 0.2)
}

# 运行PSO优化
optimizer = PSOOptimizer(param_ranges, population_size=30, max_iterations=50)
best_params = optimizer.optimize()

# 应用最优参数
Config.update(**best_params)
print("最优参数:", best_params)

# 保存最优参数
with open('best_params.txt', 'w') as f:
    for key, value in best_params.items():
        f.write(f"{key}: {value}\n")
```

## 4. 系统集成

### 4.1 与现有系统的交互

1. **参数更新**：PSO优化器通过修改`Config`类的静态属性来调整参数
2. **适应度评估**：每次评估粒子适应度时，创建新的`SimulationEngine`实例运行仿真
3. **结果应用**：优化完成后，将最优参数应用到系统中

### 4.2 性能考虑

- **并行评估**：可以使用`multiprocessing`库实现并行评估，减少优化时间
- **仿真时间**：为了平衡评估精度和计算成本，每次仿真运行30秒
- **参数范围**：基于领域知识设置合理的参数范围，减少搜索空间

## 5. 实施步骤

1. **创建优化模块**：实现`optimization.py`文件，包含PSO优化器
2. **配置参数范围**：根据系统特性设置合理的参数范围
3. **运行优化**：执行`run_optimization.py`脚本进行参数优化
4. **验证结果**：对优化后的参数进行多次仿真验证
5. **应用最优参数**：将优化后的参数应用到系统中

## 6. 预期效果

- **性能提升**：通过优化参数，提高系统的通行效率，减少碰撞次数
- **适应性**：系统能够自动适应不同的交通场景
- **可扩展性**：优化框架可以扩展到更多参数和更复杂的场景

## 7. 注意事项

- **计算成本**：PSO优化需要大量的仿真计算，可能需要较长时间
- **参数调优**：PSO算法自身的参数（如惯性权重、学习因子）可能需要调整
- **结果验证**：优化后的参数需要在不同场景下进行验证
- **并行计算**：充分利用计算资源，使用并行评估提高优化效率

## 8. 后续扩展

- **多目标优化**：考虑同时优化多个目标（如通行效率、安全性、公平性）
- **动态参数**：实现参数的动态调整，根据实时交通状况自适应调整
- **其他算法**：尝试其他优化算法（如遗传算法、模拟退火）进行比较
- **参数敏感性分析**：分析各参数对系统性能的影响程度

---

本方案通过PSO算法自动优化仿真系统参数，提高系统的真实性和准确性，为交通规划和安全评估提供更可靠的参考。