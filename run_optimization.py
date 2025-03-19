from ax.plot.pareto_frontier import plot_pareto_frontier
from ax.plot.pareto_utils import compute_posterior_pareto_frontier
from ax.service.ax_client import AxClient
from ax.service.utils.instantiation import ObjectiveProperties

import plotly.io as pio

from objectives_constraints import *

n_trials = 10 # number of trials for Bayesian optimization
n_points = 5 # number of points to show on the Pareto frontier

ax_client = AxClient()

ax_client.create_experiment(
    name='SPH_optimization',
    parameters=[
        {
            'name': 'D_pt',
            'type': 'range',
            'bounds': [25, 35],
        },
        {
            'name': 's_d',
            'type': 'range',
            'bounds': [29.96, 33.96],
        },
    ],
    objectives={
        'F_slosh': ObjectiveProperties(minimize=True),
        'V_baffle': ObjectiveProperties(minimize=True),
    },
    is_test=True
)

def evaluate(parameters):
    D_pt = parameters['D_pt']
    s_d = parameters['s_d']

    F_slosh = get_F_slosh(D_pt, s_d)
    V_baffle = get_V_baffle(D_pt, s_d)

    return {'F_slosh': F_slosh, 'V_baffle': V_baffle}

for _ in range(n_trials):
    parameters, trial_idx = ax_client.get_next_trial()
    ax_client.complete_trial(trial_index=trial_idx, raw_data=evaluate(parameters))

objectives = ax_client.experiment.optimization_config.objective.objectives
frontier = compute_posterior_pareto_frontier(
    experiment=ax_client.experiment,
    data=ax_client.experiment.fetch_data(),
    primary_objective=objectives[1].metric,
    secondary_objective=objectives[0].metric,
    absolute_metrics=['F_slosh', 'V_baffle'],
    num_points=n_points,
)
pareto_plot = plot_pareto_frontier(frontier, CI_level=0.95)
fig = pareto_plot[0]
pio.show(fig)
