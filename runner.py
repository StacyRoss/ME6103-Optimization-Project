from collections import defaultdict
from ax.core.runner import Runner
from ax.core.base_trial import TrialStatus

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
