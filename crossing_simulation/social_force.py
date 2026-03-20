"""
社会力模型模块 - 处理避让行为和运动计算
基于Helbing的社会力模型，结合180°视野限制
"""
import math
from typing import List
import numpy as np
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
    

    
    def calculate_total_force(self, entity: Entity, neighbors: List[Entity]) -> Vector2D:
        # 尝试使用NumPy向量化计算
        try:
            # 计算期望力
            desired_velocity = entity.desired_direction_np * entity.desired_speed
            desired_force = (desired_velocity - entity.velocity_np) * (entity.mass / Config.RELAXATION_TIME)
            desired_force *= Config.DESIRED_FORCE_FACTOR
            
            if not neighbors:
                return Vector2D(desired_force[0], desired_force[1])
            
            # 准备邻居数据
            neighbor_positions = np.array([n.position_np for n in neighbors], dtype=np.float32)
            neighbor_radii = np.array([n.radius for n in neighbors], dtype=np.float32)
            
            # 计算距离和方向
            diff = entity.position_np[np.newaxis, :] - neighbor_positions
            distances = np.linalg.norm(diff, axis=1)
            
            # 避免除以零
            valid_mask = distances > 1e-6
            if not np.any(valid_mask):
                return Vector2D(desired_force[0], desired_force[1])
            
            # 归一化方向
            direction = diff[valid_mask] / distances[valid_mask][:, np.newaxis]
            
            # 计算社交力
            combined_radius = entity.radius + neighbor_radii[valid_mask]
            effective_distance = distances[valid_mask] - combined_radius
            
            force_magnitude = Config.SOCIAL_FORCE_A * np.exp(-effective_distance / Config.SOCIAL_FORCE_B)
            social_forces = direction * force_magnitude[:, np.newaxis]
            
            # 总和
            total_social_force = np.sum(social_forces, axis=0) if social_forces.size > 0 else np.zeros(2, dtype=np.float32)
            
            total_force = desired_force + total_social_force
            
            return Vector2D(total_force[0], total_force[1])
        except:
            # 回退到原始实现
            return self.calculate_total_force_original(entity, neighbors)
    
    def calculate_total_force_original(self, entity: Entity, neighbors: List[Entity]) -> Vector2D:
        total_force = Vector2D(0, 0)
        
        desired_force = self.calculate_desired_force(entity)
        total_force = total_force + desired_force
        
        for neighbor in neighbors:
            social_force = self.calculate_social_force(entity, neighbor)
            total_force = total_force + social_force
        
        return total_force
    
    def update_entity(self, entity: Entity, neighbors: List[Entity], dt: float):
        # 尝试使用NumPy向量化计算
        try:
            force = self.calculate_total_force(entity, neighbors)
            
            # 转换为NumPy数组进行计算
            force_np = np.array([force.x, force.y], dtype=np.float32)
            
            acceleration = force_np / entity.mass
            
            max_acceleration = 5.0
            acc_magnitude = np.linalg.norm(acceleration)
            if acc_magnitude > max_acceleration:
                acceleration = acceleration / acc_magnitude * max_acceleration
            
            entity.velocity_np += acceleration * dt
            
            max_speed_factor = 1.5
            max_speed = entity.desired_speed * max_speed_factor
            vel_magnitude = np.linalg.norm(entity.velocity_np)
            if vel_magnitude > max_speed:
                entity.velocity_np = entity.velocity_np / vel_magnitude * max_speed
            
            old_position = entity.position_np.copy()
            new_position = entity.position_np + entity.velocity_np * dt
            
            new_position_vec = self._enforce_road_boundaries(entity, Vector2D(new_position[0], new_position[1]))
            new_position = np.array([new_position_vec.x, new_position_vec.y], dtype=np.float32)
            
            entity.position_np = new_position
            
            entity.acceleration_np = acceleration
            entity.distance_traveled += np.linalg.norm(entity.position_np - old_position)
            entity.travel_time += dt
            
            # 同步更新Vector2D对象
            entity.position = Vector2D(entity.position_np[0], entity.position_np[1])
            entity.velocity = Vector2D(entity.velocity_np[0], entity.velocity_np[1])
            entity.acceleration = Vector2D(entity.acceleration_np[0], entity.acceleration_np[1])
            
            entity.update_trail()
        except:
            # 回退到原始实现
            force = self.calculate_total_force_original(entity, neighbors)
            
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
            
            # 同步更新NumPy数组
            entity.position_np = np.array([entity.position.x, entity.position.y], dtype=np.float32)
            entity.velocity_np = np.array([entity.velocity.x, entity.velocity.y], dtype=np.float32)
            entity.acceleration_np = np.array([entity.acceleration.x, entity.acceleration.y], dtype=np.float32)
            
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
