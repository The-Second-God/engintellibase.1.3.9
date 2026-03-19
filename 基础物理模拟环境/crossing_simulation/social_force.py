"""
社会力模型模块 - 处理避让行为和运动计算
基于Helbing的社会力模型，结合180°视野限制和避让距离机制
"""
import math
from typing import List, Tuple
from .entity import Entity, Vector2D, EntityManager
from .environment import CrossingEnvironment
from .config import Config


class SocialForceModel:
    def __init__(self, environment: CrossingEnvironment, entity_manager: EntityManager = None):
        self.environment = environment
        self.entity_manager = entity_manager
    
    def set_entity_manager(self, entity_manager: EntityManager):
        self.entity_manager = entity_manager
    
    def calculate_desired_force(self, entity: Entity) -> Vector2D:
        desired_velocity = entity.desired_direction * entity.desired_speed
        force = (desired_velocity - entity.velocity) * (entity.mass / Config.RELAXATION_TIME)
        return force * Config.DESIRED_FORCE_FACTOR
    
    def calculate_social_force(self, entity: Entity, other: Entity) -> Vector2D:
        diff = entity.position - other.position
        distance = diff.magnitude()
        
        if distance < 1e-6:
            return Vector2D(0, 0)
        
        direction = diff.normalize()
        
        combined_radius = entity.radius + other.radius
        effective_distance = distance - combined_radius
        
        # 根据实体类型获取避让触发距离
        if entity.type == 'pedestrian' and other.type == 'pedestrian':
            avoidance_distance = Config.AVOIDANCE_DISTANCE_PEDESTRIAN_PEDESTRIAN
        elif (entity.type == 'pedestrian' and other.type == 'bicycle') or \
             (entity.type == 'bicycle' and other.type == 'pedestrian'):
            avoidance_distance = Config.AVOIDANCE_DISTANCE_PEDESTRIAN_BICYCLE
        else:  # bicycle and bicycle
            avoidance_distance = Config.AVOIDANCE_DISTANCE_BICYCLE_BICYCLE
        
        # 只有当有效距离小于避让触发距离时才计算避让力
        if effective_distance < avoidance_distance:
            force_magnitude = Config.SOCIAL_FORCE_A * math.exp(-effective_distance / Config.SOCIAL_FORCE_B)
            # 避让力放大
            if effective_distance < 0:  # 发生重叠
                force_magnitude *= Config.AVOIDANCE_FORCE_MULTIPLIER
            return direction * force_magnitude
        else:
            return Vector2D(0, 0)
    
    def calculate_avoidance_force(self, entity: Entity, other: Entity) -> Tuple[Vector2D, bool]:
        if not self.entity_manager:
            return Vector2D(0, 0), False
        
        avoidance_manager = self.entity_manager.avoidance_manager
        should_avoid, distance_exceeded = avoidance_manager.should_trigger_avoidance(entity, other)
        
        if not should_avoid:
            return Vector2D(0, 0), False
        
        diff = entity.position - other.position
        distance = diff.magnitude()
        
        if distance < 1e-6:
            return Vector2D(0, 0), False
        
        direction = diff.normalize()
        
        avoidance_distance = avoidance_manager.get_avoidance_distance(entity.id, other.id)
        force_magnitude = Config.SOCIAL_FORCE_A * Config.AVOIDANCE_FORCE_MULTIPLIER * math.exp(-distance / avoidance_distance)
        
        return direction * force_magnitude, True
    

    
    def calculate_total_force(self, entity: Entity, neighbors: List[Entity]) -> Vector2D:
        total_force = Vector2D(0, 0)
        
        desired_force = self.calculate_desired_force(entity)
        total_force = total_force + desired_force
        
        for neighbor in neighbors:
            social_force = self.calculate_social_force(entity, neighbor)
            total_force = total_force + social_force
            
            avoidance_force, is_avoiding = self.calculate_avoidance_force(entity, neighbor)
            if is_avoiding:
                total_force = total_force + avoidance_force
        
        return total_force
    
    def update_entity(self, entity: Entity, neighbors: List[Entity], dt: float):
        force = self.calculate_total_force(entity, neighbors)
        
        acceleration = force / entity.mass
        
        max_acceleration = 5.0
        if acceleration.magnitude() > max_acceleration:
            acceleration = acceleration.normalize() * max_acceleration
        
        entity.velocity = entity.velocity + acceleration * dt
        
        max_speed_factor = 1.5
        max_speed = entity.desired_speed * max_speed_factor
        if entity.velocity.magnitude() > max_speed:
            entity.velocity = entity.velocity.normalize() * max_speed
        
        old_position = Vector2D(entity.position.x, entity.position.y)
        new_position = entity.position + entity.velocity * dt
        
        new_position = self._enforce_road_boundaries(entity, new_position)
        
        entity.position = new_position
        
        entity.acceleration = acceleration
        entity.distance_traveled += (entity.position - old_position).magnitude()
        entity.travel_time += dt
        
        entity.update_trail()
    
    def _enforce_road_boundaries(self, entity: Entity, position: Vector2D) -> Vector2D:
        from .entity import Direction
        center_x = Config.CROSSING_WIDTH / 2
        center_y = Config.CROSSING_HEIGHT / 2
        half_road = Config.ROAD_WIDTH / 2
        threshold = Config.ROAD_BORDER_THRESHOLD
        
        is_east_west = entity.direction in [Direction.EAST, Direction.WEST]
        is_north_south = entity.direction in [Direction.NORTH, Direction.SOUTH]
        
        in_crossing = (
            (center_x - half_road <= position.x <= center_x + half_road) and
            (center_y - half_road <= position.y <= center_y + half_road)
        )
        
        if is_east_west:
            if not in_crossing:
                min_y = center_y - half_road + threshold
                max_y = center_y + half_road - threshold
                position.y = max(min(position.y, max_y), min_y)
        
        if is_north_south:
            if not in_crossing:
                min_x = center_x - half_road + threshold
                max_x = center_x + half_road - threshold
                position.x = max(min(position.x, max_x), min_x)
        
        return position
    
    def check_collision(self, entity: Entity, neighbors: List[Entity]) -> int:
        collision_count = 0
        for neighbor in neighbors:
            distance = (entity.position - neighbor.position).magnitude()
            if distance < (entity.radius + neighbor.radius):
                collision_count += 1
        return collision_count
    
    def resolve_collision(self, entity: Entity, neighbor: Entity):
        diff = entity.position - neighbor.position
        distance = diff.magnitude()
        
        if distance < 1e-6:
            diff = Vector2D(0.1, 0.1)
            distance = diff.magnitude()
        
        combined_radius = entity.radius + neighbor.radius
        overlap = combined_radius - distance
        
        if overlap > 0:
            direction = diff.normalize()
            total_mass = entity.mass + neighbor.mass
            
            entity.position = entity.position + direction * (overlap * neighbor.mass / total_mass)
            neighbor.position = neighbor.position - direction * (overlap * entity.mass / total_mass)
            
            relative_velocity = entity.velocity - neighbor.velocity
            velocity_along_normal = relative_velocity.dot(direction)
            
            if velocity_along_normal > 0:
                restitution = 0.5
                impulse = (1 + restitution) * velocity_along_normal / total_mass
                
                entity.velocity = entity.velocity - direction * (impulse * neighbor.mass)
                neighbor.velocity = neighbor.velocity + direction * (impulse * entity.mass)
