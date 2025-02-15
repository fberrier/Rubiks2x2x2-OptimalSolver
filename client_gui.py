# ################ A simple graphical interface which communicates with the server #####################################

from tkinter import *
import socket
import rubiks.thirdparties.hkociemba.face as face
import ubiks.thirdparties.hkociemba.cubie as cubie

# ################################ Edit the following line to use different colors #####################################
cols = ("yellow", "green", "red", "white", "blue", "orange")
########################################################################################################################

# ################################## some global variables and constants ###############################################
DEFAULT_HOST = 'localhost'
DEFAULT_PORT = '8080'
width = 60  # width of a facelet in pixels
facelet_id = [[[0 for col in range(2)] for row in range(2)] for face in range(6)]
colorpick_id = [0 for i in range(6)]
curcol = None
t = ("U", "R", "F", "D", "L", "B")
########################################################################################################################

# ################################################ Diverse functions ###################################################


def show_text(txt):
    """Displays messages."""
    print(txt)
    display.insert(END, txt)
    root.update_idletasks()


def create_facelet_rects(a):
    """Initializes the facelet grid on the canvas"""
    offset = ((1, 0), (2, 1), (1, 1), (1, 2), (0, 1), (3, 1))
    for f in range(6):
        for row in range(2):
            y = 20 + offset[f][1] * 2 * a + row * a
            for col in range(2):
                x = 20 + offset[f][0] * 2 * a + col * a
                facelet_id[f][row][col] = canvas.create_rectangle(x, y, x + a, y + a, fill="grey")
                if row == 1 and col == 1:
                    canvas.create_text(x, y, font=("", 14), text=t[f], state=DISABLED)


def create_colorpick_rects(a):
    """Initializes the "paintbox" on the canvas"""
    global curcol
    global cols
    for i in range(6):
        x = (i % 3)*(a+5) + 5*a
        y = (i // 3)*(a+5) + 5*a
        colorpick_id[i] = canvas.create_rectangle(x, y, x + a, y + a, fill=cols[i])
        canvas.itemconfig(colorpick_id[0], width=4)
        curcol = cols[0]


def get_definition_string():
    """Generates the cube definition string from the facelet colors."""
    color_to_facelet = {}
    for i in range(6):
        color_to_facelet.update({cols[i]: t[i]})
    s = ''
    for f in range(6):
        for row in range(2):
            for col in range(2):
                s += color_to_facelet[canvas.itemcget(facelet_id[f][row][col], "fill")]
    return s
########################################################################################################################

# ############################### Solve the displayed cube with a local or remote server ###############################


def solve():
    """Connects to the server and returns the solving maneuver"""
    display.delete(1.0, END)  # clear output window
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        show_text('Failed to create socket')
        return
    # host = 'f9f0b2jt6zmzyo6b.myfritz.net'  # my RaspberryPi, if online
    host = txt_host.get(1.0, END).rstrip()  # default is localhost
    port = int(txt_port.get(1.0, END))  # default is port 8080

    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        show_text('Hostname could not be resolved.')
        return
    try:
        s.connect((remote_ip, port))
    except:
        show_text('Cannot connect to server!')
        return
    show_text('Connected with ' + remote_ip + '\n')
    try:
        defstr = get_definition_string()+'\n'
    except:
        show_text('Invalid facelet configuration.\nWrong or missing colors.')
        return
    # show_text(defstr)
    try:
        s.sendall((defstr+'\n').encode())
    except:
        show_text('Cannot send cube configuration to server.')
        return
    show_text(s.recv(10000).decode())  # big buffer because we return all solutions (196 solutions in "worst" case)
########################################################################################################################

# ################################# Functions to change the facelet colors #############################################


def clean():
    """Restores the cube to a clean cube."""
    for f in range(6):
        for row in range(2):
            for col in range(2):
                canvas.itemconfig(facelet_id[f][row][col], fill=cols[f])


def empty():
    """Removes the facelet colors."""
    for f in range(6):
        for row in range(2):
            for col in range(2):
                canvas.itemconfig(facelet_id[f][row][col], fill="grey")


def random():
    """Generates a random cube and sets the corresponding facelet colors."""
    cc = cubie.CubieCube()
    cc.randomize()
    fc = cc.to_facelet_cube()
    idx = 0
    for f in range(6):
        for row in range(2):
            for col in range(2):
                canvas.itemconfig(facelet_id[f][row][col], fill=cols[fc.f[idx]] )
                idx += 1
########################################################################################################################

# ################################### Edit the facelet colors ##########################################################


def click(event):
    """Defines how to react on left mouseclicks."""
    global curcol
    idlist = canvas.find_withtag("current")
    if len(idlist) > 0:
        if idlist[0] in colorpick_id:
            curcol = canvas.itemcget("current", "fill")
            for i in range(6):
                canvas.itemconfig(colorpick_id[i], width=1)
            canvas.itemconfig("current", width=5)
        else:
            canvas.itemconfig("current", fill=curcol)
########################################################################################################################

#  ###################################### Generate and display the TK_widgets ##########################################
root = Tk()
root.wm_title("Solver Client")
canvas = Canvas(root, width=10 * width + 20, height=7.5 * width + 20)
canvas.pack()

bsolve = Button(text="Solve", height=2, width=10, relief=RAISED, command=solve)
bsolve_window = canvas.create_window(10 + 8.5 * width, 10 + 4.5 * width, anchor=NW, window=bsolve)
bclean = Button(text="Clean", height=1, width=10, relief=RAISED, command=clean)
bclean_window = canvas.create_window(10 + 8.5 * width, 10 + 5.5 * width, anchor=NW, window=bclean)
bempty = Button(text="Empty", height=1, width=10, relief=RAISED, command=empty)
bempty_window = canvas.create_window(10 + 8.5 * width, 10 + 6 * width, anchor=NW, window=bempty)
brandom = Button(text="Random", height=1, width=10, relief=RAISED, command=random)
brandom_window = canvas.create_window(10 + 8.5 * width, 10 + 6.5 * width, anchor=NW, window=brandom)
display = Text(height=7, width=39)
text_window = canvas.create_window(10 + 4.5 * width, 10 + 0 * width, anchor=NW, window=display)
hp = Label(text='    Hostname and Port')
hp_window = canvas.create_window(10 + 0 * width, 10 + 6.1 * width, anchor=NW, window=hp)
txt_host = Text(height=1, width=20)
txt_host_window = canvas.create_window(10 + 0 * width, 10 + 6.5 * width, anchor=NW, window=txt_host)
txt_host.insert(INSERT, DEFAULT_HOST)
txt_port = Text(height=1, width=20)
txt_port_window = canvas.create_window(10 + 0 * width, 10 + 7 * width, anchor=NW, window=txt_port)
txt_port.insert(INSERT, DEFAULT_PORT)
canvas.bind("<Button-1>", click)
create_facelet_rects(width)
create_colorpick_rects(width)
clean()
root.mainloop()
########################################################################################################################

