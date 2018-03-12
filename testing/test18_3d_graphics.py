print("START")
from rotatingCamera import RotatingCamera

pi3d=RotatingCamera.getpi3d()

display = pi3d.Display.create(samples=4)
display.set_background(0,0,0,0)
cam = pi3d.Camera(is_3d=True)
shader = pi3d.Shader("uv_light")

print("DONE")
