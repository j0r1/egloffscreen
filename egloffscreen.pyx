import os
os.environ["PYOPENGL_PLATFORM"] = "egl" # Make sure EGL is used to query context, not glx

class EGLOffScreenException(Exception):
    pass

cimport wrapper
if not wrapper.init():
    raise EGLOffScreenException("Unable to prepare and set off-screen context using EGL")
