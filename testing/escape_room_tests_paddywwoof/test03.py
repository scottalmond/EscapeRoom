import sys
sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
import pi3d
import numpy as np
import math
import random

RANGE = 100.0
HIT_DIST = 5.0
MODEL_PATH = '{}'

def shallow_clone(shape):
  state = shape.__getstate__()
  clone = pi3d.Triangle() # just saves having to feed in all init arguments, any shape will do
  clone.__setstate__(state) # as everything is overwritten here
  return clone

display = pi3d.Display.create(background=(0.0, 0.0, 0.0, 0.0))
camera = pi3d.Camera()
shader = pi3d.Shader('uv_light')
laser_shader = pi3d.Shader('mat_flat')

# scene - empty to hold objects
scene = pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))

# pod, base and gun
pod = pi3d.Model(file_string=MODEL_PATH.format('pod_2.obj'), z=20.0)
laser_base = pi3d.Model(file_string=MODEL_PATH.format('laser_base_2.obj'), y=3.15)
laser_gun = pi3d.Model(file_string=MODEL_PATH.format('laser_gun_2.obj'), y=0.4, z=-0.4)
laser_base.add_child(laser_gun)
pod.add_child(laser_base)
pod.set_shader(shader) # all use uv_light shader

# laser beam itself not a child
laser_tip = pi3d.Cuboid(w=0.05, h=0.05, d=5.0)
laser_tip.set_material((1.0, 0.0, 0.0))
laser_tip.set_alpha(0.0)
laser_tip.set_shader(laser_shader)

# asteroid
asteroid = pi3d.Model(file_string=MODEL_PATH.format('asteroid_large_1.obj'), z=50, y=10, x=20)
asteroid.set_shader(shader)

# rings
ring = pi3d.Model(file_string=MODEL_PATH.format('straight_ring_2.obj'))
empty = pi3d.Triangle(corners=((0,0),(1,1),(-1,1)), z=50.05)
ring.set_shader(shader)
ring.set_fog((0.0, 0.0, 0.0, 0.0), 300.6)
empty.add_child(ring)
ring_list = [empty]
for i in range(5):
  next_empty = empty.shallow_clone() #(empty)
  next_empty.rotateIncX(random.random() * 40.0 - 20.0)
  next_empty.rotateIncY(random.random() * 40.0 - 20.0)
  next_ring = ring.shallow_clone() #(ring)
  next_empty.children = [next_ring]
  ring_list[-1].add_child(next_empty)
  ring_list.append(next_empty)

scene.add_child(pod)
scene.add_child(asteroid)
scene.add_child(empty)
scene.add_child(laser_tip)

keys = pi3d.Keyboard()
mouse = pi3d.Mouse(restrict=False)
mouse.start()

blast_dist = 0.0

while display.loop_running():
  scene.draw()

  ring_list[0].translateZ(-0.1)
  rx, ry = ring_list[0].unif[3:5]
  ring_list[0].rotateToX(rx * 0.98)
  ring_list[0].rotateToY(ry * 0.98)

  if ring_list[0].z() < 0:
    # check clash
    r_swap = ring_list[0]
    scene.children.remove(r_swap)
    ring_list[-1].add_child(r_swap)
    ring_list = ring_list[1:] + [r_swap]
    r_swap.children.remove(ring_list[0])
    r_swap.positionZ(50.0)
    r_swap.rotateIncX(random.random() * 40.0 - 20.0)
    r_swap.rotateIncY(random.random() * 40.0 - 20.0)
    
    scene.add_child(ring_list[0])

  for r in ring_list:
    r.children[0].rotateIncZ(1.0)

  asteroid.rotateIncZ(2.0)
  mx, my = mouse.position()
  laser_base.rotateToY(mx)
  laser_gun.rotateToX(max(min(20, -my), -85))
  if blast_dist > 0.0:
    laser_tip.set_alpha(0.8)
    laser_tip.position(*(but_pt + aim_vec * (1.0 + blast_dist)))
    blast_dist += 5.0
    if blast_dist > RANGE:
      blast_dist = 0.0
      laser_tip.set_alpha(0.0)
      asteroid.set_material((0.5, 0.5, 0.5))
    if (abs(laser_tip.unif[0] - asteroid.unif[0]) < HIT_DIST and # cheaper calc than euclidean dist
        abs(laser_tip.unif[1] - asteroid.unif[1]) < HIT_DIST and
        abs(laser_tip.unif[2] - asteroid.unif[2]) < HIT_DIST):
      euclidean = sum((laser_tip.unif[i] - asteroid.unif[i]) ** 2 for i in range(3)) ** 0.5
      print(euclidean)
      asteroid.set_material((1.0, 1.0, 0.0))

  k = keys.read()
  if k >-1:
    if k == ord('a'):
      pod.translateX(-0.2)
    elif k == ord('d'):
      pod.translateX(0.2)
    elif k == ord('w'):
      pod.translateY(0.2)
    elif k == ord('s'):
      pod.translateY(-0.2)
    elif k == ord('q'):
      pod.rotateIncY(8)
    elif k == ord('e'):
      pod.rotateIncX(8)
    elif k == ord(' '): # shoot with space
      blast_dist = 0.5 # positive value 'sets it off'
      but_pt, aim_vec = laser_gun.transform_direction([0.0, 0.3, 1.0],
                                                      [0.0, 0.3, 0.0])
      laser_tip.rotate_to_direction(aim_vec)
    elif k==27:
      keys.close()
      display.destroy()
      break
  if np.sum(np.abs(camera.eye[0:2] - pod.unif[0:2])) > 0.05:
    camera.reset()
    camera.position((camera.eye[0] * 0.98 + pod.x() * 0.02, 
                     camera.eye[1] * 0.98 + pod.y() * 0.02, 0.0))
