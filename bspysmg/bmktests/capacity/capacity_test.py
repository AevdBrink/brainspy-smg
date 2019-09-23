#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 16:32:25 2018
This script generates all binary assignments of N elements.
@author: hruiz and ualegre
"""

from bspysmg.bmktests.capacity.vc_dimension_test import VCDimensionTest

from bspyalgo.utils.io import load_configs, save_configs
from bspyalgo.algorithm_manager import get_algorithm


import numpy as np


class CapacityTest():

    def __init__(self, configs):
        self.configs = configs
        self.current_dimension = configs['from_dimension']
        self.threshold = self.__calculate_threshold()
        self.vcdimension_test = VCDimensionTest(algorithm=configs['algorithm'], output_dir=configs['output_dir'], surrogate_model_name=configs['surrogate_model_name'])

    def run_test(self):
        results = {}
        while True:
            self.__init_test()
            opportunity = 0
            not_found = np.array([])
            while True:
                test_data = self.vcdimension_test.run_test(binary_labels=not_found)
                not_found = test_data['gate'].loc[test_data['found'] == False]  # noqa: E712
                opportunity += 1
                if (not_found.size == 0) or (opportunity >= self.configs['max_opportunities']):
                    break
            results[str(self.current_dimension)] = self.vcdimension_test.close_test(self.threshold, self.current_dimension, self.configs['show_plot'])
            if not results[str(self.current_dimension)] or not self.next_vcdimension():
                self.vcdimension_test.writer.save()
                self.results = results
                return results

    def __init_test(self):
        print('==== VC Dimension %d ====' % self.current_dimension)
        inputs = self.generate_test_inputs(self.current_dimension)
        binary_labels = self.__generate_binary_target(self.current_dimension).tolist()
        self.threshold = self.__calculate_threshold()
        self.vcdimension_test.init_data(inputs, binary_labels, self.threshold)

    def __calculate_threshold(self):
        return 1 - (self.configs['threshold_parameter'] / self.current_dimension)

    def next_vcdimension(self):
        if self.current_dimension + 1 > self.configs['to_dimension']:
            return False
        else:
            self.current_dimension += 1
            self.__calculate_threshold()
            return True

    # @todo change generation of inputs to differetn vc dimensions

    def generate_test_inputs(self, vc_dim):
        # @todo create a function that automatically generates non-linear inputs
        try:
            if vc_dim == 4:
                return [[-0.7, -0.7, 0.7, 0.7], [0.7, -0.7, 0.7, -0.7]]
            elif vc_dim == 5:
                return [[-0.7, -0.7, 0.7, 0.7, -0.35],
                        [0.7, -0.7, 0.7, -0.7, 0.0]]
            elif vc_dim == 6:
                return [[-0.7, -0.7, 0.7, 0.7, -0.35, 0.35],
                        [0.7, -0.7, 0.7, -0.7, 0.0, 0.0]]
            elif vc_dim == 7:
                return [[-0.7, -0.7, 0.7, 0.7, -0.35, 0.35, 0.0],
                        [0.7, -0.7, 0.7, -0.7, 0.0, 0.0, 1.0]]
            elif vc_dim == 8:
                return [[-0.7, -0.7, 0.7, 0.7, -0.35, 0.35, 0.0, 0.0],
                        [0.7, -0.7, 0.7, -0.7, 0.0, 0.0, 1.0, -1.0]]
            else:
                raise VCDimensionException()
        except VCDimensionException:
            print(
                'Dimension Exception occurred. The selected VC Dimension is %d Please insert a value between ' %
                vc_dim)

    def __generate_binary_target(self, target_dim):
        # length of list, i.e. number of binary targets
        binary_target_no = 2**target_dim
        assignments = []
        list_buf = []

        # construct assignments per element i
        print('===' * target_dim)
        print('ALL BINARY LABELS:')
        level = int((binary_target_no / 2))
        while level >= 1:
            list_buf = []
            buf0 = [0] * level
            buf1 = [1] * level
            while len(list_buf) < binary_target_no:
                list_buf += (buf0 + buf1)
            assignments.append(list_buf)
            level = int(level / 2)

        binary_targets = np.array(assignments).T
        print(binary_targets)
        print('===' * target_dim)
        return binary_targets


class VCDimensionException(Exception):
    """Exception: It does not exist an implementation of such VC Dimension."""
    pass


if __name__ == '__main__':
    from bspyalgo.utils.io import save_configs
    # platform = {}
    # platform['modality'] = 'simulation_nn'
    # # platform['path2NN'] = r'D:\UTWENTE\PROJECTS\DARWIN\Data\Mark\MSE_n_d10w90_200ep_lr1e-3_b1024_b1b2_0.90.75.pt'
    # platform['path2NN'] = r'/home/unai/Documents/3-programming/boron-doped-silicon-chip-simulation/checkpoint3000_02-07-23h47m.pt'
    # # platform['path2NN'] = r'/home/hruiz/Documents/PROJECTS/DARWIN/Data_Darwin/Devices/Marks_Data/April_2019/MSE_n_d10w90_200ep_lr1e-3_b1024_b1b2_0.90.75.pt'
    # platform['amplification'] = 10.
    # ga_configs = {}
    # ga_configs['partition'] = [5] * 5  # Partitions of population
    # # Voltage range of CVs in V
    # ga_configs['generange'] = [[-1.2, 0.6], [-1.2, 0.6],
    #                            [-1.2, 0.6], [-0.7, 0.3], [-0.7, 0.3], [1, 1]]
    # ga_configs['genes'] = len(ga_configs['generange'])    # Nr of genes
    # # Nr of individuals in population
    # ga_configs['genomes'] = sum(ga_configs['partition'])
    # ga_configs['mutationrate'] = 0.1

    # # Parameters to define target waveforms
    # ga_configs['lengths'] = [80]     # Length of data in the waveform
    # # Length of ramping from one value to the next
    # ga_configs['slopes'] = [0]  # Parameters to define task
    # ga_configs['fitness'] = 'corrsig_fit'  # 'corr_fit'
    # ga_configs['platform'] = platform  # Dictionary containing all variables for the platform

    capacity_test_configs = {}
    capacity_test_configs['output_dir'] = r'/home/unai/Documents/3-programming/boron-doped-silicon-chip-simulation/'
    capacity_test_configs['surrogate_model_name'] = 'checkpoint3000_02-07-23h47m'
    capacity_test_configs['from_dimension'] = 4
    capacity_test_configs['to_dimension'] = 5
    capacity_test_configs['max_opportunities'] = 3
    capacity_test_configs['threshold_parameter'] = 0.5
    capacity_test_configs['show_plot'] = False
    capacity_test_configs['algorithm'] = get_algorithm('genetic', 'configs/ga/ga_configs_template.json')

    save_configs(capacity_test_configs, 'capacity_test_template.json')

   # test = CapacityTest(capacity_test_configs)
   # test.run_test()