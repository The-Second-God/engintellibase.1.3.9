"""测试脚本"""
from crossing_simulation import Config, SimulationEngine

engine = SimulationEngine()
engine.initialize()
print('初始化成功')
print(f'实体数量: {len(engine.entity_manager.all_entities)}')

for i in range(10):
    state = engine.step()
    print(f'步骤 {i+1}: 时间={state["time"]:.2f}s, 活跃实体={state["active_count"]}')

print('测试完成!')
