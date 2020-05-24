import os
os.environ["PYOPENGL_PLATFORM"] = "egl" # Make sure EGL is used to query context, not glx

class EGLOffScreenException(Exception):
    pass

from ctypes import *

EGL_SURFACE_TYPE = 0x3033
EGL_PBUFFER_BIT = 0x0001
EGL_BLUE_SIZE = 0x3022
EGL_GREEN_SIZE = 0x3023
EGL_RED_SIZE = 0x3024
EGL_DEPTH_SIZE = 0x3025
EGL_RENDERABLE_TYPE = 0x3040
EGL_OPENGL_BIT = 0x0008
EGL_NONE = 0x3038
EGL_WIDTH = 0x3052
EGL_HEIGHT = 0x3056
EGL_OPENGL_API = 0x30A2
EGL_NO_CONTEXT = None
EGL_PLATFORM_DEVICE_EXT = 0x313F

EGL = cdll.LoadLibrary("libEGL.so")
eglGetProcAddress = EGL.eglGetProcAddress
eglGetProcAddress.argtypes = (c_char_p,)
eglGetProcAddress.restype = c_void_p

eglQueryDevicesEXT = CFUNCTYPE(c_uint, c_int, c_void_p, POINTER(c_int))(eglGetProcAddress(c_char_p(b"eglQueryDevicesEXT")))

eglDevs, numDevs = (c_void_p*16)(), c_int(0)
eglQueryDevicesEXT(len(eglDevs), eglDevs, byref(numDevs))
if numDevs.value < 1:
    raise EGLOffScreenException("No devices detected")

eglGetPlatformDisplayEXT = CFUNCTYPE(c_void_p, c_uint, c_void_p, POINTER(c_int))(eglGetProcAddress(c_char_p(b"eglGetPlatformDisplayEXT")))
eglInitialize = EGL.eglInitialize
eglInitialize.argtypes = (c_void_p, POINTER(c_int), POINTER(c_int))
eglInitialize.restype = c_uint

for devIdx in range(numDevs.value):
    eglDpy = eglGetPlatformDisplayEXT(EGL_PLATFORM_DEVICE_EXT, eglDevs[devIdx], None)
    if eglDpy is None:
        raise EGLOffScreenException("No EGL display could be created")

    major, minor = c_int(0), c_int(0)
    if eglInitialize(eglDpy, byref(major), byref(minor)):
        break
else:
    raise EGLOffScreenException("Could not initialize EGL display")

print("Using device idx {} ({})".format(devIdx, numDevs.value))
print("Major: {} minor: {}".format(major.value, minor.value))

configAttribs = (c_int*13)(
          EGL_SURFACE_TYPE, EGL_PBUFFER_BIT,
          EGL_BLUE_SIZE, 8,
          EGL_GREEN_SIZE, 8,
          EGL_RED_SIZE, 8,
          EGL_DEPTH_SIZE, 8,
          EGL_RENDERABLE_TYPE, EGL_OPENGL_BIT,
          EGL_NONE)
numConfigs = c_int(0)

eglChooseConfig = EGL.eglChooseConfig
eglChooseConfig.argtypes = (c_void_p, POINTER(c_int), c_void_p, c_int, POINTER(c_int))
eglChooseConfig.restype = c_uint

eglCfg = c_void_p(None)
eglChooseConfig(eglDpy, configAttribs, byref(eglCfg), 1, byref(numConfigs))
if numConfigs.value != 1:
    raise EGLOffScreenException("Could not find EGL config")

pbufferAttribs = (c_int*5)(EGL_WIDTH, 9, EGL_HEIGHT, 9, EGL_NONE)

eglCreatePbufferSurface = EGL.eglCreatePbufferSurface
eglCreatePbufferSurface.argtypes = (c_void_p, c_void_p, POINTER(c_int))
eglCreatePbufferSurface.restype = c_void_p

eglSurf = eglCreatePbufferSurface(eglDpy, eglCfg, pbufferAttribs)

eglBindAPI = EGL.eglBindAPI
eglBindAPI.argtypes = (c_int,)
eglBindAPI.restype = c_uint

eglBindAPI(EGL_OPENGL_API)

eglCreateContext = EGL.eglCreateContext
eglCreateContext.argtypes = (c_void_p, c_void_p, c_void_p, POINTER(c_int))
eglCreateContext.restype = c_void_p

eglCtx = eglCreateContext(eglDpy, eglCfg, EGL_NO_CONTEXT, None)
if eglCtx is None:
    raise EGLOffScreenException("Could not create context")

eglMakeCurrent = EGL.eglMakeCurrent
eglMakeCurrent.argtypes = (c_void_p, c_void_p, c_void_p, c_void_p)
eglMakeCurrent.restype = c_uint

if not eglMakeCurrent(eglDpy, eglSurf, eglSurf, eglCtx):
    raise EGLOffScreenException("Unable to make context current")

