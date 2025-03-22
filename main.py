from ax import (
    ChoiceParameter,
    ComparisonOp,
    Experiment,
    FixedParameter,
    Metric,
    Objective,
    OptimizationConfig,
    OrderConstraint,
    OutcomeConstraint,
    ParameterType,
    RangeParameter,
    SearchSpace,
    SumConstraint,
)
from ax.modelbridge.generation_strategy import GenerationStrategy, GenerationStep
from ax.modelbridge.registry import Models
from ax.service.scheduler import Scheduler, SchedulerOptions

from runner import JobRunner
from metrics import f_1

params = [
        {'name': 'x', 'lower': -5, 'upper': 5},
        {'name': 'y', 'lower': -5, 'upper': 5}
]

search_space = SearchSpace(parameters=[
    RangeParameter(
        name=param['name'],
        parameter_type=ParameterType.FLOAT,
        lower=param['lower'],
        upper=param['upper']
    )
    for param in params
])

optimization_config = OptimizationConfig(
        objective=Objective(metric=f_1(name='f_1'), minimize=True)
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

scheduler.run_n_trials(max_trials=10)
