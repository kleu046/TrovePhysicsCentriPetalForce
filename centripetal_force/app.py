from shiny.express import input, render, ui
from shiny import reactive
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Circle, Rectangle
import time

time_min: float = 0
time_max: float = 100
time_step: float = 1.5

ui.page_opts(title="Centripetal force", fillable=True)

with ui.nav_panel("What is centripetal force?"):
        with ui.layout_sidebar():
            with ui.sidebar(bg='#29e004'):
                ui.input_slider("time", "Animate", min=time_min, max=time_max,value=time_min, step=time_step, animate=True,)
                
            def calc_pos(r: float, w: float, t: float) -> (float, float):
                return r * np.cos(w * t), r* np.sin(w * t)

            def calc_velocity_vector(r: float, w: float, t:float) -> (float, float):
                return -w * r * np.sin(w * t), w * r * np.cos(w * t)

            plot_width: float = 100.0
            plot_height: float = 100.0
            box_width: float = 30.0
            box_height: float = 30.0
            edge_color: str = 'green'
            face_color: str = 'white'
            path_radius: float = 80
            obj_radius: float = 10
            obj_lw: float = 5

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

            with ui.card(height = 500):
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

                    time_label = f't={input.time()}'
                    ax.text(80,90, time_label, ha='left', fontdict={'size':12,'fontweight':'bold'})

                    ax.set_xlim(-plot_width,plot_width)
                    ax.set_ylim(-plot_height,plot_height)
                    ax.set_aspect('equal')
                    
                    ax.axis('off')

                    return fig

            with ui.card():
                @render.text
                def notes1():
                    return "Centripetal force is not a fundamental force.  It is an apparent force as a result of an object in motion following a circular path."

                @render.text
                def notes2():
                    return "By definition acceleration is change in velocity with respect to time.  As an object moves along a circular path at constant speed its direction changes constantly.  This means that velocity is constantly changing in direction, resulting in acceleration."

                @render.text
                def notes3():
                    return "By drawing the velocity vectors v at a point on the circular path and again after time t, it can easily be shown that the  acceleration points toward the centre of the circular path."

                @render.text
                def notes4():
                    return "At any point on the path of a circular motion, the acceleration point toward the centre, hence the term, centripetal."

                @render.text
                def notes5():
                    return "To understand why centripetal force exist we must consider Newton’s law of inertia.  If no net force is present, an object moving at velocity v tangential to the circular path will continue its path in a straight line at constant speed.  In this case, there would be no circular motion."

                @render.text
                def notes6():
                    return "In order to deviate from the straight line there must be a net force acting on the object.  This force pulls the object toward the centre to maintain the circular motion."

with ui.nav_panel('Banked corners'):

    def calc_y(x: float, angle: float) -> None:
        if  angle <= 60:
            return np.tan(rad(angle)) * x

    def rad(angle: float) -> float:
        return angle / 180 * np.pi

    with ui.layout_sidebar():        
        with ui.sidebar(bg='#29e004'):

            plot_width: float = 100.0
            plot_height: float = 100.0
            angle: float = 0
            mu: float = 0.5
            slope_x: np.array([float,float]) = np.array([0,100])
            edge_color = 'black'
            #face_color = 'lightgrey'
            box_color = 'lightgrey'
            box_height = 36
            box_width = 15
            anchor_x: float = (plot_width - box_width) / 2

            ui.input_slider("angle_slider", "Angle", min=0, max=60, value=angle, step=1)
            ui.input_slider("mu_slider", "Coefficient of friction", min=0, max=1, value=mu, step=0.01)

        def create_rectangle(anchor_x: float, _anchor_y: float, width: float, height: float, angle: float, facecolor = face_color, edgecolor = edge_color) -> matplotlib.patches.Rectangle:
            return Rectangle((anchor_x, _anchor_y), width, height, angle=angle, lw=5, facecolor = facecolor, edgecolor = edgecolor) #use rotation_point parameter default = 'xy' = bottom left corner (x, y) available in later matplotlive versions?

        
        @render.plot
        @reactive.event(input.angle_slider, input.mu_slider)
        def plot2() -> None:
            angle: float = float(input.angle_slider())
            mu: float = float(input.mu_slider())
            
            fig, ax = plt.subplots(figsize=(10,12))
            print(int(input.angle_slider()))
            ax.plot(slope_x, calc_y(slope_x, angle), lw=5, c='darkgrey', zorder=0)

            x: float = anchor_x
            y: float = calc_y(x, angle)

            rect = create_rectangle(x, calc_y(anchor_x, angle), box_width, box_height, angle=angle, facecolor = box_color, edgecolor = edge_color) # angle in degrees
            rect_bottom_centre_x = rect.get_x() + box_width/2 * np.cos(rad(angle))
            rect_bottom_centre_y = calc_y(rect_bottom_centre_x, angle)

            ax.add_patch(rect)

            dy_std = 30

            # weight
            ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=0, dy=-dy_std, shape='full', lw=2, head_width=plot_width/50, color='grey')
            ax.text(rect_bottom_centre_x + 2, rect_bottom_centre_y - 0.5 * dy_std, 'Weight', fontdict={'size':12})

            # normal
            ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=-dy_std*np.sin(rad(angle))*np.cos(rad(angle)), dy=dy_std*np.cos(rad(angle))*np.cos(rad(angle)), shape='full', lw=2, head_width=plot_width/50, color='grey')
            ax.text(rect_bottom_centre_x - dy_std*np.sin(rad(angle)) - 8, rect_bottom_centre_y + dy_std*np.cos(rad(angle)) + 8, 'Normal', fontdict={'size':12})

            ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=-mu*dy_std * np.cos(rad(angle))*np.cos(rad(angle)), dy=-mu*dy_std * np.sin(rad(angle))*np.cos(rad(angle)), shape='full', lw=2, head_width=plot_width/50, color='grey')
            ax.text(rect_bottom_centre_x - mu*dy_std * np.cos(rad(angle)) - 10, rect_bottom_centre_y - mu*dy_std * np.sin(rad(angle)) - 10, 'friction', ha='left', fontdict={'size':12})        

            if angle > 0:
                ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=-dy_std*np.sin(rad(angle)), dy=0, shape='full', lw=2, head_width=plot_width/50, color='blue')
                ax.arrow(rect_bottom_centre_x, rect_bottom_centre_y, dx=-mu*dy_std * np.cos(rad(angle)), dy=0, shape='full', lw=2, head_width=plot_width/50, color='red')


            ax.set_xlim(0,plot_width)
            ax.set_ylim(-40,plot_height)
            ax.set_aspect('equal')
            #ax.axis('off')

            return fig

        with ui.card():
            @render.text
            def notesA():
                return f"Imagine the rectangle being a wheel on a vehicle, moving around a left corner, into the page."

            @render.text
            def notesB():
                return "The only force that would keep the wheel from going off the tangent and follow the circular path is provided by friction between the ground and the tyre.  This when the road is unbanked"

            @render.text
            def notesC():
                return "Lets move the slider to increase angle to 10 degrees.  Now centripetal force as a result of friction has a lesser effect, but the horizontal component of the normal force comes into play."

            @render.text
            def notesC():
                return "In general, direct contribution to centripetal force is much greater by the normal force is much greater than friction.  Now centripetal force is the sum of the horizontal components of friction AND the normal force, which is greater than when the road is not banked.  Since centripetal force is proportional to the speed on a circular path, a vehicle can travel safely around a banked corner at higher speed without going off the road!"

ui.nav_spacer()
