"""
配置参数模块 - 所有可调参数集中管理
修改此文件中的参数即可调整仿真行为，无需修改其他代码
"""

class Config:
    
    # ==================== 环境参数 ====================
    CROSSING_WIDTH = 10.0
    CROSSING_HEIGHT = 10.0
    ROAD_WIDTH = 3.0
    
    # ==================== 行人参数 ====================
    PEDESTRIAN_COUNT = 10
    PEDESTRIAN_RADIUS = 0.125  # 减半
    PEDESTRIAN_SPEED_MIN = 1.0
    PEDESTRIAN_SPEED_MAX = 1.5
    PEDESTRIAN_MASS = 70.0
    
    # ==================== 自行车参数 ====================
    BICYCLE_COUNT = 4
    BICYCLE_RADIUS = 0.25  # 减半
    BICYCLE_SPEED_MIN = 3.0
    BICYCLE_SPEED_MAX = 5.0
    BICYCLE_MASS = 80.0
    
    # ==================== 社会力模型参数 ====================
    # 目标吸引力
    DESIRED_FORCE_FACTOR = 0.5  # 减半
    RELAXATION_TIME = 0.5
    
    # 避让力参数
    SOCIAL_FORCE_A = 3000.0  # 增大强度
    SOCIAL_FORCE_B = 0.2  # 增大作用范围至约2m
    
    # 边界参数
    ROAD_BORDER_THRESHOLD = 0.1
    
    # 视野参数
    VISION_ANGLE = 180.0
    VISION_RANGE = 4.0  # 减小到4m
    
    # ==================== 仿真参数 ====================
    DT = 0.05
    MAX_SIMULATION_TIME = 60.0
    
    # ==================== 实体生成参数 ====================
    MAX_ACTIVE_ENTITIES = 20
    PEDESTRIAN_SPAWN_PROBABILITY = 0.05  # 每步生成行人的概率
    BICYCLE_SPAWN_PROBABILITY = 0.02     # 每步生成自行车的概率
    MIN_SPAWN_INTERVAL = 1.0             # 最小生成间隔（秒）
    
    # ==================== 可视化参数 ====================
    FPS = 30
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 800
    SHOW_TRAILS = True
    TRAIL_LENGTH = 50
    SHOW_VISION_CONE = False
    
    # ==================== 颜色配置 ====================
    COLOR_PEDESTRIAN = (0, 0.588, 1.0)  # (0, 150, 255) / 255
    COLOR_BICYCLE = (1.0, 0.392, 0)      # (255, 100, 0) / 255
    COLOR_BACKGROUND = (0.941, 0.941, 0.941)  # (240, 240, 240) / 255
    COLOR_ROAD = (0.706, 0.706, 0.706)   # (180, 180, 180) / 255
    COLOR_CROSSWALK = (0.784, 0.784, 0.784)  # (200, 200, 200) / 255
    
    @classmethod
    def update(cls, **kwargs):
        for key, value in kwargs.items():
            if hasattr(cls, key):
                setattr(cls, key, value)
            else:
                raise ValueError(f"Unknown config parameter: {key}")
    
    @classmethod
    def get_entity_params(cls, entity_type):
        if entity_type == 'pedestrian':
            return {
                'radius': cls.PEDESTRIAN_RADIUS,
                'speed_min': cls.PEDESTRIAN_SPEED_MIN,
                'speed_max': cls.PEDESTRIAN_SPEED_MAX,
                'mass': cls.PEDESTRIAN_MASS,
            }
        elif entity_type == 'bicycle':
            return {
                'radius': cls.BICYCLE_RADIUS,
                'speed_min': cls.BICYCLE_SPEED_MIN,
                'speed_max': cls.BICYCLE_SPEED_MAX,
                'mass': cls.BICYCLE_MASS,
            }
        else:
            raise ValueError(f"Unknown entity type: {entity_type}")
