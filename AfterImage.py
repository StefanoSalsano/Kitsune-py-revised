import math
import numpy as np
import state
import sys


class incStat:
    def __init__(self, Lambda, ID, init_time=0, isTypeDiff=False):  # timestamp is creation time
        self.ID = 'jitter'+ID if isTypeDiff else ID
        self.CF1 = 0  # linear sum
        self.CF2 = 0  # sum of squares
        self.w = 1e-20  # weight
        self.isTypeDiff = isTypeDiff
        self.Lambda = Lambda  # Decay Factor
        self.lastTimestamp = init_time
        self.cur_mean = np.nan
        self.cur_var = np.nan
        self.cur_std = np.nan
        self.covs = [] # a list of incStat_covs (references) with relate to this incStat
        self.time_value = []
        #TODO-delete self.state = state.create()

    def insert(self, v, t=0):  # v is a scalar, t is v's arrival the timestamp
        if self.isTypeDiff:
            dif = t - self.lastTimestamp
            if dif > 0:
                v = dif
            else:
                v = 0
            #print('isTypeDiff, dif',dif)

        # includes process decay
        #TODO-delete state.update(self.state, v, t, self.Lambda)
        # if (self.ID=='00:14:1c:28:d6:0601:80:c2:00:00:00' and self.Lambda == 5) :
        #     print('inside insert, w:',self.w)
        self.processDecay(t)

        # update with v
        self.CF1 += v
        self.CF2 += math.pow(v, 2)
        self.w += 1
        # if abs(self.w - state.map1D[self.ID+'_'+str(self.Lambda)]['all'][0]) > 0.0000001 :
        #     print ('ID',self.ID,'Lambda',self.Lambda,'compare w not ok',self.w, state.map1D[self.ID+'_'+str(self.Lambda)]['all'][0] )
        # if abs(self.CF1/self.w - state.map1D[self.ID+'_'+str(self.Lambda)]['all'][1]/state.map1D[self.ID+'_'+str(self.Lambda)]['all'][0]) > 0.0000001 :
        #     print('compare mean not ok',self.ID,self.CF1/self.w, state.map1D[self.ID+'_'+str(self.Lambda)]['all'][1]/state.map1D[self.ID+'_'+str(self.Lambda)]['all'][0])
        # if abs(self.CF2/self.w - state.map1D[self.ID+'_'+str(self.Lambda)]['all'][2]/state.map1D[self.ID+'_'+str(self.Lambda)]['all'][0]) > 0.0000001 :
        #     print('compare sum of squares not ok',self.ID,self.CF1/self.w, state.map1D[self.ID+'_'+str(self.Lambda)]['all'][2]/state.map1D[self.ID+'_'+str(self.Lambda)]['all'][2])
        self.cur_mean = np.nan  # force recalculation if called
        self.cur_var = np.nan
        self.cur_std = np.nan

        #DEBUG
        # if (self.ID == '192.168.2.101192.168.2.110' and self.Lambda==0.01) or (self.ID == '192.168.2.110192.168.2.101' and self.Lambda==0.01):
        #     #print ('>>>>>>> key',self.ID,'v',v,'mean',self.CF1/self.w )
        #     pass


        # update covs (if any)
        for cov in self.covs:
            #pass #CORRECT
            cov.update_cov(self.ID, v, t, dadove='for') #WRONG
            #TODO-delete state.update2D(cov.state2D,v,t,self.Lambda)

    def processDecay(self, timestamp):
        factor=1
        # check for decay
        timeDiff = timestamp - self.lastTimestamp
        if timeDiff > 0:
            factor = math.pow(2, (-self.Lambda * timeDiff)) #wrong IMHO
            #factor = math.exp(-(timeDiff)*self.Lambda) 
            self.CF1 = self.CF1 * factor
            self.CF2 = self.CF2 * factor
            self.w = self.w * factor
            self.lastTimestamp = timestamp
        #print ('factor',factor)
        return factor

    def weight(self):
        return self.w

    def mean(self):
        if math.isnan(self.cur_mean):  # calculate it only once when necessary
            self.cur_mean = self.CF1 / self.w
        return self.cur_mean

    def var(self):
        if math.isnan(self.cur_var):  # calculate it only once when necessary
            self.cur_var = abs(self.CF2 / self.w - math.pow(self.mean(), 2))
        return self.cur_var

    def std(self):
        if math.isnan(self.cur_std):  # calculate it only once when necessary
            self.cur_std = math.sqrt(self.var())
        return self.cur_std

    def cov(self,ID2):
        for cov in self.covs:
            if cov.incStats[0].ID == ID2 or cov.incStats[1].ID == ID2 :
                return cov.cov()
        return [np.nan]

    def pcc(self,ID2):
        for cov in self.covs:
            if cov.incStats[0].ID == ID2 or cov.incStats[1].ID == ID2:
                return cov.pcc()
        return [np.nan]

    def cov_pcc(self,ID2):
        for cov in self.covs:
            if cov.incStats[0].ID == ID2 or cov.incStats[1].ID == ID2:
                return cov.get_stats1()
        return [np.nan]*2

    def radius(self, other_incStats):  # the radius of a set of incStats
        A = self.var()**2
        for incS in other_incStats:
            A += incS.var()**2
        return math.sqrt(A)

    def magnitude(self, other_incStats):  # the magnitude of a set of incStats
        A = math.pow(self.mean(), 2)
        for incS in other_incStats:
            A += math.pow(incS.mean(), 2)
        return math.sqrt(A)

    #calculates and pulls all stats on this stream
    def allstats_1D(self, for2D=False):
        self.cur_mean = self.CF1 / self.w
        if for2D:
            return [self.w, self.cur_mean, self.std()]
        else:
            self.cur_var = abs(self.CF2 / self.w - math.pow(self.cur_mean, 2))
            return [self.w, self.cur_mean, self.cur_var]

    #calculates and pulls all stats on this stream, and stats shared with the indicated stream
    def allstats_2D(self, ID2):
        stats1D = self.allstats_1D()
        # Find cov component
        stats2D = [np.nan] * 4
        for cov in self.covs:
            if cov.incStats[0].ID == ID2 or cov.incStats[1].ID == ID2:
                stats2D = cov.get_stats2()
                break
        return stats1D + stats2D

    def getHeaders_1D(self, suffix=True):
        if self.ID is None:
            s0=""
        else:
            s0 = "_0"
        if suffix:
            s0 = "_"+self.ID
        headers = ["weight"+s0, "mean"+s0, "std"+s0]
        return headers

    def getHeaders_2D(self, ID2, suffix=True):
        hdrs1D = self.getHeaders_1D(suffix)
        if self.ID is None:
            s0=""
            s1=""
        else:
            s0 = "_0"
            s1 = "_1"
        if suffix:
            s0 = "_"+self.ID
            s1 = "_" + ID2
        hdrs2D = ["radius_" + s0 + "_" + s1, "magnitude_" + s0 + "_" + s1, "covariance_" + s0 + "_" + s1,
                   "pcc_" + s0 + "_" + s1]
        return hdrs1D+hdrs2D


#like incStat, but maintains stats between two streams
class incStat_cov:
    def __init__(self, incS1, incS2, init_time = 0):
        # store references to the streams' incStats
        self.incStats = [incS1,incS2]
        self.lastRes = [0.0,0.0]
        # init extrapolators
        #self.EXs = [extrapolator(),extrapolator()]

        # init sum product residuals
        self.CF3 = 0 # sum of residule products (A-uA)(B-uB)
        self.w3 = 1e-20
        self.lastTimestamp_cf3 = init_time
        self.onlyonce = True
        self.onlyonce2 = True
        self.onlyonce3 = True
        self.onlyonce4 = True
        self.onlyonce5 = True
        self.onlyonce6 = True
        self.onlyonce7 = True
        self.error_decay_state =1.0
        self.incstate = -1

    #other_incS_decay is the decay factor of the other incstat
    # ID: the stream ID which produced (v,t)
    def update_cov(self, ID, v, t, dadove=''):  # it is assumes that incStat "ID" has ALREADY been updated with (t,v) [this si performed automatically in method incStat.insert()]
        # find incStat
        if ID == self.incStats[0].ID:
            inc = 0
        elif ID == self.incStats[1].ID:
            inc = 1
        else:
            print("update_cov ID error")
            return ## error

        other_decay = 1
        my_timeDiff = t - self.incStats[not(inc)].lastTimestamp
        if my_timeDiff > 0:
            other_decay = math.pow(2, (-self.incStats[not(inc)].Lambda * my_timeDiff)) #wrong IMHO
            self.lastRes[not(inc)] *= other_decay
            if inc == 0 and dadove == 'for':
            #if dadove == 'for':
                self.error_decay_state = other_decay

        # Decay other incStat
        self.incStats[not(inc)].processDecay(t)


        # Decay residules
        this_decay = self.processDecay(t,inc)

        # Update extrapolator for current stream
        #self.EXs[inc].insert(t,v)

        # Extrapolate other stream
        #v_other = self.EXs[not(inc)].predict(t)

        #print ('self.incStats[0].ID',self.incStats[0].ID,'self.incStats[1].ID',self.incStats[1].ID,'XX ID',ID)
        # Compute and update residule
        #DEBUG
#        if (ID == '192.168.2.101192.168.2.110' and self.incStats[not(inc)].Lambda==0.01) or (ID == '192.168.2.110192.168.2.101' and self.incStats[not(inc)].Lambda==0.01) :
        # if (ID == '192.168.2.1192.168.2.115' and self.incStats[not(inc)].Lambda==0.01) or (ID == '192.168.2.115192.168.2.1' and self.incStats[not(inc)].Lambda==0.01) :
        #     print ('ID is:', ID, 'my_timeDiff', my_timeDiff )
        #     print (self.lastRes[not(inc)])


        res = (v - self.incStats[inc].mean()) 
        # if abs(self.lastRes[not(inc)]-4.676641776745301) < 0.0000000001 :
        #     if self.onlyonce :
        #         self.onlyonce = False
        #         print ('keypoint CF3 #56', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.999690819812596
        #         self.CF3 /= 0.9999873709742889
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        #     #res *= 0.999690819812596
        #     #res /= 0.9999873709742889
        # if abs(self.lastRes[not(inc)]-3.4991155660073865) < 0.0000000001 :
        #     if self.onlyonce2 :
        #         self.onlyonce2 = False
        #         print ('keypoint CF3 #94', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.992973623941272
        #         self.CF3 /= 0.9999881394200008
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]-2.7913050131624315) < 0.0000000001 :
        #     if self.onlyonce3 :
        #         self.onlyonce3 = False
        #         print ('keypoint CF3 #153', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9929641391225846
        #         self.CF3 /= 0.999987822126216
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]-2.318939913099542) < 0.0000000001 :
        #     if self.onlyonce4 :
        #         self.onlyonce4 = False
        #         print ('keypoint CF3 #195', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9930545045718324
        #         self.CF3 /= 0.9999886401494598
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]-1.9811834800823276) < 0.0000000001 :
        #     if self.onlyonce5 :
        #         self.onlyonce5 = False
        #         print ('keypoint CF3 #232', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9930291890762589
        #         self.CF3 /= 0.9999337299652477
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]-1.727914760401055) < 0.0000000001 :
        #     if self.onlyonce6 :
        #         self.onlyonce6 = False
        #         print ('keypoint CF3 #270', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9930512289145069
        #         self.CF3 /= 0.9999843980038601
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]-1.5307653518358477) < 0.0000000001 :
        #     if self.onlyonce7 :
        #         self.onlyonce7 = False
        #         print ('keypoint CF3 #296', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9930423078905233
        #         self.CF3 /= 0.9999736613410078
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay

        #DEBUG
        # if abs(self.lastRes[not(inc)]/1.4186533805667382e-14-1.0) < 0.00000001 :
        #     if self.onlyonce7 :
        #         self.onlyonce7 = False
        #         print ('keypoint CF3 #207', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9997211921257476
        #         self.CF3 /= 0.9985669764747996
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]/1.4013235909192496e-14-1.0) < 0.00000001 :
        #     if self.onlyonce6 :
        #         self.onlyonce6 = False
        #         print ('keypoint CF3 #267', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9946660501016131
        #         self.CF3 /= 0.9930813847351339
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay
        # if abs(self.lastRes[not(inc)]/1.4208504063681235e-14-1.0) < 0.00000001 :
        #     if self.onlyonce5 :
        #         self.onlyonce5 = False
        #         print ('keypoint CF3 #271', self.CF3, 'inc', inc)
        #         self.CF3 *= 0.9999851664472873
        #         self.CF3 /= 0.9998345876044842
        #         # self.CF3 *= this_decay
        #         # self.CF3 /= other_decay


        if dadove == 'for':
            if inc == 1 :
                self.CF3 *= self.error_decay_state
            if inc == 0 :
                self.CF3 *= other_decay
        else :
            self.CF3 *= other_decay

        resid = res * self.lastRes[not(inc)]
        #self.CF3 *= this_decay 
        self.CF3 += resid
        self.w3 += 1
        self.lastRes[inc] = res

        #DEBUG
        # if abs(self.CF3) > 0 and self.incStats[inc].Lambda == 0.01:
        #     print ('other_decay', other_decay, 'this_decay', this_decay)
        #     #print (self.incStats[inc].ID)
        #     print ('res', res, 'other last_res', self.lastRes[not(inc)])
        #     print ('resid', resid, 'v', v, 'mean1', self.incStats[inc].mean())
        #     print ('CF3', self.CF3, 'dadove', dadove)
        #     #print ('w3/2', self.w3/2, 'cov', self.CF3/self.w3*2)
        #     #print ('w1 not inc', (self.incStats[not(inc)].w, 'cov_wrong', self.CF3/self.incStats[not(inc)].w)
        #     print ('w1+w2', (self.incStats[not(inc)].w+self.incStats[inc].w), 'cov_wrong', self.CF3/(self.incStats[not(inc)].w+self.incStats[inc].w))
        #     #sys.exit()

        myid1=self.incStats[not(inc)].ID+'_'+str(self.incStats[not(inc)].Lambda)
        myid2=self.incStats[inc].ID+'_'+str(self.incStats[inc].Lambda)
        #print('id1',myid1,'id2',myid2)
        # lower=state.order(myid1,myid2)
        # if lower==0 :
        #     key = myid1+'_'+str(self.incStats[1-lower].Lambda)
        # else :
        #     key = myid2+'_'+str(self.incStats[1-lower].Lambda)
        if myid1 in state.map2D :
            key = myid1
        else :
            key = myid2
        # if abs(self.w3 - state.map2D[key]['all'][0]) > 0.0000001 :
        #     print ('key',key,'Lambda',self.incStats[inc].Lambda,'compare w3 wrong',self.w3, state.map2D[key]['all'][0] )
        # if abs(self.CF3 - state.map2D[key]['all'][1]) > 0.0000001 :
        #     print ('key',key,'Lambda',self.incStats[inc].Lambda,'compare CF3 wrong',self.CF3, state.map2D[key]['all'][1] )
        # if (key == '192.168.2.101192.168.2.110_0.01') :
        #     print ('AAAAAAkey',key,'Lambda',self.incStats[inc].Lambda,'compare CF3 wrong',self.CF3, state.map2D[key]['all'][1] )

    def processDecay(self,t,micro_inc_indx):
        factor = 1
        # check for decay cf3
        timeDiffs_cf3 = t - self.lastTimestamp_cf3
        if timeDiffs_cf3 > 0:
            factor = math.pow(2, (-(self.incStats[micro_inc_indx].Lambda) * timeDiffs_cf3))
            self.CF3 *= factor
            self.w3 *= factor
            self.lastTimestamp_cf3 = t
            self.lastRes[micro_inc_indx] *= factor
        return factor

    #todo: add W3 for cf3

    #covariance approximation
    def cov(self):
        return self.CF3 / self.w3

    # Pearson corl. coef
    def pcc(self):
        ss = self.incStats[0].std() * self.incStats[1].std()
        if ss != 0:
            return self.cov() / ss
        else:
            return 0

    # calculates and pulls all correlative stats
    def get_stats1(self):
        return [self.cov(), self.pcc()]

    # calculates and pulls all correlative stats AND 2D stats from both streams (incStat)
    def get_stats2(self):
        # return [self.incStats[0].radius([self.incStats[1]]),self.incStats[0].magnitude([self.incStats[1]]),self.cov(), self.pcc()]
        return [self.incStats[0].magnitude([self.incStats[1]]), self.incStats[0].radius([self.incStats[1]]),self.cov(), self.pcc()]

    # calculates and pulls all correlative stats AND 2D stats AND the regular stats from both streams (incStat)
    def get_stats3(self):
        return [self.incStats[0].w,self.incStats[0].mean(),self.incStats[0].std(),self.incStats[1].w,self.incStats[1].mean(),self.incStats[1].std(),self.cov(), self.pcc()]

    # calculates and pulls all correlative stats AND the regular stats from both incStats AND 2D stats
    def get_stats4(self):
        return [self.incStats[0].w,self.incStats[0].mean(),self.incStats[0].std(),self.incStats[1].w,self.incStats[1].mean(),self.incStats[1].std(), self.incStats[0].radius([self.incStats[1]]),self.incStats[0].magnitude([self.incStats[1]]),self.cov(), self.pcc()]

    def getHeaders(self,ver,suffix=True): #ver = {1,2,3,4}
        headers = []
        s0 = "0"
        s1 = "1"
        if suffix:
            s0 = self.incStats[0].ID
            s1 = self.incStats[1].ID

        if ver == 1:
            headers = ["covariance_"+s0+"_"+s1, "pcc_"+s0+"_"+s1]
        if ver == 2:
            headers = ["radius_"+s0+"_"+s1, "magnitude_"+s0+"_"+s1, "covariance_"+s0+"_"+s1, "pcc_"+s0+"_"+s1]
        if ver == 3:
            headers = ["weight_"+s0, "mean_"+s0, "std_"+s0,"weight_"+s1, "mean_"+s1, "std_"+s1, "covariance_"+s0+"_"+s1, "pcc_"+s0+"_"+s1]
        if ver == 4:
            headers = ["weight_" + s0, "mean_" + s0, "std_" + s0, "covariance_" + s0 + "_" + s1, "pcc_" + s0 + "_" + s1]
        if ver == 5:
            headers = ["weight_"+s0, "mean_"+s0, "std_"+s0,"weight_"+s1, "mean_"+s1, "std_"+s1, "radius_"+s0+"_"+s1, "magnitude_"+s0+"_"+s1, "covariance_"+s0+"_"+s1, "pcc_"+s0+"_"+s1]
        return headers


class incStatDB:
    # default_lambda: use this as the lambda for all streams. If not specified, then you must supply a Lambda with every query.
    def __init__(self,limit=np.Inf,default_lambda=np.nan):
        self.HT = dict() #it is a map with all the statistics, indexed by source+lambda
        self.HT_approx = dict()
        self.limit = limit
        self.df_lambda = default_lambda

    def get_lambda(self,Lambda):
        if not np.isnan(self.df_lambda):
            Lambda = self.df_lambda
        return Lambda

    # Registers a new stream. init_time: init lastTimestamp of the incStat
    def register(self,ID,Lambda=1,init_time=0,isTypeDiff=False,lru=None,ID_lru=None,for2D=False):
        #Default Lambda?
        Lambda = self.get_lambda(Lambda)

        if ID_lru is None:
            key_lru = ('jitter'+ID if isTypeDiff else ID)
        else:
            key_lru = ID_lru
        key_lru = ('jitter'+ID if isTypeDiff else ID)
        # print(f"key_lru: {key_lru}")

        #Retrieve incStat
        key = ('jitter'+ID if isTypeDiff else ID)+"_"+str(Lambda)
        # print(f"key:     {key}")

        incS = None
        if key in lru:
            # get stat
            # print("get")
            incS = self.HT.get(key)
        # this is a fix for a bug that happens only in the Mirai dataset and
        # only in 4 packets, so for now it does not look so bad...
        if incS is not None:
            return incS
        else:
            # init stat
            # print("init")
            # self.not_found_ctr += 1
            # print(f"not found: {self.not_found_ctr}")
            incS = incStat(Lambda, ID, 0 if isTypeDiff else init_time, isTypeDiff=isTypeDiff)
            # add new entries
            self.HT[key] = incS
            lru[key] = 1
        return incS

    # Registers covariance tracking for two streams, registers missing streams
    def register_cov(self,ID1,ID2,Lambda=1,init_time=0,isTypeDiff=False,lru=None):
        # if ID1 == '192.168.2.1' and ID2 == '192.168.2.108' and Lambda == 5:
        #     print ('register_cov')
        #Default Lambda?
        Lambda = self.get_lambda(Lambda)

        # Lookup both streams
        incS1 = self.register(ID1+'_'+ID2,Lambda,init_time,isTypeDiff, lru=lru,
                              for2D=True)
        incS2 = self.register(ID2+'_'+ID1,Lambda,init_time,isTypeDiff, lru=lru,
                              ID_lru=ID1+'_'+ID2)

        #check for pre-existing link
        for cov in incS1.covs:
            # if ID1 == '192.168.2.1' and ID2 == '192.168.2.108' and Lambda == 5:
            #     print ('IDs:',cov.incStats[0].ID,cov.incStats[1].ID)
            if (cov.incStats[0].ID == ID2+'_'+ID1 and cov.incStats[1].ID ==ID1+'_'+ID2) or (cov.incStats[1].ID == ID2+'_'+ID1 and cov.incStats[0].ID ==ID1+'_'+ID2) :
                # print('existing cov!')
                return cov #there is a pre-exiting link

        # Link incStats
        inc_cov = incStat_cov(incS1,incS2,init_time)
        incS1.covs.append(inc_cov)
        incS2.covs.append(inc_cov)
        return inc_cov

    # updates/registers stream
    def update(self,ID,t,v,Lambda=1,isTypeDiff=False, lru=None):
        # if (ID=='00:14:1c:28:d6:0601:80:c2:00:00:00' and Lambda == 5) :
        #     print ('inside update')
        incS = self.register(ID,Lambda,t,isTypeDiff, lru=lru)
        incS.insert(v,t)
        if Lambda == 1 :
            #the time_value array attribute is populated only for Lambda == 1
            incS.time_value.append([t,v])
        return incS

    # Pulls current stats from the given ID
    def get_1D_Stats(self,ID,Lambda=1): #weight, mean, std
        #Default Lambda?
        Lambda = self.get_lambda(Lambda)

        #Get incStat
        incS = self.HT.get(ID+"_"+str(Lambda))
        if incS is None:  # does not already exist
            return [np.na]*3
        else:
            return incS.allstats_1D()

    # Pulls current correlational stats from the given IDs
    def get_2D_Stats(self, ID1, ID2, Lambda=1): #cov, pcc
        # Default Lambda?
        Lambda = self.get_lambda(Lambda)

        # Get incStat
        incS1 = self.HT.get(ID1 + "_" + str(Lambda))
        if incS1 is None:  # does not exist
            return [np.na]*2

        # find relevant cov entry
        return incS1.cov_pcc(ID2)

    # Pulls all correlational stats registered with the given ID
    # returns tuple [0]: stats-covs&pccs, [2]: IDs
    def get_all_2D_Stats(self, ID, Lambda=1):  # cov, pcc
        # Default Lambda?
        Lambda = self.get_lambda(Lambda)

        # Get incStat
        incS1 = self.HT.get(ID + "_" + str(Lambda))
        if incS1 is None:  # does not exist
            return ([],[])

        # find relevant cov entry
        stats = []
        IDs = []
        for cov in incS1.covs:
            stats.append(cov.get_stats1())
            IDs.append([cov.incStats[0].ID,cov.incStats[1].ID])
        return stats,IDs

    # Pulls current multidimensional stats from the given IDs
    def get_nD_Stats(self,IDs,Lambda=1): #radius, magnitude (IDs is a list)
        # Default Lambda?
        Lambda = self.get_lambda(Lambda)

        # Get incStats
        incStats = []
        for ID in IDs:
            incS = self.HT.get(ID + "_" + str(Lambda))
            if incS is not None:  #exists
                incStats.append(incS)

        # Compute stats
        rad = 0 #radius
        mag = 0 #magnitude
        for incS in incStats:
            rad += incS.var()
            mag += incS.mean()**2

        return [np.sqrt(rad),np.sqrt(mag)]

    # Updates and then pulls current 1D stats from the given ID. Automatically registers previously unknown stream IDs
    def update_get_1D_Stats(self, ID, t, v, Lambda=1, isTypeDiff=False,
                            stateUpdate=True, lru=None, for2D=False):  # weight, mean, std
        # if (ID=='00:14:1c:28:d6:0601:80:c2:00:00:00' and Lambda == 5) :
        #     print ('after image here')
        # if (ID=='c:33:00:98:3ee:fd_ff:ff:ff:ff:ff:ff' and Lambda == 1) :
        #     print ('after image here')
        #     sys.exit()

        if stateUpdate :
            state.update('jitter'+ID if isTypeDiff else ID,v,t,Lambda=Lambda,isTypeDiff=isTypeDiff)
        incS = self.update(ID,t,v,Lambda,isTypeDiff=isTypeDiff, lru=lru)
        if for2D:
            return incS.allstats_1D(for2D=True)
        else:
            return incS.allstats_1D()

    # Updates and then pulls current correlative stats between the given IDs. Automatically registers previously unknown stream IDs, and cov tracking
    #Note: AfterImage does not currently support Diff Type streams for correlational statistics.
    def update_get_2D_Stats(self,ID1,ID2,t1,v1,Lambda=1,level=1, lru=None):  #level=  1:cov,pcc  2:radius,magnitude,cov,pcc
        #state.update2D(ID1, ID2, v1, t1, Lambda)
        #retrieve/add cov tracker
        # if ID1 == '192.168.2.1' and ID2 == '192.168.2.108' and Lambda == 5:
        #     print('update_get_2D_Stats',ID1,ID2)
        inc_cov = self.register_cov(ID1, ID2, Lambda, t1, lru=lru)
        
        # Update cov tracker
        inc_cov.update_cov(ID1+'_'+ID2,v1,t1, dadove='get2D')
        if level == 1:
            return inc_cov.get_stats1()
        else:
            return inc_cov.get_stats2()

    # Updates and then pulls current 1D and 2D stats from the given IDs. Automatically registers previously unknown stream IDs
    def update_get_1D2D_Stats(self, ID1,ID2,t1,v1,Lambda=1,counter=0, lru=None):  # weight, mean, std
        #return self.update_get_1D_Stats(ID1,t1,v1,Lambda) + self.update_get_2D_Stats(ID1,ID2,t1,v1,Lambda,level=2)
        # if ((ID1+'_'+ID2)=='00:14:1c:28:d6:06_01:80:c2:00:00:00' and Lambda == 5) :
        #     print ('second after image here')
        meanID1_ID2 = state.update(ID1+'_'+ID2,v1,t1,Lambda,return_mean=True)
        state.update2D(ID1, ID2, v1, t1, meanID1_ID2, Lambda,counter)
        # return self.update_get_1D_Stats(ID1+'_'+ID2,t1,v1,Lambda,stateUpdate=False, lru=lru) + self.update_get_2D_Stats(ID1,ID2,t1,v1,Lambda,level=2, lru=lru)
        return self.update_get_1D_Stats(ID1+'_'+ID2,t1,v1,Lambda,stateUpdate=False,lru=lru,for2D=True) + self.update_get_2D_Stats(ID1,ID2,t1,v1,Lambda,level=2, lru=lru)
    
    def getHeaders_1D(self,Lambda=1,ID=None):
        # Default Lambda?
        Lambda = self.get_lambda(Lambda)
        hdrs = incStat(Lambda,ID).getHeaders_1D(suffix=False)
        return [str(Lambda)+"_"+s for s in hdrs]

    def getHeaders_2D(self,Lambda=1,IDs=None, ver=1): #IDs is a 2-element list or tuple
        # Default Lambda?
        Lambda = self.get_lambda(Lambda)
        if IDs is None:
            IDs = [0,1]
        hdrs = incStat_cov(incStat(Lambda,IDs[0]),incStat(Lambda,IDs[0]),Lambda).getHeaders(ver,suffix=False)
        return [str(Lambda)+"_"+s for s in hdrs]

    def getHeaders_1D2D(self,Lambda=1,IDs=None, ver=1):
        # Default Lambda?
        Lambda = self.get_lambda(Lambda)
        if IDs is None:
            IDs = [0,1]
        hdrs1D = self.getHeaders_1D(Lambda,IDs[0])
        hdrs2D = self.getHeaders_2D(Lambda,IDs, ver)
        return hdrs1D + hdrs2D

    def getHeaders_nD(self,Lambda=1,IDs=[]): #IDs is a n-element list or tuple
        # Default Lambda?
        ID = ":"
        for s in IDs:
            ID += "_"+s
        Lambda = self.get_lambda(Lambda)
        hdrs = ["radius"+ID, "magnitude"+ID]
        return [str(Lambda)+"_"+s for s in hdrs]


    #cleans out records that have a weight less than the cutoff.
    #returns number or removed records.
    def cleanOutOldRecords(self,cutoffWeight,curTime):
        n = 0
        dump = sorted(self.HT.items(), key=lambda tup: tup[1][0].getMaxW(curTime))
        for entry in dump:
            entry[1][0].processDecay(curTime)
            W = entry[1][0].w
            if W <= cutoffWeight:
                key = entry[0]
                del entry[1][0]
                del self.HT[key]
                n=n+1
            elif W > cutoffWeight:
                break
        return n
