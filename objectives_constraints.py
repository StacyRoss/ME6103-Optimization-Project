import numpy as np

D_b = 69.92 # in
t_b = 0.25 # in

# get_V_baffle = lambda D_pt, s_d: (np.pi*D_b**2 - D_b**2*np.arcsin(np.sqrt(D_b**2 - 4*s_d**2)/D_b) - np.pi*D_pt**2)*t_b/4

### FAKE
get_V_baffle = lambda D_pt, s_d: D_pt**2 + s_d**2
get_F_slosh = lambda D_pt, s_d: (D_pt - 1)**2 + (s_d - 1)**2
