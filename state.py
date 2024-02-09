import numpy as np
import math
import FeatureExtractor

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
    state['all']=np.array([0.0,0.0,0.0])
    state['slot']=0
    state['approx']=np.array([0.0,0.0,0.0,0.0])
    state['isTypeDiff']=False
    return (state)

def create2D():
    state2D={}
    state2D['time']=0
    state2D['all']=np.array([0.0,0.0]) # w3, sum
    state2D['last_res']=[0,0]
    return (state2D)

#update_get_1D_Stats(srcIP, timestamp, datagramSize, Lambda)
def update (ID1, x_cur, t_cur, Lambda=_lambda, return_mean=False, isTypeDiff=False) :
    # if (ID1=='00:14:1c:28:d6:0601:80:c2:00:00:00' and Lambda == 5) :
    #     print ('state here')
    state=dict()
    if not ID1+'_'+str(Lambda) in map1D :
        state = create()
        state['isTypeDiff']=isTypeDiff
        map1D[ID1+'_'+str(Lambda)] = state
    else :
        state = map1D[ID1+'_'+str(Lambda)]

    if state['isTypeDiff']:
        dif = t_cur - state['time']
        if dif > 0:
            x_cur = dif
        else:
            x_cur = 0
    
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

def update2D(ID1, ID2, x_cur, t_cur, meanID1ID2, Lambda=_lambda, counter=0):  
    #meanID1ID2 = update(ID1+ID2, x_cur, t_cur, Lambda, return_mean=True)
    #update(ID2, 0, t_cur, Lambda)
    lower=order(ID1,ID2)
    if lower==0 :
        update_cov(ID1+'_'+ID2, lower, meanID1ID2, x_cur, t_cur, Lambda, counter)
    else :
        update_cov(ID2+'_'+ID1, lower, meanID1ID2, x_cur, t_cur, Lambda, counter)

def update_cov(key, lower, meanID1ID2, x_cur, t_cur, Lambda=_lambda,counter=0):
    state2D = dict()
    if not key+'_'+str(Lambda) in map2D :
        #print('creating key',key+'_'+str(Lambda))
        state2D = create2D()
        map2D[key+'_'+str(Lambda)] = state2D
    else :
        state2D = map2D[key+'_'+str(Lambda)]

    #print ('key',key+'_'+str(Lambda))
    #decay = math.exp(-(t_cur - state['time'])/1e9*Lambda) # time in [ns]
    decay = math.pow(2, (-(t_cur - state2D['time'])*Lambda)) #wrong IMHO
    #decay = math.exp(-(t_cur - state['time'])*Lambda)  # time in [s]
    #print ('decay',decay)
    # Decay residules
    # if (counter==54 and Lambda == 0.01) :
    #     print ('key',key)
    #     print (state2D['all'][0],state2D['all'][1])
    state2D['all'][0] *= decay
    state2D['all'][1] *= decay
    state2D['time'] = t_cur

    # Compute and update residule
    res = (x_cur - meanID1ID2)
    resid = (res * state2D['last_res'][1-lower])
    state2D['all'][0] += 1
    state2D['all'][1]+= resid
    state2D['last_res'][lower] = res


def order(id1, id2) :
    if id1 <= id2 :
        return 0
    else :
        return 1
