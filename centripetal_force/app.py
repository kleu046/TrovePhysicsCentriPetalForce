from shiny.express import input, render, ui
from shiny import reactive
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
import time

plot_width: float = 100.0
plot_height: float = 100.0
plot_x_min: float = -10
plot_y_min: float = -10
box_width: float = 30.0
box_height: float = 30.0
edge_color: str = 'green'
face_color: str = 'white'
path_radius: float = 80
obj_radius: float = 10
obj_lw: float = 5
time_min: float = 0
time_max: float = 100
time_step: float = 0.5
fig_size: tuple = (10, 12)
obj_omega: float = 0.2 # angular velocity

def calc_y(x: float) -> None:
    y = np.sqrt(path_radius**2 - x**2)
    return y

def create_circle(centre_x: float, centre_y: float, obj_radius: float) -> matplotlib.patches.Circle:
    return Circle((centre_x, centre_y), radius=obj_radius, lw=obj_lw, facecolor = face_color, edgecolor = edge_color)

centre_x: float = path_radius
centre_y: float = calc_y(centre_x)

path_x: np.array = np.linspace(plot_x_min, path_radius, 100)
path_y = [calc_y(x) for x in path_x]

ui.page_opts(title="Centripetal force",) # fillable=True)

with ui.sidebar(style='background:#09AAFF'):
    ui.input_slider("time", "Animate", min=time_min, max=time_max,value=time_min, step=time_step, animate=True)

@reactive.effect
@reactive.event(input.time)
def calc_pos() -> None:
    # calculate centre_x and centre_y using input.time
    global centre_x
    global centre_y
    
    t: float = float(input.time())
    centre_x = path_radius * np.cos(obj_omega * t)
    if centre_x < 0:
        centre_x = path_radius
        ui.update_slider('time', value=0)
    centre_y = calc_y(centre_x)

@reactive.effect
@reactive.event(input.time)
def calc_velocity_vector() -> None:
    # calculate velocity based on radius, omega and time
    t: float = float(input.time())
    v_x = centre_x - path_radius * np.sin(obj_omega * t) / 10
    v_y = centre_y + path_radius * np.cos(obj_omega * t) / 10
    print(v_x, v_y)
    return v_x, v_y

@render.plot
@reactive.event(input.time)
def plot() -> None:
    fig, ax = plt.subplots(figsize=fig_size)

    # draw a small circle with a circular path
    #print(f'error: x = {centre_x}, y = {calc_y(centre_x)}')

    ax.plot(path_x, path_y, lw=2, color='black', zorder=0)

    circle = create_circle(centre_x, centre_y, obj_radius)
    ax.add_patch(circle)
    
    # ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=0, dy=-dy_std, shape='full', lw=2, head_width=plot_width/50)
    # ax.text(rect_bottom_centre_x + 2, rect_bottom_centre_y - 0.5 * dy_std, f'{str(round(w, 1))} N', fontdict={'size':12})

    ax.set_xlim(plot_x_min,plot_width)
    ax.set_ylim(plot_y_min,plot_height)
    ax.set_aspect('equal')
    #ax.axis('off')

    return fig

with ui.card():
    @render.text
    def notes1():
        return f"Explain centripetal force"
