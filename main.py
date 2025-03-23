from ax import (
    Experiment,
    FixedParameter,
    Objective,
    OptimizationConfig,
    OutcomeConstraint,
    ParameterType,
    RangeParameter,
    SearchSpace,
)
from ax.modelbridge.generation_strategy import GenerationStrategy, GenerationStep
from ax.modelbridge.registry import Models
from ax.service.scheduler import Scheduler, SchedulerOptions
from ax.service.utils.report_utils import exp_to_df
from ax.core.objective import MultiObjective, Objective
from ax.core.optimization_config import MultiObjectiveOptimizationConfig, ObjectiveThreshold

from metrics import f_1, f_2
from runner import JobRunner

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

params = [
        {'name': 'x', 'lower': -5, 'upper': 5},
        {'name': 'y', 'lower': -5, 'upper': 5}
]

f_ref_vals = [5, 5]

search_space = SearchSpace(parameters=[
    RangeParameter(
        name=param['name'],
        parameter_type=ParameterType.FLOAT,
        lower=param['lower'],
        upper=param['upper']
    )
    for param in params
])

mo = MultiObjective(objectives=[
    Objective(metric=f_1(name='f_1', lower_is_better=True)),
    Objective(metric=f_2(name='f_2', lower_is_better=True))
])

thresholds = [
        ObjectiveThreshold(metric=metric, bound=val, relative=False)
        for metric, val in zip(mo.metrics, f_ref_vals)
]

optimization_config = MultiObjectiveOptimizationConfig(
        objective=mo,
        objective_thresholds=thresholds
)

experiment = Experiment(
        name='truck_sloshing',
        search_space=search_space,
        optimization_config=optimization_config,
        runner=JobRunner()
)

generation_strategy = GenerationStrategy(
    steps=[
        GenerationStep(
            model=Models.SOBOL,
            num_trials=5,
            min_trials_observed=3,
            max_parallelism=3
        ),
        GenerationStep(
            model=Models.BOTORCH_MODULAR,
            num_trials=-1,
            max_parallelism=3
        ),
    ]
)

scheduler = Scheduler(
        experiment=experiment,
        generation_strategy=generation_strategy,
        options=SchedulerOptions(),
)

scheduler.run_n_trials(max_trials=50)

data = exp_to_df(experiment)
f_1 = np.array(data['f_1'])
f_2 = np.array(data['f_2'])

fig, ax = plt.subplots()
ax.scatter(f_1, f_2, color='blue')

ax.set_title('Pareto Frontier', fontsize='large')
ax.set_xlabel('$f_1$', fontsize='large')
ax.set_ylabel('$f_2$', fontsize='large')

ax.grid(True)

plt.show()
