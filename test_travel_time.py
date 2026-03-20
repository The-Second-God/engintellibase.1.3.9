"""测试通行时间计算和记录功能"""
from crossing_simulation import Config, SimulationEngine

# 增加生成概率以便更快地生成实体
Config.PEDESTRIAN_SPAWN_PROBABILITY = 1.0
Config.BICYCLE_SPAWN_PROBABILITY = 0.5
Config.MIN_SPAWN_INTERVAL = 0.01
Config.MAX_ACTIVE_ENTITIES = 10
Config.MAX_SIMULATION_TIME = 20.0

# 增加期望速度以便实体更快到达目标
Config.PEDESTRIAN_SPEED_MIN = 1.5
Config.PEDESTRIAN_SPEED_MAX = 2.5
Config.BICYCLE_SPEED_MIN = 4.0
Config.BICYCLE_SPEED_MAX = 6.0

def test_travel_time_calculation():
    print("测试通行时间计算和记录功能")
    print("=" * 50)
    
    engine = SimulationEngine()
    engine.initialize()
    print('初始化成功')
    
    # 运行仿真直到有实体完成通行
    step_count = 0
    max_steps = 1000
    
    while engine.is_running and step_count < max_steps:
        state = engine.step()
        step_count += 1
        
        # 每100步打印一次状态
        if step_count % 100 == 0:
            print(f'步骤 {step_count}: 时间={state["time"]:.2f}s, 活跃实体={state["active_count"]}, 已完成实体={state["completed_count"]}')
            if state["statistics"]["avg_travel_time"] > 0:
                print(f'  平均通行时间: {state["statistics"]["avg_travel_time"]:.2f}s')
        
        # 如果有实体完成通行，打印详细信息
        if len(engine.completed_entities) > 0:
            print(f'\n实体完成通行:')
            for entity in engine.completed_entities:
                print(f'  ID: {entity.id}, 类型: {entity.type}, 通行时间: {entity.travel_time:.2f}s, 行驶距离: {entity.distance_traveled:.2f}m')
            break
    
    # 打印最终统计信息
    print("\n最终统计信息:")
    metrics = engine.get_detailed_metrics()
    print(f'总时间: {metrics["total_time"]:.2f}s')
    print(f'已完成实体数量: {metrics["completed_entities"]}')
    print(f'平均通行时间: {metrics["avg_travel_time"]:.2f}s')
    print(f'平均行驶距离: {metrics["avg_distance"]:.2f}m')
    print(f'碰撞次数: {metrics["collisions"]}')
    print(f'适应度: {metrics["fitness"]:.4f}')
    
    # 验证功能是否正常
    if len(engine.completed_entities) > 0:
        print("\n✅ 通行时间计算和记录功能测试通过!")
    else:
        print("\n⚠️  没有实体完成通行，无法验证功能")

if __name__ == "__main__":
    test_travel_time_calculation()