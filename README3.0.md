# 十字路口行人通行仿真系统 - PSO参数优化执行方案

## 1. 项目概述

本项目是一个基于社会力模型的十字路口行人通行仿真系统，用于模拟行人和自行车在十字路口的行为和交互。本方案通过粒子群优化（PSO）算法自动优化系统参数，提高通行效率和安全性。

## 2. PSO算法技术细节

### 2.1 参数空间

| 参数名称 | 描述 | 范围 |
|---------|------|------|
| DESIRED_FORCE_FACTOR | 目标吸引力因子（影响速度） | [0.5, 2.0] |
| SOCIAL_FORCE_A | 社交力强度（避让强度） | [1000.0, 5000.0] |
| SOCIAL_FORCE_B | 社交力作用范围（避让距离） | [0.1, 0.3] |
| VISION_RANGE | 视野范围 | [2.0, 6.0] |

### 2.2 适应度函数

**权重分配**：
- 整体通行效率：75%
- 最慢10%通行效率：20%
- 碰撞惩罚：5%

**计算逻辑**：
1. 收集所有完成通行实体的通行时间
2. 计算平均通行时间（整体效率）
3. 计算最慢10%实体的平均通行时间
4. 计算碰撞惩罚
5. 加权求和得到总适应度

**实现代码**：
```python
def get_fitness(self) -> float:
    completed = [e for e in self.entity_manager.all_entities if not e.is_active]
    
    if not completed:
        return 0.0
    
    # 收集所有通行时间
    travel_times = [e.travel_time for e in completed]
    travel_times.sort()
    
    # 计算平均通行时间（整体效率）
    avg_time = sum(travel_times) / len(travel_times)
    
    # 计算最慢10%实体的平均时间
    slow_count = max(1, int(len(travel_times) * 0.1))
    slow_times = travel_times[-slow_count:]
    slow_avg_time = sum(slow_times) / len(slow_times)
    
    # 计算碰撞惩罚
    collision_penalty = self.collision_count * 10.0
    
    # 计算各部分权重
    efficiency = 1.0 / (avg_time + 0.1) * 0.75
    slow_penalty = 1.0 / (slow_avg_time + 0.1) * 0.20
    collision_factor = max(0, 1.0 - collision_penalty * 0.01) * 0.05
    
    # 总适应度
    fitness = efficiency + slow_penalty + collision_factor
    
    return max(0, fitness)
```

### 2.3 粒子群配置

- **粒子数量**：30-50个
- **迭代次数**：50-100次
- **速度初始化**：参数范围的正负区间
- **惯性权重**：0.7
- **学习因子**：c1=1.5（认知因子），c2=1.5（社会因子）

### 2.4 核心机制

- **并行计算**：使用`multiprocessing`库并行评估粒子适应度
- **热启动机制**：
  - 加载之前的最优参数作为初始gbest
  - 围绕最优值初始化粒子，加快收敛
- **数据持久化**：
  - 保存最优参数到`best_params.txt`
  - 保存优化过程数据到`optimization_results.txt`
  - 生成适应度演化图表`fitness_evolution.png`

## 3. 实施计划

### 3.1 步骤1：修改适应度函数

**文件**：`crossing_simulation/simulation.py`

**内容**：
- 更新`get_fitness()`方法
- 实现新的适应度计算逻辑
- 包含整体通行效率、最慢10%通行效率和碰撞惩罚的加权计算

### 3.2 步骤2：创建优化模块

**文件**：`crossing_simulation/optimization.py`

**内容**：
- 实现`PSOOptimizer`类
- 包含粒子群初始化、适应度评估、速度和位置更新
- 实现热启动机制，支持加载之前的最优参数

**核心代码结构**：
```python
class PSOOptimizer:
    def __init__(self, param_ranges, population_size=30, max_iterations=50):
        # 初始化粒子群和参数
    
    def evaluate_fitness(self, params):
        # 评估参数组合的适应度
    
    def optimize(self):
        # 执行PSO优化过程
```

### 3.3 步骤3：创建优化运行脚本

**文件**：`run_optimization.py`

**内容**：
- 配置参数范围
- 初始化并运行PSO优化器
- 保存优化结果到文件
- 生成适应度演化图表

**配置示例**：
```python
param_ranges = {
    'DESIRED_FORCE_FACTOR': (0.5, 2.0),
    'SOCIAL_FORCE_A': (1000.0, 5000.0),
    'SOCIAL_FORCE_B': (0.1, 0.3),
    'VISION_RANGE': (2.0, 6.0)
}
```

### 3.4 步骤4：运行优化

**执行命令**：
```bash
python run_optimization.py
```

**过程**：
- 观察每次迭代的最优参数和适应度
- 等待优化完成
- 查看生成的数据文件

### 3.5 步骤5：验证结果

**执行命令**：
```bash
python run_simulation.py
```

**过程**：
- 使用最优参数运行仿真
- 观察仿真效果
- 验证优化结果是否符合预期

### 3.6 步骤6：多次执行优化

**重复执行**：
```bash
python run_optimization.py
```

**过程**：
- 利用热启动机制继续优化
- 直到适应度不再显著改善
- 比较多次执行的优化效果

## 4. 预期成果

### 4.1 输出文件

- **best_params.txt**：最优参数配置
- **optimization_results.txt**：优化过程数据
- **fitness_evolution.png**：适应度演化图表

### 4.2 性能提升

- **整体通行效率**：提高系统的平均通行效率
- **最慢10%通行效率**：改善最差情况的通行体验
- **碰撞次数**：减少实体间的碰撞

### 4.3 数据反馈

- **实时反馈**：每次迭代显示当前最优参数和适应度值
- **详细输出**：优化完成后生成详细的结果报告
- **多次执行**：支持通过多次执行累积优化效果

## 5. 后续扩展

### 5.1 场景定制

- 添加用户输入接口，允许设置不同的生成概率场景
- 为不同流量密度场景分别优化参数

### 5.2 高级功能

- **参数敏感性分析**：分析各参数对系统性能的影响程度
- **其他算法对比**：尝试遗传算法、模拟退火等其他优化算法
- **动态参数调整**：实现根据实时交通状况自动调整参数

### 5.3 应用场景

- **交通规划**：评估十字路口的通行效率
- **算法研究**：测试和优化多智能体路径规划算法
- **教育教学**：演示群体行为和社会力模型
- **游戏开发**：为游戏中的NPC行为提供参考

## 6. 注意事项

### 6.1 计算成本

- PSO优化需要大量的仿真计算，可能需要较长时间
- 建议在性能较好的计算机上运行

### 6.2 参数调优

- PSO算法自身的参数（如惯性权重、学习因子）可能需要调整
- 建议根据实际情况调整`population_size`和`max_iterations`

### 6.3 结果验证

- 优化后的参数需要在不同场景下进行验证
- 确保参数在极端情况下也能表现良好

## 7. 技术栈

- **Python**：主要开发语言
- **NumPy**：向量化计算
- **Matplotlib**：可视化和图表生成
- **Multiprocessing**：并行计算

## 8. 结论

通过PSO算法自动优化仿真系统参数，可以显著提高系统的通行效率和安全性。本方案设计合理，与现有系统完全兼容，实施步骤清晰明确。通过多次执行优化，可以不断改进参数配置，为交通规划和安全评估提供更可靠的参考。