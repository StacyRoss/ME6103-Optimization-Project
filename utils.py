import pandas as pd

from collections import defaultdict

from ax.core.runner import Runner
from ax.core.base_trial import TrialStatus
from ax.core.metric import Metric, MetricFetchE
from ax.core.data import Data
from ax.utils.common.result import Ok, Err

class JobRunner(Runner):
    def run(self, trial):
        job_id = FirebaseClient.schedule_job(trial)
        return {'job_id': job_id}

    def poll_trial_status(self, trials):
        statuses = defaultdict(set)
        for trial in trials:
            status = FirebaseClient.get_job_status(trial)
            statuses[status].add(trial.index)
        return statuses

class FirebaseClient:
    @staticmethod
    def schedule_job(trial):
        ### SEND TRIAL PARAMETERS AND TrialStatus.STAGED TO DATABASE
        computer = 0

        return [trial.index, computer]
    
    @staticmethod
    def get_job_status(trial):
        ### GET JOB STATUS FROM DATABASE
        return TrialStatus.COMPLETED

    @staticmethod
    def get_f_1(trial):
        if FirebaseClient.get_job_status(trial) == TrialStatus.COMPLETED:
            ### GET f_1 FROM DATABASE
            params = trial.arm.parameters
            return (params['x'] - 1)**2 + (params['y'] - 1)**2

    @staticmethod
    def get_f_2(trial):
        params = trial.arm.parameters
        return params['x']**2 + params['y']**2

class f_1(Metric):
    def fetch_trial_data(self, trial, **kwargs):
        try:
            df_dict = {
                    'trial_index': trial.index,
                    'metric_name': self.name,
                    'arm_name': trial.arm.name,
                    'mean': FirebaseClient.get_f_1(trial),
                    'sem': None
            }
            
            return Ok(value=Data(df=pd.DataFrame.from_records([df_dict])))

        except Exception as e:
            return Err(MetricFetchE(message=f'Failed to fetch {self.name}', exception=e))

class f_2(Metric):
    def fetch_trial_data(self, trial, **kwargs):
        try:
            df_dict = {
                    'trial_index': trial.index,
                    'metric_name': self.name,
                    'arm_name': trial.arm.name,
                    'mean': FirebaseClient.get_f_2(trial),
                    'sem': None
            }
            
            return Ok(value=Data(df=pd.DataFrame.from_records([df_dict])))

        except Exception as e:
            return Err(MetricFetchE(message=f'Failed to fetch {self.name}', exception=e))
