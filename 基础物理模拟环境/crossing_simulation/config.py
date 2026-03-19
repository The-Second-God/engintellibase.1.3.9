"""
配置参数模块 - 所有可调参数集中管理
修改此文件中的参数即可调整仿真行为，无需修改其他代码
"""

class Config:
    
    # ==================== 环境参数 ====================
    CROSSING_WIDTH = 10.0  # 交叉路口宽度（米）
    CROSSING_HEIGHT = 10.0  # 交叉路口高度（米）
    ROAD_WIDTH = 3.0  # 道路宽度（米）
    
    # ==================== 行人参数 ====================
    PEDESTRIAN_COUNT = 15  # 初始行人数量
    PEDESTRIAN_RADIUS = 0.100  # 行人半径（米），用于碰撞检测
    PEDESTRIAN_SPEED_MIN = 0.5  # 行人最小速度（米/秒）
    PEDESTRIAN_SPEED_MAX = 1.2  # 行人最大速度（米/秒）
    PEDESTRIAN_MASS = 70.0  # 行人质量（千克），影响受力计算
    
    # ==================== 自行车参数 ====================
    BICYCLE_COUNT = 5  # 初始自行车数量
    BICYCLE_RADIUS = 0.15  # 自行车半径（米），用于碰撞检测
    BICYCLE_SPEED_MIN = 1.0  # 自行车最小速度（米/秒）
    BICYCLE_SPEED_MAX = 3.0  # 自行车最大速度（米/秒）
    BICYCLE_MASS = 80.0  # 自行车质量（千克），影响受力计算
    
    # ==================== 社会力模型参数 ====================
    # 目标吸引力
    DESIRED_FORCE_FACTOR = 1.0  # 目标吸引力系数，影响实体向目标移动的强度
    RELAXATION_TIME = 0.5  # 速度调整的时间常数（秒），值越小调整越快
    
    # 避让力参数
    SOCIAL_FORCE_A = 6000.0  # 社会力强度系数，值越大避让力越强
    SOCIAL_FORCE_B = 0.20  # 社会力作用范围系数，值越大作用范围越广
    
    # 避让触发距离（按实体类型组合）
    AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN = 0.02  # 行人-行人避让触发距离（米）
    AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE = 0.20  # 行人-自行车避让触发距离（米）
    AVOIDANCE_DISTANCE_BICYCLE_BICYCLE = 0.20  # 自行车-自行车避让触发距离（米）
    AVOIDANCE_FORCE_MULTIPLIER = 2.0  # 避让力放大系数，距离小于触发距离时的力放大倍数
    
    # 边界参数
    ROAD_BORDER_THRESHOLD = 0.15  # 道路边界阈值（米），用于边界约束
    
    # 视野参数
    VISION_ANGLE = 120.0  # 视野角度（度），实体能看到的水平范围
    VISION_RANGE = 3.0  # 视野范围（米），实体能看到的最大距离
    
    # ==================== 避让距离参数 ====================
    AVOIDANCE_DISTANCE_FACTOR = 0.2  # 基于首次相遇距离的避让距离系数
    MIN_AVOIDANCE_DISTANCE = 0.05  # 最小避让距离（米），无论首次相遇距离多小
    MAX_AVOIDANCE_DISTANCE = 0.3  # 最大避让距离（米），无论首次相遇距离多大
    AVOIDANCE_FORCE_MULTIPLIER = 4.0  # 基于首次相遇的避让力倍增系数
    
    # ==================== 仿真参数 ====================
    DT = 0.02  # 时间步长（秒），仿真的时间精度
    MAX_SIMULATION_TIME = 60.0  # 最大仿真时间（秒）
    
    # ==================== 实体生成参数 ====================
    MAX_ACTIVE_ENTITIES = 80  # 最大活跃实体数，超过后不再生成新实体
    PEDESTRIAN_SPAWN_PROBABILITY = 0.3  # 行人生成概率，每帧生成行人的概率
    BICYCLE_SPAWN_PROBABILITY = 0.12  # 自行车生成概率，每帧生成自行车的概率
    MIN_SPAWN_INTERVAL = 0.3  # 最小生成间隔（秒），避免短时间内生成过多实体
    
    # ==================== 可视化参数 ====================
    FPS = 30  # 帧率，每秒显示的帧数
    WINDOW_WIDTH = 800  # 窗口宽度（像素）
    WINDOW_HEIGHT = 800  # 窗口高度（像素）
    SHOW_TRAILS = True  # 是否显示实体运动轨迹
    TRAIL_LENGTH = 50  # 轨迹长度，显示多少个历史位置
    SHOW_VISION_CONE = False  # 是否显示实体视野锥
    
    # ==================== 颜色配置 ====================
    COLOR_PEDESTRIAN = (0, 0.588, 1.0)  # 行人颜色 (RGB 0-1)
    COLOR_BICYCLE = (1.0, 0.392, 0)  # 自行车颜色 (RGB 0-1)
    COLOR_BACKGROUND = (0.941, 0.941, 0.941)  # 背景颜色 (RGB 0-1)
    COLOR_ROAD = (0.706, 0.706, 0.706)  # 道路颜色 (RGB 0-1)
    COLOR_CROSSWALK = (0.784, 0.784, 0.784)  # 斑马线颜色 (RGB 0-1)
    
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
