### egloffscreen

This is a simple Python module to be able to do offscreen/headless OpenGL
things without needing e.g. the DISPLAY environment variable to be set
on an X11 system.

The code is based on https://forums.developer.nvidia.com/t/egl-without-x11/58733/4 ,
which itself was inspired by https://devblogs.nvidia.com/egl-eye-opengl-visualization-without-x-server/

The 'old' subdirectory is an initial version, using basically the C++ code that
was shown in the forum, using Cython to make Python bindings. The current version
uses ctypes to accomplish the same thing.

Loading the module initializes the EGL subsystem and creates and activates a 
single context. The test program then uses PyOpenGL to actually make OpenGL 
calls. To make sure that PyOpenGL also uses EGL (instead of GLX for example), 
the environment variable PYOPENGL_PLATFORM is set to 'egl'. 

The test program renders to a texture, of which the pixels are retrieved
and stored in a numpy array. This is subsequently pickled and saved to a file.
On a system that does use a graphical interface, these pickled numpy arrays
can be visualized using the plot script.

This allows me to do OpenGL based calculations on a supercomputer, to which
one needs to log on using SSH, and submit jobs using qsub.
