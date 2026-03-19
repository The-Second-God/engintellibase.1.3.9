"""测试持续生成实体"""
from crossing_simulation import Config, SimulationEngine

engine = SimulationEngine()
engine.initialize()
print('初始化成功')

print('\n运行100步，观察实体生成...')
for i in range(100):
    state = engine.step()
    if i % 10 == 0:
        print(f'步骤 {i+1}: 时间={state["time"]:.2f}s, 活跃实体={state["active_count"]}, 已完成={state["completed_count"]}, 碰撞={state["collision_count"]}')

print('\n测试完成!')
print(f'总碰撞次数: {engine.collision_count}')
print(f'总完成实体: {engine.completed_count}')
