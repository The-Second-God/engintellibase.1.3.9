"""
可视化模块 - 使用matplotlib进行仿真可视化
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
from matplotlib.collections import LineCollection
from typing import Dict, List, Optional
import numpy as np

from .config import Config
from .entity import Entity, Direction
from .simulation import SimulationEngine


class Visualizer:
    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        
        self.fig, self.ax = plt.subplots(figsize=(10, 10))
        self.fig.canvas.manager.set_window_title('Crossing Simulation')
        
        self.entity_patches: Dict[int, patches.Circle] = {}
        self.trail_lines: Dict[int, LineCollection] = {}
        self.vision_cones: Dict[int, patches.Wedge] = {}
        
        self.info_text = None
        self.stats_text = None
        
        self._setup_plot()
    
    def _setup_plot(self):
        self.ax.set_xlim(-2, Config.CROSSING_WIDTH + 2)
        self.ax.set_ylim(-2, Config.CROSSING_HEIGHT + 2)
        self.ax.set_aspect('equal')
        self.ax.set_facecolor(Config.COLOR_BACKGROUND)
        
        self._draw_environment()
        
        self.info_text = self.ax.text(
            0.02, 0.98, '', transform=self.ax.transAxes,
            fontsize=10, verticalalignment='top',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8)
        )
        
        self.stats_text = self.ax.text(
            0.98, 0.98, '', transform=self.ax.transAxes,
            fontsize=9, verticalalignment='top', horizontalalignment='right',
            fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
        )
        
        self.ax.set_xlabel('X (meters)')
        self.ax.set_ylabel('Y (meters)')
        self.ax.set_title('Crossing Simulation - Pedestrian & Bicycle Traffic')
    
    def _draw_environment(self):
        center_x = Config.CROSSING_WIDTH / 2
        center_y = Config.CROSSING_HEIGHT / 2
        half_road = Config.ROAD_WIDTH / 2
        
        road_h = patches.Rectangle(
            (0, center_y - half_road),
            Config.CROSSING_WIDTH,
            Config.ROAD_WIDTH,
            linewidth=1,
            edgecolor='gray',
            facecolor=Config.COLOR_ROAD,
            alpha=0.5
        )
        self.ax.add_patch(road_h)
        
        road_v = patches.Rectangle(
            (center_x - half_road, 0),
            Config.ROAD_WIDTH,
            Config.CROSSING_HEIGHT,
            linewidth=1,
            edgecolor='gray',
            facecolor=Config.COLOR_ROAD,
            alpha=0.5
        )
        self.ax.add_patch(road_v)
        
        crossing_width = 0.4
        stripe_length = 0.6
        stripe_gap = 0.4
        
        for i in range(int(Config.CROSSING_WIDTH / (stripe_length + stripe_gap)) + 1):
            x = i * (stripe_length + stripe_gap)
            stripe = patches.Rectangle(
                (x, center_y - half_road + 0.2),
                stripe_length,
                crossing_width,
                facecolor='white',
                edgecolor='none',
                alpha=0.8
            )
            self.ax.add_patch(stripe)
            
            stripe2 = patches.Rectangle(
                (x, center_y + half_road - 0.2 - crossing_width),
                stripe_length,
                crossing_width,
                facecolor='white',
                edgecolor='none',
                alpha=0.8
            )
            self.ax.add_patch(stripe2)
        
        for i in range(int(Config.CROSSING_HEIGHT / (stripe_length + stripe_gap)) + 1):
            y = i * (stripe_length + stripe_gap)
            stripe = patches.Rectangle(
                (center_x - half_road + 0.2, y),
                crossing_width,
                stripe_length,
                facecolor='white',
                edgecolor='none',
                alpha=0.8
            )
            self.ax.add_patch(stripe)
            
            stripe2 = patches.Rectangle(
                (center_x + half_road - 0.2 - crossing_width, y),
                crossing_width,
                stripe_length,
                facecolor='white',
                edgecolor='none',
                alpha=0.8
            )
            self.ax.add_patch(stripe2)
        
        corner_size = 2.0
        corners = [
            (0, 0),
            (Config.CROSSING_WIDTH - corner_size, 0),
            (0, Config.CROSSING_HEIGHT - corner_size),
            (Config.CROSSING_WIDTH - corner_size, Config.CROSSING_HEIGHT - corner_size)
        ]
        
        for cx, cy in corners:
            corner = patches.Rectangle(
                (cx, cy), corner_size, corner_size,
                linewidth=1,
                edgecolor='gray',
                facecolor='#90EE90',
                alpha=0.3
            )
            self.ax.add_patch(corner)
    
    def _create_entity_patch(self, entity: Entity) -> patches.Circle:
        color = Config.COLOR_PEDESTRIAN if entity.type == 'pedestrian' else Config.COLOR_BICYCLE
        
        circle = patches.Circle(
            (entity.position.x, entity.position.y),
            entity.radius,
            facecolor=color,
            edgecolor='black',
            linewidth=1,
            alpha=0.8
        )
        self.ax.add_patch(circle)
        return circle
    
    def _create_vision_cone(self, entity: Entity) -> Optional[patches.Wedge]:
        if not Config.SHOW_VISION_CONE:
            return None
        
        forward = entity.get_forward_direction()
        angle = forward.angle()
        
        wedge = patches.Wedge(
            (entity.position.x, entity.position.y),
            Config.VISION_RANGE,
            angle - Config.VISION_ANGLE / 2,
            angle + Config.VISION_ANGLE / 2,
            facecolor='yellow',
            edgecolor='orange',
            alpha=0.2
        )
        self.ax.add_patch(wedge)
        return wedge
    
    def _update_trail(self, entity: Entity):
        if not Config.SHOW_TRAILS or not entity.trail:
            return
        
        if len(entity.trail) < 2:
            return
        
        points = np.array(entity.trail)
        segments = np.array([[points[i], points[i + 1]] for i in range(len(points) - 1)])
        
        color = Config.COLOR_PEDESTRIAN if entity.type == 'pedestrian' else Config.COLOR_BICYCLE
        
        if entity.id in self.trail_lines:
            self.trail_lines[entity.id].set_segments(segments)
        else:
            lc = LineCollection(segments, colors=[(*color, 0.3)], linewidths=1)
            self.ax.add_collection(lc)
            self.trail_lines[entity.id] = lc
    
    def update(self, state: Dict):
        active_entities = [e for e in state['entities'] if e.is_active]
        
        current_ids = set(e.id for e in active_entities)
        existing_ids = set(self.entity_patches.keys())
        
        for eid in existing_ids - current_ids:
            if eid in self.entity_patches:
                self.entity_patches[eid].remove()
                del self.entity_patches[eid]
            if eid in self.trail_lines:
                self.trail_lines[eid].remove()
                del self.trail_lines[eid]
            if eid in self.vision_cones:
                if self.vision_cones[eid]:
                    self.vision_cones[eid].remove()
                del self.vision_cones[eid]
        
        for entity in active_entities:
            if entity.id not in self.entity_patches:
                self.entity_patches[entity.id] = self._create_entity_patch(entity)
                if Config.SHOW_VISION_CONE:
                    self.vision_cones[entity.id] = self._create_vision_cone(entity)
            
            self.entity_patches[entity.id].center = (entity.position.x, entity.position.y)
            
            if Config.SHOW_VISION_CONE and entity.id in self.vision_cones:
                cone = self.vision_cones[entity.id]
                if cone:
                    cone.set_center((entity.position.x, entity.position.y))
                    forward = entity.get_forward_direction()
                    angle = forward.angle()
                    cone.set_theta1(angle - Config.VISION_ANGLE / 2)
                    cone.set_theta2(angle + Config.VISION_ANGLE / 2)
            
            self._update_trail(entity)
        
        info_str = (
            f"Time: {state['time']:.2f}s\n"
            f"Frame: {state['frame']}\n"
            f"Status: {'Running' if state['is_running'] else 'Stopped'}"
        )
        self.info_text.set_text(info_str)
        
        stats = state['statistics']
        stats_str = (
            f"Active: {stats['active_entities']}\n"
            f"Completed: {stats['completed_count']}\n"
            f"Total Spawned: {stats['total_spawned']}\n"
            f"Collisions: {state['collision_count']}\n"
            f"Avg Time: {stats['avg_travel_time']:.2f}s"
        )
        self.stats_text.set_text(stats_str)
        
        self.fig.canvas.draw_idle()
    
    def show_static(self, state: Dict):
        self.update(state)
        plt.show()
    
    def close(self):
        plt.close(self.fig)


class AnimatedVisualizer:
    def __init__(self, engine: SimulationEngine):
        self.engine = engine
        self.visualizer = Visualizer(engine)
        self.animation = None
        self.is_running = False
    
    def _init_animation(self):
        return []
    
    def _update_animation(self, frame):
        if not self.engine.is_running:
            self.is_running = False
            return []
        
        state = self.engine.step()
        self.visualizer.update(state)
        return []
    
    def run(self, interval: int = None):
        if interval is None:
            interval = int(1000 / Config.FPS)
        
        self.engine.initialize()
        self.is_running = True
        
        self.animation = FuncAnimation(
            self.visualizer.fig,
            self._update_animation,
            init_func=self._init_animation,
            interval=interval,
            blit=False,
            cache_frame_data=False
        )
        
        plt.show()
    
    def stop(self):
        self.is_running = False
        if self.animation:
            self.animation.event_source.stop()
    
    def close(self):
        self.stop()
        self.visualizer.close()
