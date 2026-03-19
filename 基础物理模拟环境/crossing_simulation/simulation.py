"""
仿真引擎模块 - 主循环和状态管理
"""
import random
from typing import List, Dict, Any, Optional, Callable
from .config import Config
from .entity import Entity, EntityManager
from .environment import CrossingEnvironment
from .social_force import SocialForceModel


class SimulationEngine:
    def __init__(self):
        self.environment = CrossingEnvironment()
        self.entity_manager = EntityManager()
        self.social_force = SocialForceModel(self.environment, self.entity_manager)
        
        self.time = 0.0
        self.frame = 0
        self.is_running = False
        self.is_paused = False
        
        self.collision_count = 0
        self.completed_count = 0
        
        self.last_spawn_time = 0.0
        
        self.on_step_complete: Optional[Callable[[Dict], None]] = None
        self.on_entity_complete: Optional[Callable[[Entity], None]] = None
    
    def initialize(self):
        self.entity_manager.initialize()
        self.time = 0.0
        self.frame = 0
        self.collision_count = 0
        self.completed_count = 0
        self.is_running = True
        self.is_paused = False
    
    def reset(self):
        self.entity_manager = EntityManager()
        self.social_force.set_entity_manager(self.entity_manager)
        self.initialize()
    
    def step(self) -> Dict[str, Any]:
        if not self.is_running or self.is_paused:
            return self._get_state()
        
        dt = Config.DT
        
        self._spawn_entities()
        
        for entity in self.entity_manager.all_entities:
            if not entity.is_active:
                continue
            
            neighbors = self.entity_manager.get_neighbors_in_vision(entity)
            
            self.social_force.update_entity(entity, neighbors, dt)
            
            collisions = self.social_force.check_collision(entity, neighbors)
            self.collision_count += collisions
            
            if entity.has_reached_target():
                entity.is_active = False
                self.completed_count += 1
                if self.on_entity_complete:
                    self.on_entity_complete(entity)
        
        self._resolve_all_collisions()
        self.entity_manager.remove_inactive()
        
        self.time += dt
        self.frame += 1
        
        if self.time >= Config.MAX_SIMULATION_TIME:
            self.is_running = False
        
        state = self._get_state()
        
        if self.on_step_complete:
            self.on_step_complete(state)
        
        return state
    
    def _spawn_entities(self):
        if self.time - self.last_spawn_time < Config.MIN_SPAWN_INTERVAL:
            return
        
        active_count = len([e for e in self.entity_manager.all_entities if e.is_active])
        if active_count >= Config.MAX_ACTIVE_ENTITIES:
            return
        
        if random.random() < Config.PEDESTRIAN_SPAWN_PROBABILITY:
            self.entity_manager.create_entity('pedestrian')
            self.last_spawn_time = self.time
        
        if random.random() < Config.BICYCLE_SPAWN_PROBABILITY:
            self.entity_manager.create_entity('bicycle')
            self.last_spawn_time = self.time
    
    def _resolve_all_collisions(self):
        entities = self.entity_manager.all_entities
        for i, entity1 in enumerate(entities):
            if not entity1.is_active:
                continue
            for entity2 in entities[i + 1:]:
                if not entity2.is_active:
                    continue
                
                distance = (entity1.position - entity2.position).magnitude()
                if distance < (entity1.radius + entity2.radius):
                    self.social_force.resolve_collision(entity1, entity2)
    
    def _get_state(self) -> Dict[str, Any]:
        return {
            'time': self.time,
            'frame': self.frame,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'collision_count': self.collision_count,
            'completed_count': self.completed_count,
            'active_count': sum(1 for e in self.entity_manager.all_entities if e.is_active),
            'entities': self.entity_manager.all_entities.copy(),
            'statistics': self.entity_manager.get_statistics()
        }
    
    def pause(self):
        self.is_paused = True
    
    def resume(self):
        self.is_paused = False
    
    def stop(self):
        self.is_running = False
    
    def get_fitness(self) -> float:
        completed = [e for e in self.entity_manager.all_entities if not e.is_active]
        
        if not completed:
            return 0.0
        
        avg_time = sum(e.travel_time for e in completed) / len(completed)
        
        collision_penalty = self.collision_count * 10.0
        
        efficiency = 1.0 / (avg_time + 0.1)
        
        fitness = efficiency - collision_penalty * 0.01
        
        return max(0, fitness)
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        completed = [e for e in self.entity_manager.all_entities if not e.is_active]
        active = [e for e in self.entity_manager.all_entities if e.is_active]
        
        return {
            'total_time': self.time,
            'total_frames': self.frame,
            'collisions': self.collision_count,
            'completed_entities': len(completed),
            'active_entities': len(active),
            'avg_travel_time': sum(e.travel_time for e in completed) / len(completed) if completed else 0,
            'avg_distance': sum(e.distance_traveled for e in completed) / len(completed) if completed else 0,
            'fitness': self.get_fitness()
        }


class SimulationRunner:
    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        self.step_callback: Optional[Callable[[Dict], None]] = None
        self.complete_callback: Optional[Callable[[Dict], None]] = None
    
    def run_single_step(self) -> Dict:
        return self.engine.step()
    
    def run_until_complete(self, max_steps: int = None) -> Dict:
        step_count = 0
        while self.engine.is_running:
            state = self.engine.step()
            step_count += 1
            
            if self.step_callback:
                self.step_callback(state)
            
            if max_steps and step_count >= max_steps:
                break
            
            if not any(e.is_active for e in self.engine.entity_manager.all_entities):
                self.engine.is_running = False
        
        final_state = self.engine._get_state()
        
        if self.complete_callback:
            self.complete_callback(final_state)
        
        return final_state
    
    def run_for_time(self, duration: float) -> List[Dict]:
        states = []
        end_time = self.engine.time + duration
        
        while self.engine.is_running and self.engine.time < end_time:
            state = self.engine.step()
            states.append(state)
            
            if self.step_callback:
                self.step_callback(state)
        
        return states
