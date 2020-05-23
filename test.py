import egloffscreen
from OpenGL.GL import *
import numpy as np
import pickle

print(glGetString(GL_VERSION))

fbId = glGenFramebuffers(1)
print("fbId", fbId)

glBindFramebuffer(GL_FRAMEBUFFER, fbId)
print("glBindFramebuffer error", glGetError())

texture = glGenTextures(1)
glBindTexture(GL_TEXTURE_2D, texture)
glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 500, 500, 0, GL_RGB, GL_FLOAT, None)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
print("tex error", glGetError())

glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, texture, 0)

glClearColor(0.2,0.9,0.2,1)
glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

result = glGetTexImagef(GL_TEXTURE_2D, 0, GL_RGB)
print(type(result), result)
pickle.dump(result, open("green.dat", "wb"))

vShaderSrc = """
#version 330 core
layout (location = 0) in vec2 aPos;

out vec2 TexCoords;

void main()
{
    gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0);
    TexCoords = (aPos+1.0)/2.0;
}
"""

fShaderSrc = """
#version 330 core
out vec4 FragColor;

in vec2 TexCoords;

void main()
{
    FragColor = vec4(TexCoords.x, TexCoords.y, 1.0-TexCoords.x/2.0-TexCoords.y/2.0, 1);
}
"""

vShader = glCreateShader(GL_VERTEX_SHADER)
fShader = glCreateShader(GL_FRAGMENT_SHADER)
print("shaders", vShader, fShader)

glShaderSource(vShader, vShaderSrc)
print("glShaderSource error", glGetError())

glCompileShader(vShader)
if not glGetShaderiv(vShader, GL_COMPILE_STATUS):
    print(glGetShaderInfoLog(vShader).decode())
    raise Exception("Can't compile vertex shader")

glShaderSource(fShader, fShaderSrc)
glCompileShader(fShader)
if not glGetShaderiv(fShader, GL_COMPILE_STATUS):
    print(glGetShaderInfoLog(fShader).decode())
    raise Exception("Can't compile fragment shader")

prog = glCreateProgram()
glAttachShader(prog, vShader)
glAttachShader(prog, fShader)
glLinkProgram(prog)
if not glGetProgramiv(prog, GL_LINK_STATUS):
    print(glGetProgramInfoLog(prog).decode())
    raise Exception("Can't link program")


glUseProgram(prog)
aPosBuf = glGenBuffers(1)

vertices = np.array([ -1.0, -1.0,
                 -1.0, 1.0,
                 1.0, -1.0,
                 1.0, 1.0 ], dtype=np.float32)
glBindBuffer(GL_ARRAY_BUFFER, aPosBuf)
glBufferData(GL_ARRAY_BUFFER, vertices, GL_STATIC_DRAW)

aPosLoc = glGetAttribLocation(prog, "aPos")
glVertexAttribPointer(aPosLoc, 2, GL_FLOAT, False, 0, None)
glEnableVertexAttribArray(aPosLoc)

glViewport(0,0,500,500)
glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)
print("draw error", glGetError())

result = glGetTexImagef(GL_TEXTURE_2D, 0, GL_RGB)
print(type(result), result)
pickle.dump(result, open("colors.dat", "wb"))
