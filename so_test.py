import numpy as np
import pandas as pd

from ax.service.ax_client import AxClient, ObjectiveProperties

n_trials = 25
batch_size = 1

f = lambda x, y: 2*(x - 1)**2 - 1.05*(x - 1)**4 + (x - 1)**6/6 + (x - 1)*(y - 1) + (y - 1)**2

ax_client = AxClient()

ax_client.create_experiment(
        name='so_test',
        parameters=[
            {
                'name': 'x',
                'type': 'range',
                'bounds': [-5.0, 5.0]
            },
            {
                'name': 'y',
                'type': 'range',
                'bounds': [-5.0, 5.0]
            }
        ],
        objectives={'f': ObjectiveProperties(minimize=True)}
)

def evaluate(params):
    return {'f': (f(params['x'], params['y']), 0)}

data = []
for _ in range(n_trials):
    params, trial_index = ax_client.get_next_trial()

    

    ax_client.complete_trial(trial_index=trial_index, raw_data=evaluate(params))

best_params, _ = ax_client.get_best_parameters()
print(f'(x, y) = ({best_params["x"]:.3g}, {best_params["y"]:.3g})')
