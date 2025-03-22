import pandas as pd

from ax.core.metric import Metric, MetricFetchE
from ax.core.data import Data
from ax.utils.common.result import Ok, Err

from runner import FirebaseClient

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
