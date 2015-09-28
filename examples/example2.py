"""

Following code demostrates the use of the hoppMCMC algorithm
for sampling from different posterior modes of the Langermann's function

"""

from hoppMCMC import hoppMCMC, chainMCMC
from numpy import cos,pi,exp,sqrt,Inf,isnan,array,cov,repeat
import pylab

def langer(x,y):
#   pyOpt: http://www.pyopt.org/examples/examples.autorefine.html
    
    a = [3,5,2,1,7]
    b = [5,2,1,4,9]
    c = [1,2,5,3,5]
    
    f = 0.0
    for i in xrange(5):
        f += -(c[i]*exp(-(1/pi)*((x-a[i])**2 + (y-b[i])**2))*cos(pi*((x-a[i])**2 + (y-b[i])**2)))
    
    return f

## The following is the objective function to be optimised
def fitness(x):
    if any(isnan(x)) or any(x<0.0) or any(x>10.0):
        return Inf
    return 4.0*(6.0+langer(x[0],x[1]))

## The following will run the hoppMCMC algorithm
results = hoppMCMC(fitness,            # define the objective function
                   param = [5.0,5.0],  # begin with x=5, y=5
                   varmat = [[1e-14,0],[0,1e-14]],
                                       # assign a low initial proposal variation
                   gibbs = True,       # this is enforced for single-parameter runs
                   rangeT = [1,10],    # define the range of annealing temperature
                   model_comp = 10,    # tolerance for accepting hopp-steps
                   num_hopp = 10,      # run for 10 hopp-steps
                   num_adapt = 100,    # each hopp-step comprises 100 adaptation steps
                   num_chain = 4,      # run with 4 parallel chains
                   chain_length = 10)  # each chain is 10 iterations long

## This will plot the state of the chains at the end of each hopp-step
pylab.plot([0,10],[0,10],alpha=0)
for n in range(len(results.parmats)):
    pylab.plot(repeat(n,4),results.parmats[n][:,1],'o')
pylab.show()

## This will select the final hopp-step and run an MCMC chain to sample
## from around the identified posterior mode
n = len(results.parmats)-1
parmat = array(results.parmats[n])
param = parmat[parmat[:,0]==min(parmat[:,0]),1:][0]
varmat = cov(parmat[:,1:],rowvar=False)

## The following will run the chainMCMC algorithm
mcmc =   chainMCMC(fitness,            # define the objective function
                   param = param,      # begin with the optimum sample from results
                   varmat = varmat,    # assign an initial proposal variation
                   inferpar = [0,1],   # infer both x and y
                   gibbs = True,       # this is enforced for single-parameter runs
                   chain_id = 0,       # chain identifier
                   pulsevar = 1,       # scaling factor for proposal variation
                   anneal = 1,         # annealing temperature
                   accthr = 0.25,      # target acceptance rate
                   varmat_change = 0,  # varmat is fixed
                   pulse_change = 10,  # variation is scaled at each 10th step
                   pulse_change_ratio = 2,
                                       # scaling is linear with a coefficient 2
                   print_iter = 100)   # status is displayed at each 100th iteration

# This will iterate the chainMCMC for 10000 steps recording every 25th iteration
# while discarding the initial 5000 steps
samples = []
for m in range(10000):
    mcmc.iterate()
    if m>5000 and m%25==0:
        samples.append(mcmc.getParam())
samples = array(samples)

# This will plot the posterior samples obtained from chainMCMC
pylab.plot([0,10],[0,10],alpha=0)
pylab.plot(samples[:,1],samples[:,2],marker='o',linewidth=0)
pylab.show()
