"""
环境类模块 - 十字路口场景定义
"""
from typing import List, Tuple
from .entity import Vector2D
from .config import Config


class Wall:
    def __init__(self, start: Vector2D, end: Vector2D):
        self.start = start
        self.end = end
        self.direction = (end - start).normalize()
        self.length = (end - start).magnitude()
        self.normal = Vector2D(-self.direction.y, self.direction.x)
    
    def distance_to_point(self, point: Vector2D) -> float:
        v = point - self.start
        t = max(0, min(1, v.dot(self.direction) / self.length))
        closest = self.start + self.direction * t * self.length
        return (point - closest).magnitude()
    
    def get_closest_point(self, point: Vector2D) -> Vector2D:
        v = point - self.start
        t = max(0, min(1, v.dot(self.direction) / self.length))
        return self.start + self.direction * t * self.length


class CrossingEnvironment:
    def __init__(self):
        self.width = Config.CROSSING_WIDTH
        self.height = Config.CROSSING_HEIGHT
        self.road_width = Config.ROAD_WIDTH
        self.walls: List[Wall] = []
        self._create_walls()
    
    def _create_walls(self):
        center_x = self.width / 2
        center_y = self.height / 2
        half_road = self.road_width / 2
        
        self.walls = [
            Wall(Vector2D(0, center_y - half_road), Vector2D(center_x - half_road, center_y - half_road)),
            Wall(Vector2D(center_x + half_road, center_y - half_road), Vector2D(self.width, center_y - half_road)),
            Wall(Vector2D(0, center_y + half_road), Vector2D(center_x - half_road, center_y + half_road)),
            Wall(Vector2D(center_x + half_road, center_y + half_road), Vector2D(self.width, center_y + half_road)),
            
            Wall(Vector2D(center_x - half_road, 0), Vector2D(center_x - half_road, center_y - half_road)),
            Wall(Vector2D(center_x - half_road, center_y + half_road), Vector2D(center_x - half_road, self.height)),
            Wall(Vector2D(center_x + half_road, 0), Vector2D(center_x + half_road, center_y - half_road)),
            Wall(Vector2D(center_x + half_road, center_y + half_road), Vector2D(center_x + half_road, self.height)),
        ]
    
    def is_in_crossing_area(self, position: Vector2D) -> bool:
        center_x = self.width / 2
        center_y = self.height / 2
        half_road = self.road_width / 2
        
        in_horizontal = (center_y - half_road <= position.y <= center_y + half_road)
        in_vertical = (center_x - half_road <= position.x <= center_x + half_road)
        
        return in_horizontal or in_vertical
    
    def is_in_bounds(self, position: Vector2D, margin: float = 0.0) -> bool:
        return (-margin <= position.x <= self.width + margin and
                -margin <= position.y <= self.height + margin)
    
    def get_nearest_wall(self, position: Vector2D) -> Tuple[Wall, float]:
        min_distance = float('inf')
        nearest_wall = None
        
        for wall in self.walls:
            distance = wall.distance_to_point(position)
            if distance < min_distance:
                min_distance = distance
                nearest_wall = wall
        
        return nearest_wall, min_distance
    
    def get_road_boundaries(self) -> dict:
        center_x = self.width / 2
        center_y = self.height / 2
        half_road = self.road_width / 2
        
        return {
            'north_road': (center_y - half_road, center_y + half_road),
            'east_road': (center_x - half_road, center_x + half_road),
            'center': (center_x, center_y)
        }
    
    def get_spawn_zones(self) -> dict:
        center_x = self.width / 2
        center_y = self.height / 2
        half_road = self.road_width / 2
        
        return {
            'north': {
                'x_range': (center_x - half_road, center_x + half_road),
                'y': self.height + 1.0
            },
            'south': {
                'x_range': (center_x - half_road, center_x + half_road),
                'y': -1.0
            },
            'east': {
                'x': self.width + 1.0,
                'y_range': (center_y - half_road, center_y + half_road)
            },
            'west': {
                'x': -1.0,
                'y_range': (center_y - half_road, center_y + half_road)
            }
        }
