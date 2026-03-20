"""
实体类模块 - 行人和自行车的定义
"""
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

import numpy as np

from .config import Config


class SpatialGrid:
    def __init__(self, cell_size=1.0):
        self.cell_size = cell_size
        self.grid = {}
    
    def add_entity(self, entity):
        key = self._get_cell_key(entity.position)
        if key not in self.grid:
            self.grid[key] = []
        self.grid[key].append(entity)
    
    def remove_entity(self, entity):
        key = self._get_cell_key(entity.position)
        if key in self.grid:
            self.grid[key] = [e for e in self.grid[key] if e.id != entity.id]
            if not self.grid[key]:
                del self.grid[key]
    
    def update_entity(self, entity):
        self.remove_entity(entity)
        self.add_entity(entity)
    
    def get_nearby_entities(self, position, radius):
        nearby = []
        # 计算需要检查的网格范围
        cell_radius = math.ceil(radius / self.cell_size)
        center_key = self._get_cell_key(position)
        
        # 检查周围的网格
        for i in range(-cell_radius, cell_radius + 1):
            for j in range(-cell_radius, cell_radius + 1):
                key = (center_key[0] + i, center_key[1] + j)
                if key in self.grid:
                    nearby.extend(self.grid[key])
        
        return nearby
    
    def _get_cell_key(self, position):
        return (int(position.x / self.cell_size), int(position.y / self.cell_size))


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
        
        # 添加NumPy数组属性
        self.position_np = np.array([position.x, position.y], dtype=np.float32)
        self.velocity_np = np.array([0.0, 0.0], dtype=np.float32)
        self.acceleration_np = np.array([0.0, 0.0], dtype=np.float32)
        self.target_np = np.array([self.target.x, self.target.y], dtype=np.float32)
        self.desired_direction_np = np.array([self.desired_direction.x, self.desired_direction.y], dtype=np.float32)
        
        self.trail: List[Tuple[float, float]] = []
        self.is_active = True
        self.travel_time = 0.0
        self.distance_traveled = 0.0
    
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
        # 基于边界的完成判定
        if self.direction == Direction.NORTH and self.position.y > Config.CROSSING_HEIGHT:
            return True
        elif self.direction == Direction.SOUTH and self.position.y < 0:
            return True
        elif self.direction == Direction.EAST and self.position.x > Config.CROSSING_WIDTH:
            return True
        elif self.direction == Direction.WEST and self.position.x < 0:
            return True
        return False
    
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
        self.spatial_grid = SpatialGrid(cell_size=Config.VISION_RANGE)
    
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
    
    def create_pedestrians(self, count: int = None):
        if count is None:
            count = Config.PEDESTRIAN_COUNT
        
        for _ in range(count):
            direction = random.choice(list(Direction))
            position = self._generate_spawn_position(direction)
            speed = self._generate_random_speed('pedestrian')
            
            pedestrian = Pedestrian(
                entity_id=self._next_id,
                position=position,
                direction=direction,
                desired_speed=speed
            )
            self.pedestrians.append(pedestrian)
            self.all_entities.append(pedestrian)
            self.spatial_grid.add_entity(pedestrian)
            self._next_id += 1
    
    def create_bicycles(self, count: int = None):
        if count is None:
            count = Config.BICYCLE_COUNT
        
        for _ in range(count):
            direction = random.choice(list(Direction))
            position = self._generate_spawn_position(direction)
            speed = self._generate_random_speed('bicycle')
            
            bicycle = Bicycle(
                entity_id=self._next_id,
                position=position,
                direction=direction,
                desired_speed=speed
            )
            self.bicycles.append(bicycle)
            self.all_entities.append(bicycle)
            self.spatial_grid.add_entity(bicycle)
            self._next_id += 1
    
    def create_entity(self, entity_type: str) -> bool:
        if len([e for e in self.all_entities if e.is_active]) >= Config.MAX_ACTIVE_ENTITIES:
            return False
        
        direction = random.choice(list(Direction))
        position = self._generate_spawn_position(direction)
        speed = self._generate_random_speed(entity_type)
        
        if entity_type == 'pedestrian':
            entity = Pedestrian(
                entity_id=self._next_id,
                position=position,
                direction=direction,
                desired_speed=speed
            )
            self.pedestrians.append(entity)
        else:
            entity = Bicycle(
                entity_id=self._next_id,
                position=position,
                direction=direction,
                desired_speed=speed
            )
            self.bicycles.append(entity)
        
        self.all_entities.append(entity)
        self.spatial_grid.add_entity(entity)
        self._next_id += 1
        return True
    
    def initialize(self):
        pass  # 不再一次性生成所有实体
    
    def get_neighbors_in_vision(self, entity: Entity) -> List[Entity]:
        # 首先通过空间网格获取附近实体
        nearby_entities = self.spatial_grid.get_nearby_entities(
            entity.position, Config.VISION_RANGE
        )
        
        # 然后检查视野
        neighbors = []
        for other in nearby_entities:
            if other.id != entity.id and other.is_active:
                if entity.is_in_vision(other):
                    neighbors.append(other)
        return neighbors
    
    def remove_inactive(self):
        inactive = [e for e in self.all_entities if not e.is_active]
        self.all_entities = [e for e in self.all_entities if e.is_active]
        self.pedestrians = [p for p in self.pedestrians if p.is_active]
        self.bicycles = [b for b in self.bicycles if b.is_active]
        
        for e in inactive:
            self.spatial_grid.remove_entity(e)
    
    def get_statistics(self) -> dict:
        active_count = sum(1 for e in self.all_entities if e.is_active)
        completed = [e for e in self.all_entities if not e.is_active]
        
        return {
            'active_entities': active_count,
            'completed_count': len(completed),
            'avg_travel_time': sum(e.travel_time for e in completed) / len(completed) if completed else 0,
            'total_distance': sum(e.distance_traveled for e in self.all_entities + completed)
        }
