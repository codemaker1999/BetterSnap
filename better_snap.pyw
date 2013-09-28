from win32gui import EnumWindows,GetWindowRect,SetWindowPos
from win32gui import MessageBox as mbox
from win32api import GetSystemMetrics
import exceptions as ex
import sys

# The default width, in pixels, of a maximized top-level
#   window on the primary display monitor (61)
w_maxed = GetSystemMetrics(61)
# The default height, in pixels, of a maximized top-level
#   window on the primary display monitor (62)
h_maxed = GetSystemMetrics(62)-15
# The width of the screen of the primary display monitor,
#   in pixels (0)
w = GetSystemMetrics(0)
# The height of the screen of the primary display monitor,
#   in pixels (1)
h = GetSystemMetrics(1)

# Params (read from cfg file)
try:
    cfg=open('settings.cfg','r')
except ex.IOError as e:
    mbox(0,'Could not open settings.cfg','Error',0)
    sys.exit()

#Parse file
params={}
readflag=0
for line in cfg:
    if readflag:
        params[s]=int(line)
        readflag=0
    elif line.startswith('['):
        readflag=1
        s=line

#Try to assign values
try:
    m=params['[cols]\n']
    n=params['[rows]\n']
    brd=params['[border]\n']
except ex.KeyError as e:
    mbox(0,'File settings.cfg not properly formatted','Error',0)
    sys.exit()

# dx and dy are counts of the pixels per chunk
dx=w_maxed/m
dy=h_maxed/n

# Snap a window
def window_snap(hwnd, spam):
    '''Snap window with handle hwnd to nearest multiple of dx and dy'''
    global dx,dy,w_maxed,h_maxed,brd
    #Find window corners
    (left,top,right,bottom)=GetWindowRect(hwnd)

    #If Window Maximaized, do nothing and return
    if (right-left,bottom-top)==(w_maxed,h_maxed):
        return

    # Note: window borders are 8px, and we want to overlap them
    
    # Update Left Coord
    left_squares=left/float(dx)
    left_sq_floor=int(left_squares)
    if left_squares-left_sq_floor < 0.5:
        new_left = dx*left_sq_floor - brd
    else:
        new_left = dx*(left_sq_floor+1) - brd

    # Update right Coord
    right_squares=right/float(dx)
    right_sq_floor=int(right_squares)
    if right_squares-right_sq_floor < 0.5:
        new_right = dx*right_sq_floor
    else:
        new_right = dx*(right_sq_floor+1)

    # Update top Coord
    top_squares=top/float(dy)
    top_sq_floor=int(top_squares)
    if top_squares-top_sq_floor < 0.5:
        new_top = dy*top_sq_floor
    else:
        new_top = dy*(top_sq_floor+1)

    # Update bottom Coord
    bottom_squares=bottom/float(dy)
    bottom_sq_floor=int(bottom_squares)
    if bottom_squares-bottom_sq_floor < 0.5:
        new_bottom = dy*bottom_sq_floor + brd
    else:
        new_bottom = dy*(bottom_sq_floor+1) + brd
    
    #Handle sizing errors
    if (new_left > w_maxed):
        #sub 100 since we need room for right of window
        new_left = w_maxed-2*dx-brd
    elif (new_left < 0):
        new_left = 0

    if (new_right >= w_maxed):
        new_right = w_maxed+brd
    elif (new_right < 0):
        new_right = 0+2*dx

    if (new_top > h_maxed):
        new_top = h_maxed-2*dy
    elif (new_top < 0):
        new_top = 0

    if (new_bottom > h_maxed+brd):
        new_bottom = h_maxed+brd
    elif (new_bottom < 0):
        new_bottom = 0+2*dx

    #Resize the window
    cx=new_right-new_left
    cy=new_bottom-new_top
    # 0 is a z-order; 0x0004 tells SWP to keep the original z-order
    SetWindowPos(hwnd,0,new_left,new_top,cx,cy,0x0004)

#Get all window handles and resize
EnumWindows(window_snap, None)
