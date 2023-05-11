import numpy as np
import math

time_constant = 10 # [seconds]
_lambda = 1/time_constant
frames = 20
forget_tc = 3
forget_frames = frames * forget_tc
step_decay = math.exp(-(1/frames))
ns_per_frame = time_constant/ frames * 1e9
print('step_decay',step_decay)
print ('ns_per_frame', ns_per_frame)

map1D = dict()
map2D = dict()

# class stats:
#     def __init__(self):  # timestamp is creation time
#         self.state={}
#         self.state['time']=0
#         self.state['slot']=0
#         self.state['all']=np.array([0,0,0])
#         self.state['approx']=np.array([0,0,0,0])
#         #print(state['time'])

def create() :
    # I TRY NOT TO STORE LAMBDA IN THE STATE
    state={}
    state['time']=0
    state['all']=np.array([0,0,0])
    state['slot']=0
    state['approx']=np.array([0,0,0,0])
    return (state)

def create2D():
    state2D={}
    state2D['time']=0
    state2D['all']=np.array([0,0]) # w3, sum
    state2D['last_res']=[0,0]
    return (state2D)

#update_get_1D_Stats(srcIP, timestamp, datagramSize, Lambda)
def update (ID1, x_cur, t_cur, Lambda=_lambda, return_mean=False) :
    state=dict()
    if not ID1+str(Lambda) in map1D :
        state = create()
        map1D[ID1+str(Lambda)] = state
    else :
        state = map1D[ID1+str(Lambda)]
    #print((t_cur - state['time']) /1e9)
    #decay = math.exp(-(t_cur - state['time'])/1e9*Lambda) # time in [ns]
    decay = math.pow(2, (-(t_cur - state['time'])*Lambda)) #wrong IMHO
    #decay = math.exp(-(t_cur - state['time'])*Lambda)  # time in [s]
    #print ('decay',decay)
    state['time']=t_cur
    state['all']=np.multiply(state['all'],decay)
    #state['all'][0]=state['all'][0]+1
    w = state['all'][0]+1
    state['all'][0] = w
    #state['all'][1]=state['all'][1]+x_cur
    tot_count=state['all'][1]+x_cur
    state['all'][1]=tot_count
    state['all'][2]=state['all'][2]+x_cur*x_cur
    if return_mean :
        return tot_count / w

#update_get_1D2D_Stats(srcIP, dstIP,timestamp,datagramSize,Lambda)

def update2D(ID1, ID2, x_cur, t_cur, Lambda=_lambda):  
    meanID1 = update(ID1, x_cur, t_cur, Lambda, return_mean=True)
    update(ID2, 0, t_cur, Lambda)
    lower=order(ID1,ID2)
    if lower==0 :
        update_cov(ID1+ID2+Lambda, lower, meanID1, ID1, ID2, x_cur, t_cur, Lambda=_lambda)
    else :
        update_cov(ID2+ID1+Lambda, lower, meanID1, ID1, ID2, x_cur, t_cur, Lambda=_lambda)

def update_cov(key, lower, meanID1, ID1, ID2, x_cur, t_cur, Lambda=_lambda):  
    state2D = dict()
    if not key+str(Lambda) in map2D :
        state2D = create2D()
        map2D[key+str(Lambda)] = state2D
    else :
        #decay = math.exp(-(t_cur - state['time'])/1e9*Lambda) # time in [ns]
        decay = math.pow(2, (-(t_cur - state2D['time'])*Lambda)) #wrong IMHO
        #decay = math.exp(-(t_cur - state['time'])*Lambda)  # time in [s]

        # Decay residules
        self.processDecay(t,inc)

        factor = 1
        # check for decay cf3
        timeDiffs_cf3 = t - self.lastTimestamp_cf3
        if timeDiffs_cf3 > 0:
            self.CF3 *= factor
            self.w3 *= factor
            self.lastTimestamp_cf3 = t
            self.lastRes[micro_inc_indx] *= factor
        state2D['all'][0] *= decay
        state2D['all'][1] *= decay
        state2D['time'] = t_cur

        


        # Compute and update residule
        res = (x_cur - meanID1)
        resid = (x_cur -res * state2D['last_res'][1-lower])
        state2D['all'][0] += 1
        state2D['all'][1]+= resid
        state2D['last_res'][lower] = res
