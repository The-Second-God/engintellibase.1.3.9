"""
避让距离管理器模块 - 追踪首次相遇位置和计算避让距离
"""
from dataclasses import dataclass
from typing import Dict, Tuple, Optional, TYPE_CHECKING
from .config import Config

if TYPE_CHECKING:
    from .entity import Entity, Vector2D


@dataclass
class EncounterRecord:
    entity1_id: int
    entity2_id: int
    entity1_initial_position: 'Vector2D'
    entity2_initial_position: 'Vector2D'
    initial_distance: float
    avoidance_distance: float


class AvoidanceDistanceManager:
    def __init__(self):
        self._encounter_records: Dict[Tuple[int, int], EncounterRecord] = {}
        self._entity_positions: Dict[int, 'Vector2D'] = {}
    
    def _make_pair_key(self, id1: int, id2: int) -> Tuple[int, int]:
        return (min(id1, id2), max(id1, id2))
    
    def _calculate_avoidance_distance(self, initial_distance: float) -> float:
        avoidance_dist = initial_distance * Config.AVOIDANCE_DISTANCE_FACTOR
        avoidance_dist = max(Config.MIN_AVOIDANCE_DISTANCE, avoidance_dist)
        avoidance_dist = min(Config.MAX_AVOIDANCE_DISTANCE, avoidance_dist)
        return avoidance_dist
    
    def check_and_record_encounter(self, entity1: 'Entity', entity2: 'Entity') -> Optional[EncounterRecord]:
        from .entity import Vector2D
        
        pair_key = self._make_pair_key(entity1.id, entity2.id)
        
        if pair_key in self._encounter_records:
            return self._encounter_records[pair_key]
        
        distance = (entity1.position - entity2.position).magnitude()
        
        record = EncounterRecord(
            entity1_id=entity1.id,
            entity2_id=entity2.id,
            entity1_initial_position=Vector2D(entity1.position.x, entity1.position.y),
            entity2_initial_position=Vector2D(entity2.position.x, entity2.position.y),
            initial_distance=distance,
            avoidance_distance=self._calculate_avoidance_distance(distance)
        )
        
        self._encounter_records[pair_key] = record
        return record
    
    def get_encounter_record(self, entity1_id: int, entity2_id: int) -> Optional[EncounterRecord]:
        pair_key = self._make_pair_key(entity1_id, entity2_id)
        return self._encounter_records.get(pair_key)
    
    def get_avoidance_distance(self, entity1_id: int, entity2_id: int) -> float:
        record = self.get_encounter_record(entity1_id, entity2_id)
        if record:
            return record.avoidance_distance
        return Config.MIN_AVOIDANCE_DISTANCE
    
    def is_within_avoidance_distance(self, entity1: 'Entity', entity2: 'Entity') -> bool:
        current_distance = (entity1.position - entity2.position).magnitude()
        avoidance_distance = self.get_avoidance_distance(entity1.id, entity2.id)
        return current_distance < avoidance_distance
    
    def should_trigger_avoidance(self, entity1: 'Entity', entity2: 'Entity') -> Tuple[bool, float]:
        pair_key = self._make_pair_key(entity1.id, entity2.id)
        
        if pair_key not in self._encounter_records:
            return False, 0.0
        
        current_distance = (entity1.position - entity2.position).magnitude()
        avoidance_distance = self._encounter_records[pair_key].avoidance_distance
        
        if current_distance < avoidance_distance:
            return True, avoidance_distance - current_distance
        
        return False, 0.0
    
    def remove_entity_records(self, entity_id: int):
        keys_to_remove = [
            key for key in self._encounter_records.keys()
            if entity_id in key
        ]
        for key in keys_to_remove:
            del self._encounter_records[key]
        
        if entity_id in self._entity_positions:
            del self._entity_positions[entity_id]
    
    def get_all_encounters_for_entity(self, entity_id: int) -> list:
        encounters = []
        for key, record in self._encounter_records.items():
            if entity_id in key:
                encounters.append(record)
        return encounters
    
    def get_statistics(self) -> dict:
        return {
            'total_encounters': len(self._encounter_records),
            'active_encounters': len([
                r for r in self._encounter_records.values()
                if r.avoidance_distance > Config.MIN_AVOIDANCE_DISTANCE
            ])
        }
    
    def clear(self):
        self._encounter_records.clear()
        self._entity_positions.clear()
