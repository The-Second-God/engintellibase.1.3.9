"""
运行PSO优化脚本
"""
from crossing_simulation import PSOOptimizer, Config

# 定义参数范围
param_ranges = {
    'DESIRED_FORCE_FACTOR': (0.5, 2.0),
    'SOCIAL_FORCE_A': (600.0, 6000.0),
    'SOCIAL_FORCE_B': (0.1, 0.3),
    'VISION_RANGE': (0.5, 8.0)
}

# 运行PSO优化
print("启动PSO参数优化...")
print(f"参数范围: {param_ranges}")
print("=" * 60)

optimizer = PSOOptimizer(
    param_ranges=param_ranges,
    population_size=100,  # 粒子数量
    max_iterations=70    # 迭代次数
)

print("开始优化过程...")
print("=" * 60)

best_params = optimizer.optimize()

print("=" * 60)
print("优化完成!")
print(f"最优适应度: {optimizer.gbest_fitness:.4f}")
print("最优参数:")
for key, value in best_params.items():
    print(f"  {key}: {value:.4f}")

# 应用最优参数
Config.update(**best_params)
print("\n最优参数已应用到系统配置中。")
print("可以运行 'python run_simulation.py' 查看优化效果。")

# 保存最优参数到文件
with open('best_params.txt', 'w') as f:
    for key, value in best_params.items():
        f.write(f"{key}: {value}\n")
print("\n最优参数已保存到 'best_params.txt' 文件。")