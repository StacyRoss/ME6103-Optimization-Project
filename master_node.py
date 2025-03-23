import sys
import time

from firebase_admin import credentials, initialize_app, db
from ax.service.ax_client import AxClient, ObjectiveProperties
from ax.exceptions.generation_strategy import MaxParallelismReachedException

from master_node_utils import *

F_slosh_max = 0
V_baffle_max = 0

clear_database = True # SET TO FALSE FOR REAL OPTIMIZATION RUNS

# Initialize firebase access
cred = credentials.Certificate('credentials.json')
initialize_app(cred, {
    'databaseURL': 'https://truck-sloshing-default-rtdb.firebaseio.com/'
})

# Clear database
if clear_database:
    user_input = input('Clear database? [y/n] ')
    
    if user_input == 'y':
        ref = db.reference('/')
        ref.delete()
        print('Database cleared')
    else:
        print('Database was not cleared')
        user_input = input('Proceed with optimization? [y/n] ')

        if user_input != 'y':
            sys.exit()

# Initialize ax client
ax_client = AxClient()

ax_client.create_experiment(
    name="truck sloshing",
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
    objectives={
        'F_slosh': ObjectiveProperties(minimize=True, threshold=F_slosh_max),
        'V_baffle': ObjectiveProperties(minimize=True, threshold=V_baffle_max)
    }
)

print('Ax client initialized')

# Run optimization
while True:
    find_instance_of(ax_client, 'available', assign_new_job)
    print('Scheduled available trials')
    
    find_instance_of(ax_client, 'completed', receive_completed_job)
    print('Received completed jobs')
    
    time.sleep(5)
    
    find_instance_of(ax_client, 'staged', abandon_staged_job)
    print('Abandoned remaining staged jobs')
