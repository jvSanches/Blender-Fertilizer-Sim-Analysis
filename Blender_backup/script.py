import bpy
import os

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

##lists sons of Rotors
def getChildren(Myobj):
    My_obj = bpy.data.objects[Myobj]
    childs = []
    for obj in bpy.data.objects:              
        if obj.parent:
            
            if obj.parent.name == Myobj:
                childs.append(obj)
    return childs

def prepare_sim():
    print("Preparing sim")
    #Gets sim objects
    rotors = getChildren('Rotors')
    hoppers = getChildren('Hoppers')

    #Reads witch objects to simulate
    sim_case_rotor = bpy.data.scenes[0]["sim_case_rotor"]
    sim_case_hopper = bpy.data.scenes[0]["sim_case_hopper"]



    rotor_damp = 0.3
    rotor_fric = 0.5
    hopper_damp = 0.4
    hopper_fric = 0.3

    i = rotors[sim_case_rotor]
    j = hoppers[sim_case_hopper]
    #Hopper selection and collision activation
    bpy.ops.object.select_pattern(pattern=i.name, extend=False)        
    bpy.context.view_layer.objects.active = i
    bpy.ops.object.modifier_add(type='COLLISION')
    i.modifiers[0].settings.damping_factor = hopper_damp
    i.modifiers[0].settings.friction_factor = hopper_fric
     
    #Rotor selection and collision activation   
    bpy.ops.object.select_pattern(pattern=j.name, extend=False)        
    bpy.context.view_layer.objects.active = j
    bpy.ops.object.modifier_add(type='COLLISION')
    j.modifiers[0].settings.damping_factor = rotor_damp
    j.modifiers[0].settings.friction_factor = rotor_fric

    #Reads rotor volume from rotor filename 
    #The name must contain the rotor volume in the form of [...](VOL)[...] where VOL is the volume in cm^3

    rotor_volume = float(i.name[i.name.index("(")+1:i.name.index(")")])

    #Dose must be set here
    dose = 100 #kg/ha
    global last_dose
    last_dose = dose
    moving_speed = 5 #Km/h
    row_spacing = 0.5 #m


    rotor_rpm = 10/6 * dose * row_spacing * moving_speed/rotor_volume
    global last_rpm
    last_rpm = rotor_rpm
    action_name = 'RotorsAction'
    rad_min = rotor_rpm * 6.2832
    # Find the appropriate action
    action = bpy.data.actions.get(action_name)
    fc = action.fcurves[0]
    while len(fc.keyframe_points)>1:
        fc.keyframe_points.remove(fc.keyframe_points[-1])
    fc.keyframe_points.insert(6000, rad_min)



    bpy.ops.ptcache.free_bake_all()
    bpy.ops.object.select_pattern(pattern='Emitter', extend=False)
    bpy.ops.object.mol_simulate()
    bpy.data.scenes[0]["sim_state"] = 2

def check_sim():
    em = bpy.data.objects["Emitter"]
    psys = em.particle_systems[0]
    if psys.point_cache.is_baked:
        bpy.data.scenes[0]["sim_state"] = 3
    


def clear_sim():
    print("Clearing sim")
     #Gets sim objects
    rotors = getChildren('Rotors')
    hoppers = getChildren('Hoppers')

    #Reads witch objects to simulate
    sim_case_rotor = bpy.data.scenes[0]["sim_case_rotor"]
    sim_case_hopper = bpy.data.scenes[0]["sim_case_hopper"]


    i = rotors[sim_case_rotor]
    j = hoppers[sim_case_hopper]
    #Rotor selection and collision removal
    bpy.ops.object.select_pattern(pattern=i.name, extend=False)      
    bpy.context.view_layer.objects.active = i
    bpy.ops.object.modifier_remove(modifier="Collision")
        
    #Hopper selection and collision removal    
    bpy.ops.object.select_pattern(pattern=j.name, extend=False)
    bpy.context.view_layer.objects.active = j
    bpy.ops.object.modifier_remove(modifier="Collision")

    #Updates next objects to simulate
    if sim_case_rotor + 1 == len(rotors):
        sim_case_rotor = 0
        sim_case_hopper +=1
    else:
        sim_case_rotor += 1

    if sim_case_hopper == len(hoppers):
        bpy.data.scenes[0]["sim_state"] = 5
        ## Ends simulation batch
    else:
        bpy.data.scenes[0]["sim_state"] = 1

    bpy.data.scenes[0]["sim_case_rotor"] = sim_case_rotor

    bpy.data.scenes[0]["sim_case_hopper"] = sim_case_hopper  

   


        
def log_sim():
    global last_rpm
    logger_ver = 0.2
    print("Logging sim")
    # Dependancy graph
    degp = bpy.context.evaluated_depsgraph_get()

    # Emitter Object 
    object = bpy.data.objects["Emitter"]

    # Evaluate the depsgraph (Important step)
    particle_systems = object.evaluated_get(degp).particle_systems

    # All particles of first particle-system which has index "0"
    particles = particle_systems[0].particles

    # Total Particles
    totalParticles = len(particles)

    locations = 3*totalParticles*[0]
    sizes = totalParticles*[0]
    deaths = totalParticles*[0]

    particles.foreach_get("location",locations)
    particles.foreach_get("size",sizes)
    particles.foreach_get("die_time",deaths)

    #Gets sim objects
    rotors = getChildren('Rotors')
    hoppers = getChildren('Hoppers')

    #Reads witch objects to simulate
    sim_case_rotor = bpy.data.scenes[0]["sim_case_rotor"]
    sim_case_hopper = bpy.data.scenes[0]["sim_case_hopper"]

    logname = rotors[sim_case_rotor].name + " + " + hoppers[sim_case_hopper].name
    file_location = os.getcwd()
    filename = file_location + "\\" + logname + ".txt"

    logfile = open(filename,"w")
    line = "Rotor: %s, Hopper: %s, RPM: %f, Dose: %f, Logger_Version: %s\n" %(rotors[sim_case_rotor].name, hoppers[sim_case_hopper].name,last_rpm,last_dose,logger_ver)
    logfile.write(line)    
    line = "x, y, z, size, die_time \n"
    logfile.write(line)
    for i in range(totalParticles):
        
        line = "%f, %f, %f, %f, %f \n" %(locations[3*i],locations[3*i+1],locations[3*i+2], sizes[i], deaths[i])
        logfile.write(line)
        
    logfile.close()
    bpy.data.scenes[0]["sim_state"] = 4


def sim_controller():
    sim_state = bpy.data.scenes[0]["sim_state"]
    
    
    if sim_state == 0:
        bpy.data.scenes[0]["sim_case_rotor"] = 0
        bpy.data.scenes[0]["sim_case_hopper"] = 0  
        print("Simcontroller Idle")
    elif sim_state == 1:
        prepare_sim()
    elif sim_state == 2:
        check_sim()
    elif sim_state == 3:
        log_sim()
    elif sim_state == 4:
        clear_sim()
    elif sim_state == 5:
        print("Simcontroller Stopped")
        bpy.data.scenes[0]["sim_state"] = 0
        ShowMessageBox(message = "##### Done Simulating. Close blender before next run#####", title = "Simulation", icon = 'INFO')
    
    else:
        print("Something went wrong")

    return 5


bpy.app.timers.register(sim_controller)
bpy.data.scenes[0]["sim_state"] = 1