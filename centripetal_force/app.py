from shiny.express import input, render, ui
from shiny import reactive
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import time

plot_width: float = 100.0
plot_height: float = 100.0
box_width: float = 30.0
box_height: float = 30.0
edge_color: str = 'green'
face_color: str = 'white'
path_radius: float = 80
obj_radius: float = 10
obj_lw: float = 5
time_min: float = 0
time_max: float = 100
time_step: float = 2
fig_size: tuple = (10, 12)
obj_omega: float = 0.5 # angular velocity
lightgrey: list = ['#888888','#999999','#aaaaaa','#bbbbbb','#cccccc','#dddddd','#eeeeee','#ffffff']


def create_circle(centre: (float,float), obj_radius: float, **kwargs) -> matplotlib.patches.Circle:
    return Circle(centre, radius=obj_radius, lw=obj_lw, **kwargs)

centre_x: float = path_radius
centre_y: float = 0

x = np.linspace(-path_radius, path_radius, 100)
y = [np.sqrt(path_radius**2 - x_e**2) for x_e in x]
path_x = np.hstack([x, x[::-1]])
path_y = np.hstack([y,  [-1 * y_e for y_e in y][::-1]])

v_x: float = 0
v_y: float = obj_omega * path_radius

ui.page_opts(title="Centripetal force", fillable=True)

with ui.sidebar(bg='#29e004'):
    ui.input_slider("time", "Animate", min=time_min, max=time_max,value=time_min, step=time_step, animate=True,)

def calc_pos(r: float, w: float, t: float) -> (float, float):
    return r * np.cos(w * t), r* np.sin(w * t)

def calc_velocity_vector(r: float, w: float, t:float) -> (float, float):
    return -w * r * np.sin(w * t), w * r * np.cos(w * t)

@reactive.effect
@reactive.event(input.time)
def set_pos() -> None:
    # calculate centre_x and centre_y using input.time
    global centre_x
    global centre_y
    
    t: float = float(input.time())
    centre_x, centre_y_new = calc_pos(path_radius, obj_omega, t)
    if (centre_y_new > 0 and centre_y < 0) or ((input.time() - time_step) >= len(lightgrey)):
        centre_y = 0
        centre_x = path_radius
        ui.update_slider('time',value=0)
    else:
        centre_y = centre_y_new

@reactive.effect
@reactive.event(input.time)
def set_velocity_vector() -> None:
    global v_x
    global v_y

    t: float = float(input.time())
    v_x, v_y = calc_velocity_vector(path_radius, obj_omega, t)

@render.plot
@reactive.event(input.time)
def plot() -> None:
    # draw a small circle with a circular path
    fig, ax = plt.subplots(figsize=fig_size)
    ax.plot(path_x, path_y, lw=10, color='#f0ff0f', zorder=0)

    counter = 0
    n = input.time() - time_step
    while n > 0 and counter < len(lightgrey):
        grey_centre = calc_pos(path_radius, obj_omega, n)
        grey_circle = create_circle(grey_centre, obj_radius, facecolor = face_color, edgecolor =lightgrey[counter])
        ax.add_patch(grey_circle)
        
        grey_velocity = calc_velocity_vector(path_radius, obj_omega, n)
        ax.arrow(grey_centre[0] , grey_centre[1], dx=grey_velocity[0], dy=grey_velocity[1], shape='full', color=lightgrey[counter], lw=2, head_width=plot_width/50)
        n -= time_step
        counter += 1

    circle = create_circle((centre_x, centre_y), obj_radius, facecolor = face_color, edgecolor = edge_color)
    ax.add_patch(circle)
    ax.arrow(centre_x, centre_y, dx=v_x, dy=v_y, shape='full', lw=2, head_width=plot_width/50)
    ax.text((centre_x + v_x) / 0.9, (centre_y + v_y)/0.9, 'v', fontdict={'size':12,'fontweight':'bold'})
    ax.arrow(centre_x, centre_y, dx=0-centre_x, dy=0-centre_y, shape='full', lw=3, head_width=plot_width/30)
    ax.text((centre_x + v_x/2)* 0.5, (centre_y + v_y/2) * 0.5, 'a', fontdict={'size':12,'fontweight':'bold'})

    #ax.text(rect_bottom_centre_x + 2, rect_bottom_centre_y - 0.5 * dy_std, f'{str(round(w, 1))} N', fontdict={'size':12})

    ax.set_xlim(-plot_width,plot_width)
    ax.set_ylim(-plot_height,plot_height)
    ax.set_aspect('equal')
    
    #ax.axis('off')

    return fig

with ui.card():
    @render.text
    def notes1():
        return f"Explain centripetal force"
