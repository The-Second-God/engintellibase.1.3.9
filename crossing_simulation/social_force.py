"""
社会力模型模块 - 处理避让行为和运动计算
基于Helbing的社会力模型，结合180°视野限制
"""
import math
from typing import List
from .entity import Entity, Vector2D
from .environment import CrossingEnvironment
from .config import Config


class SocialForceModel:
    def __init__(self, environment: CrossingEnvironment):
        self.environment = environment
    
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
        
        force_magnitude = Config.SOCIAL_FORCE_A * math.exp(-effective_distance / Config.SOCIAL_FORCE_B)
        
        return direction * force_magnitude
    
    def calculate_wall_force(self, entity: Entity) -> Vector2D:
        total_force = Vector2D(0, 0)
        
        for wall in self.environment.walls:
            distance = wall.distance_to_point(entity.position)
            effective_distance = distance - entity.radius
            
            if effective_distance < Config.VISION_RANGE:
                closest_point = wall.get_closest_point(entity.position)
                direction = (entity.position - closest_point).normalize()
                
                force_magnitude = Config.WALL_FORCE_A * math.exp(-effective_distance / Config.WALL_FORCE_B)
                total_force = total_force + direction * force_magnitude
        
        return total_force
    
    def calculate_total_force(self, entity: Entity, neighbors: List[Entity]) -> Vector2D:
        total_force = Vector2D(0, 0)
        
        desired_force = self.calculate_desired_force(entity)
        total_force = total_force + desired_force
        
        for neighbor in neighbors:
            social_force = self.calculate_social_force(entity, neighbor)
            total_force = total_force + social_force
        
        wall_force = self.calculate_wall_force(entity)
        total_force = total_force + wall_force
        
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
        entity.position = entity.position + entity.velocity * dt
        
        entity.acceleration = acceleration
        entity.distance_traveled += (entity.position - old_position).magnitude()
        entity.travel_time += dt
        
        entity.update_trail()
    
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
