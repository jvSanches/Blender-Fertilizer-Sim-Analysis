import bpy

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
    rotor_fric = 0.3
    hopper_damp = 0.3
    hopper_fric = 0.3

    i = rotors[sim_case_rotor]
    j = hoppers[sim_case_hopper]
    #Hopper selection and collision activation
    bpy.ops.object.select_pattern(pattern=i.name, extend=False)        
    bpy.context.view_layer.objects.active = i
    bpy.ops.object.modifier_add(type='COLLISION')
#    bpy.context.obj.collision.damping_factor = hopper_damp
#    bpy.context.obj.collision.friction = hopper_fric
     
    #Rotor selection and collision activation   
    bpy.ops.object.select_pattern(pattern=j.name, extend=False)        
    bpy.context.view_layer.objects.active = j
    bpy.ops.object.modifier_add(type='COLLISION')
#    bpy.context.obj.collision.damping_factor = rotor_damp
#    bpy.context.obj.collision.friction = rotor_fric

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

    logname = rotors[sim_case_rotor].name + hoppers[sim_case_hopper].name
    filename = "C:\\Users\\joao.vitor\\Documents\\teste molecular\\autologs\\%s.txt" %(logname)

    logfile = open(filename,"w")
    line = "x, y, z, size \n"
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
    
    else:
        print("Something went wrong")

    return 5


bpy.app.timers.register(sim_controller)