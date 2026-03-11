"""
实体类模块 - 行人和自行车的定义
"""
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .config import Config
from .avoidance_manager import AvoidanceDistanceManager


class Direction(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


@dataclass
class Vector2D:
    x: float
    y: float
    
    def __add__(self, other):
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other):
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar):
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar):
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def normalize(self) -> 'Vector2D':
        mag = self.magnitude()
        if mag > 0:
            return Vector2D(self.x / mag, self.y / mag)
        return Vector2D(0, 0)
    
    def dot(self, other) -> float:
        return self.x * other.x + self.y * other.y
    
    def angle(self) -> float:
        return math.degrees(math.atan2(self.y, self.x))
    
    @staticmethod
    def from_angle(angle_deg: float, magnitude: float = 1.0) -> 'Vector2D':
        angle_rad = math.radians(angle_deg)
        return Vector2D(
            magnitude * math.cos(angle_rad),
            magnitude * math.sin(angle_rad)
        )


class Entity:
    def __init__(self, entity_id: int, entity_type: str, 
                 position: Vector2D, direction: Direction,
                 desired_speed: float):
        self.id = entity_id
        self.type = entity_type
        self.position = position
        self.velocity = Vector2D(0, 0)
        self.acceleration = Vector2D(0, 0)
        self.direction = direction
        self.desired_speed = desired_speed
        
        params = Config.get_entity_params(entity_type)
        self.radius = params['radius']
        self.mass = params['mass']
        
        self.target = self._calculate_target()
        self.desired_direction = (self.target - self.position).normalize()
        
        self.trail: List[Tuple[float, float]] = []
        self.is_active = True
        self.travel_time = 0.0
        self.distance_traveled = 0.0
        
        self.first_encounter_positions: Dict[int, Vector2D] = {}
        self.encountered_entities: set = set()
    
    def _calculate_target(self) -> Vector2D:
        margin = 1.0
        if self.direction == Direction.NORTH:
            return Vector2D(self.position.x, Config.CROSSING_HEIGHT + margin)
        elif self.direction == Direction.SOUTH:
            return Vector2D(self.position.x, -margin)
        elif self.direction == Direction.EAST:
            return Vector2D(Config.CROSSING_WIDTH + margin, self.position.y)
        else:
            return Vector2D(-margin, self.position.y)
    
    def update_trail(self):
        if Config.SHOW_TRAILS:
            self.trail.append((self.position.x, self.position.y))
            if len(self.trail) > Config.TRAIL_LENGTH:
                self.trail.pop(0)
    
    def has_reached_target(self) -> bool:
        distance = (self.target - self.position).magnitude()
        return distance < self.radius
    
    def get_forward_direction(self) -> Vector2D:
        return self.desired_direction
    
    def is_in_vision(self, other: 'Entity') -> bool:
        to_other = other.position - self.position
        distance = to_other.magnitude()
        
        if distance > Config.VISION_RANGE:
            return False
        
        if distance < 1e-6:
            return True
        
        forward = self.get_forward_direction()
        to_other_norm = to_other.normalize()
        
        dot_product = forward.dot(to_other_norm)
        angle = math.degrees(math.acos(max(-1, min(1, dot_product))))
        
        return angle <= Config.VISION_ANGLE / 2
    
    def record_first_encounter(self, other: 'Entity') -> bool:
        if other.id in self.encountered_entities:
            return False
        
        self.encountered_entities.add(other.id)
        self.first_encounter_positions[other.id] = Vector2D(
            self.position.x, self.position.y
        )
        return True
    
    def has_encountered(self, other_id: int) -> bool:
        return other_id in self.encountered_entities
    
    def get_first_encounter_position(self, other_id: int) -> Optional[Vector2D]:
        return self.first_encounter_positions.get(other_id)


class Pedestrian(Entity):
    def __init__(self, entity_id: int, position: Vector2D, 
                 direction: Direction, desired_speed: float):
        super().__init__(entity_id, 'pedestrian', position, direction, desired_speed)


class Bicycle(Entity):
    def __init__(self, entity_id: int, position: Vector2D, 
                 direction: Direction, desired_speed: float):
        super().__init__(entity_id, 'bicycle', position, direction, desired_speed)


class EntityManager:
    def __init__(self):
        self.pedestrians: List[Pedestrian] = []
        self.bicycles: List[Bicycle] = []
        self.all_entities: List[Entity] = []
        self._next_id = 0
        
        # 实体类型映射表
        self._entity_type_map = {
            'pedestrian': Pedestrian,
            'bicycle': Bicycle
        }
        self.avoidance_manager = AvoidanceDistanceManager()
    
    def _generate_spawn_position(self, direction: Direction) -> Vector2D:
        road_half = Config.ROAD_WIDTH / 2
        center_x = Config.CROSSING_WIDTH / 2
        center_y = Config.CROSSING_HEIGHT / 2
        
        if direction == Direction.NORTH:
            x = center_x + random.uniform(-road_half * 0.8, road_half * 0.8)
            y = -1.0
        elif direction == Direction.SOUTH:
            x = center_x + random.uniform(-road_half * 0.8, road_half * 0.8)
            y = Config.CROSSING_HEIGHT + 1.0
        elif direction == Direction.EAST:
            x = -1.0
            y = center_y + random.uniform(-road_half * 0.8, road_half * 0.8)
        else:
            x = Config.CROSSING_WIDTH + 1.0
            y = center_y + random.uniform(-road_half * 0.8, road_half * 0.8)
        
        return Vector2D(x, y)
    
    def _generate_random_speed(self, entity_type: str) -> float:
        params = Config.get_entity_params(entity_type)
        return random.uniform(params['speed_min'], params['speed_max'])
    
    def _create_single_entity(self, entity_type: str) -> Optional[Entity]:
        """创建单个实体，返回创建的实体对象，如果达到最大数量则返回 None"""
        if len([e for e in self.all_entities if e.is_active]) >= Config.MAX_ACTIVE_ENTITIES:
            return None
        
        direction = random.choice(list(Direction))
        position = self._generate_spawn_position(direction)
        speed = self._generate_random_speed(entity_type)
        
        # 使用类型映射创建实体
        entity_class = self._entity_type_map.get(entity_type)
        if entity_class is None:
            raise ValueError(f"Unknown entity type: {entity_type}")
        
        entity = entity_class(
            entity_id=self._next_id,
            position=position,
            direction=direction,
            desired_speed=speed
        )
        
        # 添加到对应的类型列表
        if entity_type == 'pedestrian':
            self.pedestrians.append(entity)
        elif entity_type == 'bicycle':
            self.bicycles.append(entity)
        
        self.all_entities.append(entity)
        self._next_id += 1
        
        return entity
    
    def create_pedestrians(self, count: int = None):
        """创建指定数量的行人实体"""
        if count is None:
            count = Config.PEDESTRIAN_COUNT
        
        for _ in range(count):
            self._create_single_entity('pedestrian')
    
    def create_bicycles(self, count: int = None):
        """创建指定数量的自行车实体"""
        if count is None:
            count = Config.BICYCLE_COUNT
        
        for _ in range(count):
            self._create_single_entity('bicycle')
    
    def create_entity(self, entity_type: str) -> bool:
        """创建单个实体，返回是否创建成功"""
        entity = self._create_single_entity(entity_type)
        return entity is not None
    
    def initialize(self):
        pass  # 不再一次性生成所有实体
    
    def get_neighbors_in_vision(self, entity: Entity) -> List[Entity]:
        neighbors = []
        for other in self.all_entities:
            if other.id != entity.id and other.is_active:
                if entity.is_in_vision(other):
                    neighbors.append(other)
                    self._record_mutual_encounter(entity, other)
        return neighbors
    
    def _record_mutual_encounter(self, entity1: Entity, entity2: Entity):
        entity1.record_first_encounter(entity2)
        entity2.record_first_encounter(entity1)
        self.avoidance_manager.check_and_record_encounter(entity1, entity2)
    
    def remove_inactive(self):
        for entity in self.all_entities:
            if not entity.is_active:
                self.avoidance_manager.remove_entity_records(entity.id)
        
        self.all_entities = [e for e in self.all_entities if e.is_active]
        self.pedestrians = [p for p in self.pedestrians if p.is_active]
        self.bicycles = [b for b in self.bicycles if b.is_active]
    
    def get_statistics(self) -> dict:
        active_count = sum(1 for e in self.all_entities if e.is_active)
        completed = [e for e in self.all_entities if not e.is_active]
        
        return {
            'active_entities': active_count,
            'completed_count': len(completed),
            'avg_travel_time': sum(e.travel_time for e in completed) / len(completed) if completed else 0,
            'total_distance': sum(e.distance_traveled for e in self.all_entities + completed)
        }
