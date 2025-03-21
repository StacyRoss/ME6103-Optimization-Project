import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ax.service.ax_client import AxClient, MultiObjectiveOptimizationConfig
from ax.service.scheduler import Scheduler
from ax.core.base_trial import BaseTrial
from ax.core.runner import Runner
from ax.core.trial import Trial

from firebase_admin import db

class AxClient2(AxClient):
    def get_trace2(self, optimization_config: MultiObjectiveOptimizationConfig | None = None):
        return np.array(super().get_trace(optimization_config))

    def get_pareto_points(self):
        pareto_params = self.get_pareto_optimal_parameters()

        pareto_points = []
        for param in pareto_params.values():
            pareto_points.append(
                {
                    'x': param[0]['x'],
                    'f_1': param[1][0]['f_1'],
                    'f_2': param[1][0]['f_2']
                }
            )

        return pd.DataFrame(pareto_points)

    def plot_pareto_points(self, pareto_points=None):
        if pareto_points is None:
            pareto_points = self.get_pareto_points()

        fig, ax = plt.subplots()
        ax.scatter(pareto_points['f_1'], pareto_points['f_2'], color='blue')

        ax.set_title('Pareto Frontier', fontsize='large')
        ax.set_xlabel('$f_1$', fontsize='large')
        ax.set_ylabel('$f_2$', fontsize='large')

        ax.grid(True)

class DistributedRunner(Runner):
    def run(self, trial: BaseTrial):
        if not isinstance(trial, Trial):
            raise ValueError("This runner only handles 'Trial'.")

        

        params = trial.arm.parameters
        trial_idx = trial.index
        trial_data = {
            'trial_idx': trial_idx,
            'parameters': params,
            'status': 'pending'
        }
        
        db.reference('trials').child(f'trial_{trial_idx}').set(trial_data)
        return {'trial_idx': trial_idx}

    def poll_trial_status(self, trials):
        # In this setup, assume all trials are complete after execution
        return {trial.index: "COMPLETED" for trial in trials}

class DistributedScheduler(Scheduler):
    def should_stop_early(self):
        return False
