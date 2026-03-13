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
    PEDESTRIAN_COUNT = 15
    PEDESTRIAN_RADIUS = 0.100  # 减半
    PEDESTRIAN_SPEED_MIN = 0.5
    PEDESTRIAN_SPEED_MAX = 1.2
    PEDESTRIAN_MASS = 70.0
    
    # ==================== 自行车参数 ====================
    BICYCLE_COUNT = 5
    BICYCLE_RADIUS = 0.15  # 减半
    BICYCLE_SPEED_MIN = 1.0
    BICYCLE_SPEED_MAX = 3.0
    BICYCLE_MASS = 80.0
    
    # ==================== 社会力模型参数 ====================
    # 目标吸引力
    DESIRED_FORCE_FACTOR = 1.0  # 减半
    RELAXATION_TIME = 0.5
    
    # 避让力参数
    SOCIAL_FORCE_A = 3000.0  # 增大强度
    SOCIAL_FORCE_B = 0.08  # 增大作用范围至约2m
    
    # 避让触发距离（按实体类型组合）
    AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN = 0.05  # 人与人
    AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE = 0.2    # 人与车
    AVOIDANCE_DISTANCE_BICYCLE_BICYCLE = 0.2       # 车与车
    AVOIDANCE_FORCE_MULTIPLIER = 1.0  # 避让力放大系数
    
    # 边界参数
    ROAD_BORDER_THRESHOLD = 0.1
    
    # 视野参数
    VISION_ANGLE = 120.0
    VISION_RANGE = 3.0  # 减小到4m
    
    # ==================== 避让距离参数 ====================
    AVOIDANCE_DISTANCE_FACTOR = 1.0  # 避让距离系数（相对于首次相遇距离）
    MIN_AVOIDANCE_DISTANCE = 0.3     # 最小避让距离（米）
    MAX_AVOIDANCE_DISTANCE = 1.0     # 最大避让距离（米）
    AVOIDANCE_FORCE_MULTIPLIER = 2.0 # 避让力倍增系数
    
    # ==================== 仿真参数 ====================
    DT = 0.05
    MAX_SIMULATION_TIME = 60.0
    
    # ==================== 实体生成参数 ====================
    MAX_ACTIVE_ENTITIES = 30  # 增加最大活跃实体数
    PEDESTRIAN_SPAWN_PROBABILITY = 0.3   # 增加行人生成概率
    BICYCLE_SPAWN_PROBABILITY = 0.12     # 增加自行车生成概率
    MIN_SPAWN_INTERVAL = 0.5             # 减少生成间隔
    
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
