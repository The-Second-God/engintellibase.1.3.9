#!/usr/bin/env python3
"""
训练数据可视化脚本
用于分析和展示已训练的数据
"""
import numpy as np
import matplotlib.pyplot as plt
import json
import os

# 确保outcome目录存在
OUTCOME_DIR = 'outcome'
if not os.path.exists(OUTCOME_DIR):
    os.makedirs(OUTCOME_DIR)

def load_best_params():
    """加载最优参数"""
    try:
        params = {}
        with open('best_params.txt', 'r') as f:
            for line in f:
                key, value = line.strip().split(': ')
                params[key] = float(value)
        return params
    except Exception as e:
        print(f"Error loading best_params.txt: {e}")
        return None

def load_optimization_results():
    """加载优化结果"""
    try:
        iterations = []
        fitness = []
        params = []
        with open('optimization_results.txt', 'r') as f:
            next(f)  # 跳过表头
            for line in f:
                parts = line.strip().split(',', 2)
                if len(parts) >= 3:
                    iterations.append(int(parts[0]))
                    fitness.append(float(parts[1]))
                    # 解析参数字典
                    param_str = parts[2].replace('{', '').replace('}', '')
                    param_dict = {}
                    for param in param_str.split(', '):
                        if param:
                            key, val = param.split(': ')
                            # 处理numpy格式的数值
                            val = val.replace('np.float64(', '').replace(')', '')
                            param_dict[key] = float(val)
                    params.append(param_dict)
        return iterations, fitness, params
    except Exception as e:
        print(f"Error loading optimization_results.txt: {e}")
        return [], [], []

def load_particles_data():
    """加载粒子数据"""
    try:
        data = []
        with open('particles_data.txt', 'r') as f:
            next(f)  # 跳过表头
            for line in f:
                parts = line.strip().split(',', 4)
                if len(parts) >= 5:
                    iteration = int(parts[0])
                    particle_id = int(parts[1])
                    initial_pos = list(map(float, parts[2].split(',')))
                    final_pos = list(map(float, parts[3].split(',')))
                    fitness = float(parts[4])
                    data.append({
                        'iteration': iteration,
                        'particle_id': particle_id,
                        'initial_position': initial_pos,
                        'final_position': final_pos,
                        'fitness': fitness
                    })
        return data
    except Exception as e:
        print(f"Error loading particles_data.txt: {e}")
        return []

def load_iteration_best_results():
    """加载迭代最佳结果"""
    try:
        iterations = []
        fitness = []
        params = []
        with open('iteration_best_results.txt', 'r') as f:
            next(f)  # 跳过表头
            for line in f:
                parts = line.strip().split(',', 2)
                if len(parts) >= 3:
                    iterations.append(int(parts[0]))
                    fitness.append(float(parts[1]))
                    # 解析参数字典
                    param_str = parts[2].replace('{', '').replace('}', '')
                    param_dict = {}
                    for param in param_str.split(', '):
                        if param:
                            key, val = param.split(': ')
                            # 处理numpy格式的数值
                            val = val.replace('np.float64(', '').replace(')', '')
                            param_dict[key] = float(val)
                    params.append(param_dict)
        return iterations, fitness, params
    except Exception as e:
        print(f"Error loading iteration_best_results.txt: {e}")
        return [], [], []

def plot_fitness_evolution(iterations, fitness):
    """绘制适应度演化图"""
    plt.figure(figsize=(12, 6))
    plt.plot(iterations, fitness, '-o', linewidth=2, markersize=5)
    plt.title('Fitness Evolution During Optimization', fontsize=16)
    plt.xlabel('Iteration', fontsize=12)
    plt.ylabel('Fitness', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTCOME_DIR, 'fitness_evolution.png'), dpi=150)
    plt.close()
    print("Fitness evolution plot saved to outcome/fitness_evolution.png")

def plot_param_evolution(iterations, params):
    """绘制参数演化图"""
    if not params:
        return
    
    # 获取所有参数名
    param_names = list(params[0].keys())
    
    for param_name in param_names:
        param_values = [p.get(param_name, 0) for p in params]
        
        plt.figure(figsize=(12, 6))
        plt.plot(iterations, param_values, '-o', linewidth=2, markersize=5)
        plt.title(f'{param_name} Evolution', fontsize=16)
        plt.xlabel('Iteration', fontsize=12)
        plt.ylabel(param_name, fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTCOME_DIR, f'{param_name}_evolution.png'), dpi=150)
        plt.close()
        print(f"{param_name} evolution plot saved to outcome/{param_name}_evolution.png")

def plot_particle_fitness_distribution(particles_data):
    """绘制粒子适应度分布图"""
    if not particles_data:
        return
    
    # 按迭代分组
    iterations = sorted(set(data['iteration'] for data in particles_data))
    
    for iteration in iterations:
        iteration_data = [data for data in particles_data if data['iteration'] == iteration]
        fitness_values = [data['fitness'] for data in iteration_data]
        
        plt.figure(figsize=(10, 6))
        plt.hist(fitness_values, bins=20, alpha=0.7, edgecolor='black')
        plt.title(f'Particle Fitness Distribution - Iteration {iteration}', fontsize=16)
        plt.xlabel('Fitness', fontsize=12)
        plt.ylabel('Count', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(os.path.join(OUTCOME_DIR, f'particle_fitness_iteration_{iteration}.png'), dpi=150)
        plt.close()
    
    print("Particle fitness distribution plots saved to outcome directory")

def create_summary_report(best_params, iterations, fitness):
    """创建总结报告"""
    report = f"""
# 训练数据可视化报告

## 最优参数
{json.dumps(best_params, indent=2)}

## 优化过程
- 总迭代次数: {len(iterations)}
- 最佳适应度: {max(fitness):.4f}
- 平均适应度: {sum(fitness)/len(fitness):.4f}
- 适应度提升: {((max(fitness) - fitness[0])/fitness[0] * 100):.2f}%

## 生成的文件
- fitness_evolution.png - 适应度演化图
- 参数演化图 - 每个参数的演化趋势
- 粒子适应度分布图 - 各迭代的粒子适应度分布
"""
    
    with open(os.path.join(OUTCOME_DIR, 'summary_report.md'), 'w', encoding='utf-8') as f:
        f.write(report)
    
    print("Summary report saved to outcome/summary_report.md")

def main():
    """主函数"""
    print("Loading training data...")
    
    # 加载数据
    best_params = load_best_params()
    iterations, fitness, params = load_optimization_results()
    particles_data = load_particles_data()
    iter_best_iterations, iter_best_fitness, iter_best_params = load_iteration_best_results()
    
    print("Generating visualizations...")
    
    # 生成可视化
    if iterations and fitness:
        plot_fitness_evolution(iterations, fitness)
    
    if iterations and params:
        plot_param_evolution(iterations, params)
    
    if particles_data:
        plot_particle_fitness_distribution(particles_data)
    
    if best_params and iterations and fitness:
        create_summary_report(best_params, iterations, fitness)
    
    print("All visualizations have been generated and saved to the 'outcome' directory.")

if __name__ == '__main__':
    main()
