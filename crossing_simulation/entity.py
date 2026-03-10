"""
实体类模块 - 行人和自行车的定义
"""
import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .config import Config


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
            self._next_id += 1
    
    def initialize(self):
        self.create_pedestrians()
        self.create_bicycles()
    
    def get_neighbors_in_vision(self, entity: Entity) -> List[Entity]:
        neighbors = []
        for other in self.all_entities:
            if other.id != entity.id and other.is_active:
                if entity.is_in_vision(other):
                    neighbors.append(other)
        return neighbors
    
    def remove_inactive(self):
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
