import paramiko
import json

from ax.service.ax_client import ObjectiveProperties
from ax.service.scheduler import Scheduler
from utils import *

# Define functions (this will be deleted in place of actual functions)
f_1 = lambda x: x**2
f_2 = lambda x: (x - 1)**2

# Set up ax client
ax_client = AxClient2()
ax_client.create_experiment(
    name='so_test',
    parameters=[
        {
            'name': 'x',
            'type': 'range',
            'bounds': [-10.0, 10.0]
        },
    ],
    objectives={
        'f_1': ObjectiveProperties(minimize=True, threshold=5),
        'f_2': ObjectiveProperties(minimize=True, threshold=5)
    }
)

runner = DistributedRunner()
scheduler = DistributedScheduler(
    experiment=ax_client.experiment,
    runner=runner
)
scheduler.run_all_trials()

def evaluate(params):
    return {'f_1': (f_1(params['x']), 0), 'f_2': (f_2(params['x']), 0)}

while True:
    params, trial_index = ax_client.get_next_trial()
