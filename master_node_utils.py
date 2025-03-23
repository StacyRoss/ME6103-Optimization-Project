from firebase_admin import db
from ax.exceptions.generation_strategy import MaxParallelismReachedException

def find_instance_of(ax_client, status, action):
    ref = db.reference('/workers')

    try:
        workers = ref.get()
    except:
        print('Timeout: could not receive workers')
        return

    if workers == None:
        print('No active workers')
        return

    for worker_id, worker_info in workers.items():
        print(worker_id)
        print(worker_info)
        if worker_info['status'] == status:
            action(ax_client, worker_id)

def assign_new_job(ax_client, worker_id):
    # Get next trial, check for max parallelism
    try:
        params, trial_index = ax_client.get_next_trial()
    except MaxParallelismReachedException:
        print('Max parallelism achieved')
        return
    
    # Asssign trial, cancel trial if server times out
    trial_ref = db.reference(f'/trials/trial_{trial_index}')
    worker_ref = db.reference(f'/workers/{worker_id}')
    try:
        trial_ref.set(params)
        worker_ref.set({'status': 'staged', 'trial index': trial_index})
    except:
        ax_client.mark_trial_as_abandoned(trial_index)
        print(f'Trial {trial_index} abandoned due to timeout')
        return

    print(f'Trial {trial_index} successfully assigned')

def receive_completed_job(ax_client, worker_id):
    # Get trial index
    worker_ref = db.reference(f'/workers/{worker_id}')
    try:
        trial_index = worker_ref.get()['trial index']
    except:
        print('Timeout: could not receive trial index')
        return
    trial_ref = db.reference(f'/trials/trial_{trial_index}')

    # Get function values
    try:    
        F_slosh = trial_ref.get()['F_slosh']
        V_baffle = trial_ref.get()['V_baffle']
        
        worker_ref.set({'status': 'available', 'trial index': -1})
    except:
        print('Timeout: could not get function values')
        return

    # Complete trial
    ax_client.complete_trial(trial_index=trial_index, raw_data={
        'F_slosh': (F_slosh, 0),
        'V_baffle': (V_baffle, 0)
    })

    print(f'Trial {trial_index} successfully received')


def abandon_staged_job(ax_client, worker_id):
    worker_ref = db.reference(f'/workers/{worker_id}')
    try:
        trial_index = worker_ref.get()['trial index']
    except:
        print('Timeout: could not receive trial index')
        return
    
    ax_client.mark_trial_as_abandoned(trial_index)
    print(f'Trial {trial_index} successfully abandoned')
