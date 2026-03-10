"""
主程序入口 - 运行基础仿真测试
"""
from crossing_simulation import (
    Config, SimulationEngine, AnimatedVisualizer
)


def main():
    print("=" * 50)
    print("十字路口行人通行仿真系统")
    print("=" * 50)
    print(f"\n当前配置:")
    print(f"  路口尺寸: {Config.CROSSING_WIDTH}m x {Config.CROSSING_HEIGHT}m")
    print(f"  道路宽度: {Config.ROAD_WIDTH}m")
    print(f"  行人数量: {Config.PEDESTRIAN_COUNT}")
    print(f"  自行车数量: {Config.BICYCLE_COUNT}")
    print(f"  视野角度: {Config.VISION_ANGLE}°")
    print(f"  视野范围: {Config.VISION_RANGE}m")
    print(f"  最大仿真时间: {Config.MAX_SIMULATION_TIME}s")
    print(f"  时间步长: {Config.DT}s")
    print("\n启动可视化仿真...")
    print("关闭窗口可结束仿真\n")
    
    engine = SimulationEngine()
    visualizer = AnimatedVisualizer(engine)
    
    visualizer.run()


if __name__ == "__main__":
    main()