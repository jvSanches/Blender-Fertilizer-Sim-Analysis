import sys
import os
import matplotlib.pyplot as plt
import numpy

##Simulation settings
blender_frames =  2000
blender_timestep = 0.01
blender_groud_speed = 18 #m/s
blender_dose = 100 #kg/ha
blender_density = 1 #g/cm^3
blender_simulation_time = blender_frames * blender_timestep
blender_logger_ver = 0.2

def getVolumeDiferential(T,S,discrete_time_step, simulation_time_step, frames):
    ###Converts dying times to volume increment for each timestep

    T_ = [i for i in T]
    S_ = [i for i in S]
    discrete_period = int(discrete_time_step / simulation_time_step)
    differential_volume = []
    for i in range(0,frames, discrete_period):
        step_volume = 0
        eval_time = i
        for j in reversed(range(len(T_))):
            if T_[j] < eval_time:
                step_volume += (S_[j]/10)**3*3.1415
                del S_[j]
                del T_[j]
        differential_volume.append(step_volume)
    return differential_volume



def integrateVolumeDiferential(differential_volume):
    volume = [sum(differential_volume[0:i]) for i in range(len(differential_volume))] 
    return volume  


def calc_cv(differential_volume, samples):
    differential_volume_steps = len(differential_volume)
     
    cv = differential_volume_steps * [None]
    if differential_volume_steps < samples:
        print("Not enough samples for cv calculation... Exiting")
        input()
        quit()
        return cv 

    samples = int(samples/2)
    for i in range(samples, differential_volume_steps-samples):
        stddev = numpy.std(differential_volume[i-samples:i+samples])
        mean = numpy.mean(differential_volume[i-samples : i+samples])
        if mean != 0 and stddev != 0:
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
    
    header = lines[0].split(sep= ',')

    log_rotor = header[0].split(sep= ':')[-1]
    log_calha = header[1].split(sep= ':')[-1]
    log_rpm = float(header[2].split(sep= ':')[-1])
    log_dose = float(header[3].split(sep= ':')[-1])
    log_ver = float(header[4].split(sep= ':')[-1])
    wrong_logger_version_message = " "
    if log_ver != blender_logger_ver:
        wrong_logger_version_message = "Versão do logger incorreta"
    
    #collumns = lines[1].split(sep= ',')
    for line in lines[2:]:
        splitvalues = line.split(sep= ',')
        X.append(float(splitvalues[0]))
        Y.append(float(splitvalues[1]))
        Z.append(float(splitvalues[2]))
        S.append(float(splitvalues[3]))
        T.append(float(splitvalues[4]))
        if T[-1] <= blender_frames:                ####There must be a better way
            Xabs.append(T[-1]*blender_groud_speed*blender_timestep + X[-1]/1000)
        else:
            Xabs.append(-1)
            S[-1] = 0
    y_mean = numpy.mean(Y)        
    discrete_time_step = 0.1
    diff_volume = getVolumeDiferential(T,S, discrete_time_step,blender_timestep, blender_frames)
    total_volume = integrateVolumeDiferential(diff_volume)
    cv_samples = 100
    cvs = calc_cv(diff_volume,cv_samples)
    cv_min = getMin(cvs)

    ###Generates the plot
    plt.figure(figsize=(6, 10))
    
    plt.suptitle("Rotor: %s      Calha: %s \nRotação(RPM): %.1f  Dosagem(Kg/ha): %.1f  Versão do Logger: %.1f \n %s" %(log_rotor, log_calha, log_rpm, log_dose ,log_ver,wrong_logger_version_message))
    plt.subplot(411)
    plotscale = 0.5
    plt.scatter(Xabs,Y-y_mean,s=[i * plotscale for i in S], edgecolors='none')
    plt.ylim(-70,70)
    plt.title("Distribuição")
    plt.xlim(0, blender_groud_speed*blender_simulation_time)
    plt.xlabel("Distância [m]")
    plt.xlabel("[mm]")

    plt.subplot(412)    
    plt.plot(numpy.linspace(0,blender_simulation_time,len(total_volume)), total_volume)
    plt.title("Volume dosado")
    plt.ylabel("[cm^3]")
    plt.xlim(0, blender_simulation_time)
    plt.xlabel("Tempo [s]")
    plt.grid()

    plt.subplot(413)
    plt.plot(numpy.linspace(0,blender_simulation_time,len(diff_volume)),diff_volume, 'green')
    plt.xlim(0, blender_simulation_time)
    plt.title("Variação volumétrica")
    plt.xlabel("Tempo [s]")
    plt.grid()

    
    plt.subplot(414)    
    plt.plot(cvs, 'red')
    plt.title("CV para %s amostras" %(cv_samples))
    plt.xlim(0, len(cvs))
    plt.xlabel("Intervalos")

    plt.text(0.1,cv_min+0.1, "Min cv: %.3f" %(cv_min))
    plt.hlines(cv_min, 0, len(cvs), linestyles= 'dashed')
    plt.tight_layout(pad=0.5)
    if show_result: 
        plt.show()
    else:
        plt.savefig(droppedFile[:-4]+"_analysis.pdf", dpi=1200)
    


if len(sys.argv) > 1:
    for i in range(1, len(sys.argv)):
        filename = sys.argv[i]
        if filename[-3:] == "txt":
            print("Starting analysis...")            
            generate_plot(filename)
            print("Done. PDF generated \n")
else:
    filename = "R2-9x120d(148) + H0.txt"
    generate_plot(filename, 1)

