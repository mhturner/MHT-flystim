#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:20:02 2018

@author: mhturner
"""
import numpy as np
from visprotocol.protocol import clandinin_protocol
import socket
from flystim.trajectory import RectangleTrajectory, Trajectory


class BaseProtocol(clandinin_protocol.BaseProtocol):
    def __init__(self):
        super().__init__() #call the parent class init method first
        if socket.gethostname() == "MHT-laptop": # (laptop, for dev.)
            self.send_ttl = False
        else:
            self.send_ttl = True
            

# %%
class CheckerboardWhiteNoise(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID  = 'RandomGrid'
        
        start_seed = int(np.random.choice(range(int(1e6))))
        
        
        distribution_data = {'name':'Gaussian',
                                 'args':[],
                                 'kwargs':{'rand_mean':self.protocol_parameters['rand_mean'],
                                           'rand_stdev':self.protocol_parameters['rand_stdev']}}

        self.epoch_parameters = {'name':stimulus_ID,
                            'theta_period':self.protocol_parameters['checker_width'],
                            'phi_period':self.protocol_parameters['checker_width'],
                            'start_seed':start_seed,
                            'update_rate':self.protocol_parameters['update_rate'],
                            'distribution_data':distribution_data}
        self.convenience_parameters = {}

    def getParameterDefaults(self):
        self.protocol_parameters = {'checker_width':5.0,
                       'update_rate':0.5,
                       'rand_mean': 0.5,
                       'rand_stdev':0.15}
    
    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'CheckerboardWhiteNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}
        
# %%
class DriftingSquareGrating(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()

    def getEpochParameters(self):
        stimulus_ID  = 'RotatingBars'
        
        currentAngle = self.selectParametersFromLists(self.protocol_parameters['angle'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])
        
        self.epoch_parameters = {'name':stimulus_ID,
                            'period':self.protocol_parameters['period'],
                            'duty_cycle':0.5,
                            'rate':self.protocol_parameters['rate'],
                            'color':self.protocol_parameters['color'],
                            'background':self.protocol_parameters['background'],
                            'angle':currentAngle}
        
        self.convenience_parameters = {}

    def getParameterDefaults(self):
        self.protocol_parameters = {'period':20.0,
                       'rate':20.0,
                       'color':1.0,
                       'background':0.0,
                       'angle':[0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'DriftingSquareGrating',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':4.0,
              'tail_time':0.5,
              'idle_color':0.5}
        
# %%
class ExpandingMovingSquare(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        
        currentWidth = self.selectParametersFromLists(self.protocol_parameters['width'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])
        
        centerX = self.protocol_parameters['center'][0]
        centerY = self.protocol_parameters['center'][1]
        angle = self.protocol_parameters['angle']
        speed = self.protocol_parameters['speed']
        stim_time = self.run_parameters['stim_time']
        distance_to_travel = speed * stim_time
        
        startX = (0,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
        endX = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
        startY = (0,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
        endY = (stim_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)

        trajectory = RectangleTrajectory(x = [startX, endX],
                                              y = [startY, endY],
                                              angle = angle,
                                              h = currentWidth,
                                              w = currentWidth,
                                              color = self.protocol_parameters['color']).to_dict()   

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'currentWidth': currentWidth,
                                  'center':self.protocol_parameters['center'],
                                  'angle':self.protocol_parameters['angle'],
                                  'speed':self.protocol_parameters['speed'],
                                  'color':self.protocol_parameters['color']}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width':[2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0],
                       'color':0.0,
                       'center': [55.0, 120.0],
                       'speed':60.0,
                       'angle': 0.0,
                       'randomize_order':True}

    
    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'ExpandingMovingSquare',
              'num_epochs':70,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
        
# %%
class FlickeringPatch(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        stim_time = self.run_parameters['stim_time']
        
        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        trajectory_sample_rate = 100 # Hz
        nPoints = trajectory_sample_rate * stim_time
        time_points = np.linspace(0, stim_time, nPoints)
        color_values = np.sin(time_points * 2 * np.pi * current_temporal_frequency)
        color_trajectory = list(zip(time_points,color_values))

        trajectory = RectangleTrajectory(x = self.protocol_parameters['center'][0],
                                              y = self.protocol_parameters['center'][1],
                                              angle = 0,
                                              h = self.protocol_parameters['height'],
                                              w = self.protocol_parameters['width'],
                                              color = color_trajectory).to_dict()   

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'current_temporal_frequency':current_temporal_frequency,
                                  'center':self.protocol_parameters['center'],
                                  'width':self.protocol_parameters['width'],
                                  'height':self.protocol_parameters['height']}

    def getParameterDefaults(self):
        self.protocol_parameters = {'height':5.0,
                       'width':5.0,
                       'center': [55.0, 120.0],
                       'temporal_frequency': [1.0, 2.0, 4.0, 8.0, 16.0, 32.0],
                       'randomize_order':True}

# %%
class LoomingPatch(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        stim_time = self.run_parameters['stim_time']
        start_size = self.protocol_parameters['start_size']
        end_size = self.protocol_parameters['end_size']
        
        rv_ratio = self.protocol_parameters['rv_ratio'] #msec
        trajectory_code = [0, 1, 2] #0 = expanding, 1 = reversed (shrinking), 2 = randomized

        current_rv_ratio, current_trajectory_code = self.selectParametersFromLists((rv_ratio, trajectory_code),
                                                                                             all_combinations = True, 
                                                                                             randomize_order = self.protocol_parameters['randomize_order'])
        
        current_rv_ratio = current_rv_ratio / 1e3 #msec -> sec
    
        time_steps = np.arange(0,stim_time-0.001,0.001) #time steps of trajectory
        # calculate angular size at each time step for this rv ratio
        angular_size = 2 * np.rad2deg(np.arctan(current_rv_ratio * (1 /(stim_time - time_steps))))
        
        # shift curve vertically so it starts at start_size
        min_size = angular_size[0]
        size_adjust = min_size - start_size
        angular_size = angular_size - size_adjust
        # Cap the curve at end_size and have it just hang there
        max_size_ind = np.where(angular_size > end_size)[0][0]
        angular_size[max_size_ind:] = end_size

        # Get the correct trajectory type
        if current_trajectory_code == 0:
            current_trajectory_type = 'expanding'
            angular_size = angular_size # initial trajectory
            
        elif current_trajectory_code == 1:
            current_trajectory_type = 'contracting'
            angular_size = np.flip(angular_size, axis = 0) # reverse in time
            
        elif current_trajectory_code == 2:
            current_trajectory_type = 'randomized'
            angular_size = np.random.permutation(angular_size) #randomize in time

        # time-modulated trajectories
        h = Trajectory(list(zip(time_steps,angular_size)), kind = 'previous')
        w = Trajectory(list(zip(time_steps,angular_size)), kind = 'previous')

        # constant trajectories:
        centerX = Trajectory(self.protocol_parameters['center'][0])
        centerY = Trajectory(self.protocol_parameters['center'][1])
        color = Trajectory(self.protocol_parameters['color'])
        angle = Trajectory(0)
        trajectory = {'x': centerX.to_dict(), 'y': centerY.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}
        

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}

        self.convenience_parameters = {'center':self.protocol_parameters['center'],
                                  'current_rv_ratio':current_rv_ratio,
                                  'color':self.protocol_parameters['color'],
                                  'time_steps':time_steps,
                                  'angular_size':angular_size,
                                  'start_size':start_size,
                                  'end_size':end_size,
                                  'randomize_order':self.protocol_parameters['randomize_order'],
                                  'current_trajectory_type':current_trajectory_type}

    def getParameterDefaults(self):
        self.protocol_parameters = {'color':0.0,
                       'center': [55.0, 120],
                       'start_size': 2.5,
                       'end_size': 80.0,
                       'rv_ratio':[5.0, 10.0, 20.0, 40.0, 80.0],
                       'randomize_order': True}
    
    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'LoomingPatch',
              'num_epochs':75,
              'pre_time':0.5,
              'stim_time':1.0,
              'tail_time':0.5,
              'idle_color':0.5}

# %%
class MovingRectangle(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
            
        currentAngle = self.selectParametersFromLists(self.protocol_parameters['angle'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])
        
        centerX = self.protocol_parameters['center'][0]
        centerY = self.protocol_parameters['center'][1]
        speed = self.protocol_parameters['speed']
        stim_time = self.run_parameters['stim_time']
        distance_to_travel = speed * stim_time
        
        startX = (0,centerX - np.cos(np.radians(currentAngle)) * distance_to_travel/2)
        endX = (stim_time, centerX + np.cos(np.radians(currentAngle)) * distance_to_travel/2)
        startY = (0,centerY - np.sin(np.radians(currentAngle)) * distance_to_travel/2)
        endY = (stim_time, centerY + np.sin(np.radians(currentAngle)) * distance_to_travel/2)

        trajectory = RectangleTrajectory(x=[startX, endX],
                                              y=[startY, endY],
                                              angle=currentAngle,
                                              h = self.protocol_parameters['height'],
                                              w = self.protocol_parameters['width'],
                                              color = self.protocol_parameters['color']).to_dict()   

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'currentAngle': currentAngle,
                                  'center':self.protocol_parameters['center'],
                                  'speed':self.protocol_parameters['speed'],
                                  'color':self.protocol_parameters['color'],
                                  'height':self.protocol_parameters['height'],
                                  'width':self.protocol_parameters['width']}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [55.0, 120],
                       'speed':60.0,
                       'angle': [0.0, 45.0, 90.0, 135.0, 180.0, 225.0, 270.0, 315.0],
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingRectangle',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}

# %%
class MovingSquareMapping(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        az_loc = self.protocol_parameters['azimuth_locations']
        el_loc = self.protocol_parameters['elevation_locations']
        
        if type(az_loc) is not list:
            az_loc = [az_loc]
        if type(el_loc) is not list:
            el_loc = [el_loc]
        
        location_list = np.concatenate((az_loc, el_loc))
        movement_axis_list = np.concatenate((np.ones(len(az_loc)), 2*np.ones(len(el_loc))))
        
        current_search_axis_code, current_location = self.selectParametersFromLists((movement_axis_list, location_list),
                                                                                              all_combinations = False,
                                                                                              randomize_order = self.protocol_parameters['randomize_order'])
        
        if current_search_axis_code == 1:
            current_search_axis = 'azimuth'
        elif current_search_axis_code == 2:
            current_search_axis = 'elevation'

        #where does the square begin? Should be just off screen...
        startingAzimuth = 20.0; startingElevation = 40.0;
        speed = self.protocol_parameters['speed']
        stim_time = self.run_parameters['stim_time']
        
        if current_search_axis == 'elevation': #move along x (azimuth)
            startX = (0,startingAzimuth)
            endX = (stim_time,startingAzimuth + speed * stim_time)    
            startY = (0,current_location)
            endY = (stim_time,current_location)    
        elif current_search_axis == 'azimuth':  #move along y (elevation)
            startX = (0,current_location)
            endX = (stim_time,current_location)
            startY = (0,startingElevation)
            endY = (stim_time,startingElevation + speed * stim_time)   

        trajectory = RectangleTrajectory(x = [startX, endX],
                                             y = [startY, endY],
                                             angle=0,
                                             h = self.protocol_parameters['square_width'],
                                             w = self.protocol_parameters['square_width'],
                                             color = self.protocol_parameters['color']).to_dict()
        
        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory': trajectory}

        self.convenience_parameters = {'speed':speed,
                                  'current_search_axis':current_search_axis,
                                  'current_location':current_location,
                                  'randomize_order':self.protocol_parameters['randomize_order'],
                                  'square_width':self.protocol_parameters['square_width'],
                                  'color':self.protocol_parameters['color']}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation_locations': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0], # 100...140
                       'azimuth_locations': [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0], #30...80
                       'speed':60.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'MovingSquareMapping',
              'num_epochs':100,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}
        
# %%
class SequentialOrRandomMotion(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
    
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'

        stim_time = self.run_parameters['stim_time']
        no_steps = self.protocol_parameters['no_steps']
        
        time_steps = np.linspace(0,stim_time,no_steps)
        x_steps = np.linspace(self.protocol_parameters['azimuth_boundaries'][0],self.protocol_parameters['azimuth_boundaries'][1],no_steps)
        y_steps = np.linspace(self.protocol_parameters['elevation'],self.protocol_parameters['elevation'],no_steps)
        
        #switch back and forth between sequential and random
        randomized_order = bool(np.mod(self.num_epochs_completed,2))
        if randomized_order:
            x_steps = np.random.permutation(x_steps)
        
        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        # constant trajectories:
        w = Trajectory(self.protocol_parameters['square_width'])
        h = Trajectory(self.protocol_parameters['square_width'])
        angle = Trajectory(0)
        color = Trajectory(self.protocol_parameters['color'])
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'square_width':self.protocol_parameters['square_width'],
                                  'angle':0,
                                  'color':self.protocol_parameters['color'],
                                  'elevation':self.protocol_parameters['elevation'],
                                  'azimuth_boundaries':self.protocol_parameters['azimuth_boundaries'],
                                  'no_steps':self.protocol_parameters['no_steps'],
                                  'randomized_order':randomized_order,
                                  'x_steps':x_steps}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation': 120.0,
                       'azimuth_boundaries': [50.0, 70.0],
                       'no_steps': 8}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SequentialOrRandomMotion',
              'num_epochs':20,
              'pre_time':0.5,
              'stim_time':0.5,
              'tail_time':1.0,
              'idle_color':0.5}
        
# %%
class SineTrajectoryPatch(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        
        current_temporal_frequency = self.selectParametersFromLists(self.protocol_parameters['temporal_frequency'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])

        centerX = self.protocol_parameters['center'][0]
        centerY = self.protocol_parameters['center'][1]
        amplitude = self.protocol_parameters['amplitude']
        movement_axis = self.protocol_parameters['movement_axis']
        
        stim_time = self.run_parameters['stim_time']
        
        time_steps = np.arange(0,stim_time,0.005) #time steps of trajectory
        distance_along_movement_axis = amplitude * np.sin(time_steps * 2 * np.pi * current_temporal_frequency)

        x_steps = centerX + np.cos(np.radians(movement_axis)) * distance_along_movement_axis
        y_steps = centerY + np.sin(np.radians(movement_axis)) * distance_along_movement_axis

        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous')
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        
        # constant trajectories:
        color = Trajectory(self.protocol_parameters['color'])
        w = Trajectory(self.protocol_parameters['width']) 
        h = Trajectory(self.protocol_parameters['height']) 
        angle = Trajectory(movement_axis)
        
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}
        

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        
        self.convenience_parameters = {'width': self.protocol_parameters['width'],
                                  'height':self.protocol_parameters['height'],
                                  'color':self.protocol_parameters['color'],
                                  'center':self.protocol_parameters['center'],
                                  'amplitude':self.protocol_parameters['amplitude'],
                                  'temporal_frequency':self.protocol_parameters['temporal_frequency'],
                                  'current_temporal_frequency':current_temporal_frequency,
                                  'movement_axis':self.protocol_parameters['movement_axis'],
                                  'randomize_order':self.protocol_parameters['randomize_order'],
                                  'time_steps':time_steps,
                                  'x_steps':x_steps,
                                  'y_steps':y_steps
                                  }

        
    def getParameterDefaults(self):
        self.protocol_parameters = {'width':5.0,
                       'height':5.0,
                       'color':0.0,
                       'center': [55.0, 120],
                       'amplitude': 20, #deg, half of total travel distance
                       'temporal_frequency': [1, 2, 4, 6, 8], #Hz
                       'movement_axis': 0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SineTrajectoryPatch',
              'num_epochs':40,
              'pre_time':0.5,
              'stim_time':2.0,
              'tail_time':0.5,
              'idle_color':0.5}

# %%
class SparseNoise(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        
    def getEpochParameters(self):
        stimulus_ID = 'RandomGrid'
        
        start_seed = int(np.random.choice(range(int(1e6))))
        
        distribution_data = {'name':'SparseBinary',
                                 'args':[],
                                 'kwargs':{'rand_min':self.protocol_parameters['rand_min'],
                                           'rand_max':self.protocol_parameters['rand_max'],
                                           'sparseness':self.protocol_parameters['sparseness']}}
        
        self.epoch_parameters = {'name': stimulus_ID,
                            'theta_period': self.protocol_parameters['checker_width'],
                            'phi_period': self.protocol_parameters['checker_width'],
                            'start_seed': start_seed, 
                            'update_rate': self.protocol_parameters['update_rate'],
                            'distribution_data': distribution_data}
        
        self.convenience_parameters = {'rand_min':self.protocol_parameters['rand_min'],
                                  'rand_max':self.protocol_parameters['rand_max'],
                                  'sparseness':self.protocol_parameters['sparseness'],
                                  'distribution_name':'SparseBinary'}

    def getParameterDefaults(self):
        self.protocol_parameters = {'checker_width':5.0,
                               'update_rate':8.0,
                               'rand_min': 0.0,
                               'rand_max':1.0,
                               'sparseness':0.95}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SparseNoise',
              'num_epochs':10,
              'pre_time':1.0,
              'stim_time':30.0,
              'tail_time':1.0,
              'idle_color':0.5}
        
# %%     
class SpeedTuningSquare(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
            
        currentSpeed = self.selectParametersFromLists(self.protocol_parameters['speed'],
                                                                randomize_order = self.protocol_parameters['randomize_order'])
        
        centerX = self.protocol_parameters['center'][0]
        centerY = self.protocol_parameters['center'][1]
        angle = self.protocol_parameters['angle']
        width = self.protocol_parameters['width']
        stim_time = self.run_parameters['stim_time']
        
        distance_to_travel = 120 # deg
        #travel time in sec, at start of stim_time. Remaining stim_time spot just hangs at the end of the trajectory
        travel_time = distance_to_travel / currentSpeed  
        
        startX = (0,centerX - np.cos(np.radians(angle)) * distance_to_travel/2)
        startY = (0,centerY - np.sin(np.radians(angle)) * distance_to_travel/2)
        endX = (travel_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
        endY = (travel_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
        
        if  travel_time < stim_time:
            hangX = (stim_time, centerX + np.cos(np.radians(angle)) * distance_to_travel/2)
            hangY = (stim_time, centerY + np.sin(np.radians(angle)) * distance_to_travel/2)
            x = [startX, endX, hangX]
            y = [startY, endY, hangY]
        elif travel_time >= stim_time:
            print('Warning: stim_time is too short to show whole trajectory')
            x = [startX, endX]
            y = [startY, endY]

        trajectory = RectangleTrajectory(x = x,
                                         y = y,
                                         angle = angle,
                                         h = width,
                                         w = width,
                                         color = self.protocol_parameters['color']).to_dict()   

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'width': width,
                                  'center':self.protocol_parameters['center'],
                                  'angle':angle,
                                  'currentSpeed':currentSpeed,
                                  'color':self.protocol_parameters['color']}

    def getParameterDefaults(self):
        self.protocol_parameters = {'width': 5.0,
                       'color':0.0,
                       'center': [55.0, 120.0],
                       'speed':[20.0, 40.0, 60.0, 80.0, 100.0, 120.0, 140.0, 160.0, 180.0, 200.0],
                       'angle': 0.0,
                       'randomize_order':True}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'SpeedTuningSquare',
              'num_epochs':50,
              'pre_time':0.5,
              'stim_time':5.0,
              'tail_time':0.5,
              'idle_color':0.5}
        
# %%
class StationaryMapping(BaseProtocol):
    def __init__(self):
        super().__init__()
        
        self.getRunParameterDefaults()
        self.getParameterDefaults()
        
    def getEpochParameters(self):
        stimulus_ID = 'MovingPatch'
        az_loc = self.protocol_parameters['azimuth_locations']
        el_loc = self.protocol_parameters['elevation_locations']
        
        if type(az_loc) is not list:
            az_loc = [az_loc]
        if type(el_loc) is not list:
            el_loc = [el_loc]
        

        stim_time = self.run_parameters['stim_time'] #sec
        flash_duration = self.protocol_parameters['flash_duration'] #sec
        
        time_steps = np.arange(0,stim_time,flash_duration)
        no_steps = len(time_steps)
        x_steps = np.random.choice(az_loc, size = no_steps, replace=True)
        y_steps = np.random.choice(el_loc, size = no_steps, replace=True)
 
        
        # time-modulated trajectories
        x = Trajectory(list(zip(time_steps,x_steps)), kind = 'previous') #note interp kind is previous
        y = Trajectory(list(zip(time_steps,y_steps)), kind = 'previous')
        # constant trajectories:
        w = Trajectory(self.protocol_parameters['square_width'])
        h = Trajectory(self.protocol_parameters['square_width'])
        angle = Trajectory(0)
        color = Trajectory(self.protocol_parameters['color'])
        trajectory = {'x': x.to_dict(), 'y': y.to_dict(), 'w': w.to_dict(), 'h': h.to_dict(),
            'angle': angle.to_dict(), 'color': color.to_dict()}

        self.epoch_parameters = {'name':stimulus_ID,
                            'background':self.run_parameters['idle_color'],
                            'trajectory':trajectory}
        self.convenience_parameters = {'square_width':self.protocol_parameters['square_width'],
                                  'angle':0,
                                  'color':self.protocol_parameters['color'],
                                  'elevation_locations':el_loc,
                                  'azimuth_locations':az_loc,
                                  'flash_duration':self.protocol_parameters['flash_duration'],
                                  'x_steps':x_steps,
                                  'y_steps':y_steps,
                                  'time_steps':time_steps}

    def getParameterDefaults(self):
        self.protocol_parameters = {'square_width':5.0,
                       'color':0.0,
                       'elevation_locations': [100.0, 105.0, 110.0, 115.0, 120.0, 125.0, 130.0, 135.0, 140.0], # 100...140
                       'azimuth_locations': [30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 80.0], #30...80
                       'flash_duration':0.25}

    def getRunParameterDefaults(self):
        self.run_parameters = {'protocol_ID':'StationaryMapping',
              'num_epochs':6,
              'pre_time':2.0,
              'stim_time':100.0,
              'tail_time':2.0,
              'idle_color':0.5}
