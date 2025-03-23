import uuid
import time

from firebase_admin import credentials, initialize_app, db

sleep_time = 1

F_slosh = lambda x, y: x**2 + y**2
V_baffle = lambda x, y: (x - 1)**2 + (y - 1)**2

# Create/access unique computer ID
try:
    with open('worker_id.txt', 'r') as file:
        worker_id = file.read()
except FileNotFoundError:
    worker_id = str(uuid.uuid4())
    with open('worker_id.txt', 'w') as file:
        file.write(worker_id)

# Initialize firebase access
cred = credentials.Certificate('credentials.json')
initialize_app(cred, {'databaseURL': 'https://truck-sloshing-default-rtdb.firebaseio.com/'})

# Initialize worker node
worker_ref = db.reference(f'/workers/{worker_id}')
worker_ref.set({'status': 'available', 'trial index': -1})

# Listen for staged trial
while True:
    try:
        status = worker_ref.get()['status']
    except:
        print('Timeout: could not receive worker status')
        time.sleep(sleep_time)
        continue

    if status == 'staged':
        # Get trial to run
        try:
            trial_index = worker_ref.get()['trial index']
        except:
            print('Timeout: could not receive trial index')
            time.sleep(sleep_time)
            continue
        trial_ref = db.reference(f'/trials/trial_{trial_index}')

        try:
            x = trial_ref.get()['x']
            y = trial_ref.get()['y']
        except:
            print('Timeout: could not receive parameters')
            time.sleep(sleep_time)
            continue

        print(f'Trial {trial_index} successfully received')

        # Run trial
        F_slosh_val = F_slosh(x, y)
        V_baffle_val = V_baffle(x, y)
        
        # Save trial data
        try:
            trial_ref.update({
                'F_slosh': F_slosh_val,
                'V_baffle': V_baffle_val
            })
            worker_ref.update({'status': 'completed', trial_index: -1})
        except:
            print('Timeout: could not save trial data')
            time.sleep(sleep_time)
            continue

        print(f'Trial {trial_index} successfully executed')
    else:
        print('No trial received')

    time.sleep(sleep_time)
