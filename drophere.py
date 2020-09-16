import sys
import os
import matplotlib.pyplot as plt
import numpy


def timeDistribution(T,S, discrete_time_step):
    T_ = [i for i in T]
    S_ = [i for i in S]
    time_step = 0.01
    discrete_period = int(discrete_time_step / time_step)
    sim_frames = 1500
    accumulated_volume = []
    for i in range(0,sim_frames, discrete_period):
        step_volume = 0
        eval_time = i
        for j in reversed(range(len(T_))):
            if T_[j] < eval_time:
                step_volume += S_[j]**3
                del S_[j]
                del T_[j]
        accumulated_volume.append(step_volume)
    return accumulated_volume



def getDistribution(X,S,step_size):
    x = [i for i in X]
    s = [i for i in S]
    steps = int((max(x)-min(x))/step_size)
    startx = min(x)
    diff_volume = []
    for step in range(steps):
        eval_x = startx + step * step_size
        eval_volume = 0
        for i in reversed(range(len(x))):
            if x[i] <= eval_x:
                eval_volume += s[i]**3
                del x[i]
                del s[i]
        diff_volume.append(eval_volume)  
    return diff_volume  



def calc_cv(diff_volume, samples):
    measurements = len(diff_volume)
    cv = measurements * [None]
    sammples = 5
    for i in range(samples, measurements-samples):
        stddev = numpy.std(diff_volume[i-samples:i+samples])
        mean = numpy.mean(diff_volume[i-samples : i+samples])
        cv[i] = stddev/mean 
    
    return cv

def getMin(values):
    locmin = float('inf')
    for i in range(len(values)):        
        if values[i] != None and values[i] < locmin:
            locmin = values[i]
    return locmin

def generate_plot(droppedFile, show_result = 0):
    print(droppedFile)
    logfile = open(droppedFile, 'r')
    lines = logfile.readlines()
    X = []
    Y = []
    Z = []
    S = []
    T = []
    Xabs = []

    for line in lines[1:]:
        splitvalues = line.split(sep= ',')
        X.append(float(splitvalues[0]))
        Y.append(float(splitvalues[1]))
        Z.append(float(splitvalues[2]))
        S.append(float(splitvalues[3]))
        T.append(float(splitvalues[4]))
        Xabs.append([T[-1]*18 + X[-1]])
        

    plt.figure()
    plotscale = 0.5
    plt.scatter(Xabs,Y,s=[i * plotscale for i in S], edgecolors='none')
    # plt.axis([min(Xabs), max(Xabs), -300, 300])
    plt.ylim(-300,300)
    plt.title("Distribuição")
    if show_result: 
        plt.show()
    else:
        plt.savefig(droppedFile[:-4]+"_distribution.png", dpi=1200)
    plt.figure()
    plt.subplot(311)

    diff_volume = timeDistribution(T,S, 0.5)

    volume = [sum(diff_volume[0:i]) for i in range(len(diff_volume))]
    plt.plot(volume)
    plt.title("Volume dosado")

    plt.subplot(312)
    # diff_volume = getDistribution(X,S,10)
    plt.plot(diff_volume, 'green')
    # plt.xlim(0, len(diff_volume))
    plt.title("Variação volumétrica")
    plt.subplot(313)
    cvs = calc_cv(diff_volume,5)
    plt.plot(cvs, 'red')
    plt.xlim(0, len(cvs))
    plt.title("CV")
    cv_min = getMin(cvs)
    plt.text(0.1,cv_min+0.1, "Min cv: %.3f" %(cv_min))
    plt.hlines(cv_min, 0, len(cvs), linestyles= 'dashed')
    plt.tight_layout(pad=0.5)
    if show_result: 
        plt.show()
    else:
        plt.savefig(droppedFile[:-4]+"_analysis.png", dpi=1200)
    

   

if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        filename = sys.argv[i]
        if filename[-3:] == "txt":
            print("Starting analysis...")            
            generate_plot(filename)
            print("Done. Image generated \n")
else:
    filename = "hellix 120 16-14-15.txt"
    generate_plot(filename, 1)

