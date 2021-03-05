import math
from functools import lru_cache

import numpy as np
import shapely.geometry as geom

from Car_Model import CarState, Car
from bezier_util import dist


class Track():
    def __init__(self, track_center_x, track_center_y, track_width):
        self.center_x = track_center_x
        self.center_y = track_center_y
        self.width = track_width
        self.boundary1_x, self.boundary1_y = zip(*self._generate_right_boundary())
        self.boundary2_x, self.boundary2_y = zip(*self._generate_left_boundary())
        self.center_coords = np.array([*zip(self.center_x, self.center_y)])
        self.line = geom.LineString(self.center_coords)
        
        
    def _generate_right_boundary(self):
        for i in range(len(self.center_x)):
            if i == len(self.center_y) - 1: break
            dy = self.center_y[i+1] - self.center_y[i]
            dx = self.center_x[i+1] - self.center_x[i]
            dist = math.sqrt(dy ** 2 + dx ** 2)
            arr = np.array([dx * math.cos(90) + dy * math.sin(90), -dx*math.sin(90) + dy*math.cos(90)])
            arr = arr * (self.width/2)/dist
            yield self.center_x[i] + arr[0], self.center_y[i]+arr[1]

    def _generate_left_boundary(self):
        for i in range(len(self.center_x)):
            if i == len(self.center_y) - 1: break
            dy = self.center_y[i+1] - self.center_y[i]
            dx = self.center_x[i+1] - self.center_x[i]
            dist = math.sqrt(dy ** 2 + dx ** 2)
            arr = np.array([dx * math.cos(90) - dy * math.sin(90), dx*math.sin(90) + dy*math.cos(90)])
            arr = arr * (self.width/2)/dist
            yield self.center_x[i] + arr[0], self.center_y[i]+arr[1]

    def find_pos_index(self, init_px, currx, curry, point_horizon=400):
        min_dist = np.inf
        min_idx = 999999
        for i in range(init_px, init_px + point_horizon):
            idx = i % len(self.center_x)
            d = dist(self.center_x[idx], self.center_y[idx], currx, curry)
            if d < min_dist:
                min_dist = d
                min_idx = i
        return min_idx
    
    def place_car(self, x, y, dx, dy, d2x, d2y, heading, car_profile, optimizer_parameters):
        tpx  = self.find_pos_index(0, x, y, point_horizon=len(self.center_x))
        state = CarState(x, y, dx, dy, d2x, d2y, tpx, heading)
        car = Car(car_profile, state, self, optimizer_parameters)
        return car

    @lru_cache(maxsize=500)
    def distance_to_center(self, x, y):
        point = geom.Point(x, y)
        return point.distance(self.line)
