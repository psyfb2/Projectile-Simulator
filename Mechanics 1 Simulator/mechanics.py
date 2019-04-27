import pygame, math
from pygame.locals import *
from os import path
pygame.init()

_FONT = 'VeraSe.ttf'
data_folder = "main_data"

# fonts were originally loaded inside the display_text function but
# this was very inefficient as they would be called atleast 60 times a second
# so now they are loaded once outside of any function placed in a loop
font = pygame.font.Font(path.join(data_folder, _FONT), 15)
font_10 = pygame.font.Font(path.join(data_folder, _FONT), 10)

def display_text(text, size, p, window, centered=False, colour=(0,0,0)):
    if size == 15:
        t = font.render(text, True, colour)
    else:
        t = font_10.render(text, True, colour)
    tpos = t.get_rect()
    if centered:
        # define centre values
        tpos.centerx = p[0]
        tpos.centery = p[1]
    else:
        # else define top left corner values
        tpos.left = p[0]
        tpos.top = p[1]
    window.blit(t, tpos)

def load_image(name, res=None, colourkey=None):
    image = pygame.image.load(path.join(data_folder, name)).convert()
    if res != None:
        # transform resoloution of the image
        image = pygame.transform.scale(image, res)
    if colourkey != None:
        image.set_colorkey(colourkey)
    return image

def display_static_projectile(window, trajectory_colour, trajectory_position, x, y, width, height, colour):
     for coord in trajectory_position:
        pygame.draw.line(window, trajectory_colour, coord, (coord[0]+1, coord[1]+1))
     pygame.draw.ellipse(window, colour, [x, y, width, height])

class Projectile(pygame.sprite.Sprite):
    # input angle in degrees
    # window_width and window_height dont have to be the actual window height or width
    # its just where the walls are placed for the ball to bounce or to check when the ball hits the floor
    def __init__(self, window, FPS=60.0, window_width=800, window_height=600, x=35, y=564,
    width=35, height=35, initial_speed=10, angle=90, xacc=0, yacc=9.8, colour=(255, 0, 0), realtime=True, graphic_name=None, colour_key=None):
        self.window = window
        self.FPS = FPS
        self.window_width = window_width
        self.window_height = window_height
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.xacc = xacc
        self.yacc = yacc # the acceleration in the y has to be the same as acceleration due to gravity
        self.angle = angle
        self.realtime = realtime
        self.initial_speed = initial_speed
        self.xvelocity = math.cos(math.radians(angle)) * initial_speed
        self.yvelocity = math.sin(math.radians(angle)) * initial_speed * -1
        self.initial_xvelocity = self.xvelocity
        self.initial_yvelocity = self.yvelocity
        self.initial_xacc = self.xacc
        self.initial_yacc = self.yacc
        self.initial_x = self.x
        self.initial_y = self.y
        self.font = pygame.font.SysFont("Calibri", 10, True, False)
        self.position = []
        # game_mode variables
        self.offset_position = []
        self.frames = []
        self.future_position = [[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0],[0,0]]
        self.graphic_name = graphic_name
        if graphic_name:
            self.ball = load_image(graphic_name, (width, height), colour_key)

    def wall_bounce(self):
        # Method for detecting when the ball hits the edge of the window
        # and reversing the x/yvelocity's so the ball stays on screen
        if self.x > (self.window_width - (self.width)):
            self.x = (self.window_width - (self.width))
            self.xvelocity = -self.xvelocity

        elif self.x < 0:
            self.x = 0
            self.xvelocity = -self.xvelocity

        if self.y > (self.window_height - (self.height)):
            self.y = (self.window_height - (self.height))
            self.yvelocity = -self.yvelocity

        elif self.y < 0:
            self.y = 0
            self.yvelocity = -self.yvelocity

    def check_floor_collision(self):
        # check to see if the projectile has reached the floor
        if self.y > (self.window_height - (self.height)):
            self.y = (self.window_height - (self.height))
            return True
        return False

    def check_below_point(self, y):
        if self.y < y:
            self.y = y
            return True
        return False

    def is_focused(self, mouse_x, mouse_y):
        if mouse_x >= self.x and mouse_x <= self.x + self.width and mouse_y >= self.y and mouse_y <= self.y + self.height:
            return True
        return False

    def is_moving(self):
        # return whether the ball has any movement as a boolean
        if self.xvelocity == 0 and self.yvelocity == 0: # not moving
            return False
        return True

    def move(self, zoom=1):
        # at 60 fps 60 pixels maps to one real life metre
        # the zoom also effects this at 60 fps and zoom=2 30 pixels will map to one metre
        # so Metres = Pixels / (FPS / Zoom)
        self.xvelocity += ( float(self.xacc) / self.FPS )
        self.yvelocity += ( float(self.yacc) / self.FPS )
        if not self.realtime: # slow motion
            pygame.time.wait(5)
        self.x += self.xvelocity / zoom
        self.y += self.yvelocity / zoom

    def stop(self):
        self.xacc = self.yacc = self.xvelocity = self.yvelocity = 0

    def pause(self):
        self.pause_xvelocity = self.xvelocity
        self.pause_yvelocity = self.yvelocity
        self.pause_xacc = self.xacc
        self.pause_yacc = self.yacc
        self.xacc = self.yacc = self.xvelocity = self.yvelocity = 0

    def start_from_pause(self):
        self.xvelocity = self.pause_xvelocity
        self.yvelocity = self.pause_yvelocity
        self.xacc = self.pause_xacc
        self.yacc = self.pause_yacc

    def restart(self, delete_trajectory=True):
        self.x = self.initial_x
        self.y = self.initial_y
        self.xvelocity = self.initial_xvelocity
        self.yvelocity = self.initial_yvelocity
        self.xacc = self.initial_xacc
        self.yacc = self.initial_yacc
        if delete_trajectory:
            self.position = []
            self.frames = []
            self.offset_position = []

    # set the calculation to be performed to True when using this method
    def calculation(self, starting_height, distance_max_height=False, # starting height is just the starting height of the projectile in metres
    time_max_height=False, range_=False,time_of_flight=False ,detect_max_height=False):

        if distance_max_height:
            if self.angle < 0:
                return starting_height
            return (((self.initial_yvelocity)**2) / (2 * self.initial_yacc)) + starting_height # v^2 = u^2 - 2as

        elif time_max_height:
            if self.angle < 0:
                return 0.0
            return (-self.initial_yvelocity / self.initial_yacc) # v = u + at

        elif range_:
            angle_radians = math.radians(self.angle)
            y0 = math.sqrt(( (self.initial_speed)**2) * ((math.sin(angle_radians))**2) + (2 * self.yacc * starting_height))
            y0 += (self.initial_speed * math.sin(angle_radians))
            return y0 * ( (self.initial_speed * math.cos(angle_radians)) / self.yacc) + 0

        elif time_of_flight:
            angle_radians = math.radians(self.angle)
            t = math.sqrt( (((self.initial_speed * math.sin(angle_radians)))**2) + (2 * self.yacc * starting_height) )
            t += self.initial_speed * math.sin(angle_radians)
            return t / self.yacc

        elif detect_max_height:
            # yvelocity will never exaclty = 0 but it will get very close
            if (self.yvelocity < 1 / self.FPS) and (self.yvelocity > -1 / self.FPS):
                return True
            return False

    def get_speed(self, pause):
        # return the current speed as a scalar quantity
        # pause is used here because if the ball is paused we dont want 0.0 to be returned
        # but instead we want what would have been the speed at the time of the pause to be returned
        if pause:
            return math.sqrt((self.pause_xvelocity)**2 + (self.pause_yvelocity)**2)
        return math.sqrt((self.xvelocity)**2 + (self.yvelocity)**2)

    def draw_trajectory(self, trajectory_colour):
        if self.xvelocity != 0 or self.yvelocity != 0: # stop appending the position of the ball if it is stationary
            self.position.append(((self.x + (self.width/2)), (self.y + (self.height/2))))
        for coord in self.position:
            pygame.draw.line(self.window, trajectory_colour, coord, (coord[0]+1, coord[1]+1))

    def draw_offset_trajectory(self, trajectory_colour, x_offset):
        if self.xvelocity != 0 or self.yvelocity != 0: # stop appending the position of the ball if it is stationary
            self.offset_position.append(((self.x + (self.width/2)), (self.y + (self.height/2)))) # append current middle position of the ball
            for i in range(len(self.frames)): # add one to each element in self.frames
                self.frames[i] += 1
            self.frames.append(0) # add a new element zero
        for i in range(len(self.offset_position)):
            pygame.draw.line(self.window, trajectory_colour, (self.offset_position[i][0] - (self.frames[i] * x_offset), self.offset_position[i][1]), (self.offset_position[i][0]+1 - (self.frames[i] * x_offset), self.offset_position[i][1]+1))

    def draw_angle(self):
        if self.angle >= 0:
            pygame.draw.arc(self.window, self.colour,[self.initial_x+(self.width/2), self.initial_y-(self.height/2), 60, 60] ,
            math.radians(-self.angle/5), math.radians(self.angle+(self.angle/2.5)))

    def draw_start_path(self, speed, angle, height):
        # used in game mode to draw approximatly where the projectile will go as a straight line for the user
        angle = math.radians(angle)
        x_increment = speed * math.cos(angle)
        y_increment = speed * math.sin(angle)
        self.future_position[0][0] = 300
        self.future_position[0][1] = self.window_height - 17
        for i in range(len(self.future_position)-1):
            self.future_position[i+1][0] = self.future_position[i][0] + x_increment
            self.future_position[i+1][1] = self.future_position[i][1] - y_increment
        for coord in self.future_position:
            pygame.draw.line(self.window, (0, 0, 0), (coord[0], coord[1] - height), (coord[0]+1, coord[1]+1 - height))

    def write_text(self, text_colour):
        text=str(self.angle)+" Degrees"
        text = self.font.render(str(text), True, text_colour)
        self.window.blit(text, [self.initial_x + 50 + self.width, self.initial_y])

    def get_distance(self):
        # return how far the ball has moved in the x and y directions from its start position in pixels
        return (self.x - self.initial_x), (self.y - self.initial_y)

    def change_values(self, new_initial_speed, new_angle, new_height):
        # speed, angle and height are to be changed using the sliders
        # so this method is neccesarry to allow the projectile to take these new values
        self.initial_speed = new_initial_speed
        self.xvelocity = math.cos(math.radians(new_angle)) * new_initial_speed
        self.yvelocity = math.sin(math.radians(new_angle)) * new_initial_speed * -1
        self.initial_xvelocity = self.xvelocity
        self.initial_yvelocity = self.yvelocity
        self.angle = new_angle
        # when calculating height use Metres = Pixels / FPS
        # as the input value new_height needs to be the number of pixels below the origin vertically
        self.initial_y = new_height
        self.y = self.initial_y

    def display(self):
        if self.graphic_name:
            self.window.blit(self.ball, [self.x, self.y])
        # ellipse used as it can take float values for its position
        else:
            pygame.draw.ellipse(self.window, self.colour, [self.x, self.y, self.width, self.height])


class StaticProjectile(Projectile):
    def __init__(self, window, trajectory_colour, position, x, y, width, height, colour):
        self.window = window
        self.trajectory_colour = trajectory_colour
        self.position = position
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.colour = colour
        self.graphic_name = None

    def draw_trajectory(self): # overide parent class method
        for coord in self.position:
            pygame.draw.line(self.window, self.trajectory_colour, coord, (coord[0]+1, coord[1]+1))

class slider:
    def __init__(self, window, holder_x, holder_y, holder_colour, holder_width, holder_height, slider_x, slider_y,
    slider_width, slider_height, slider_colour, slider_min_val, slider_max_val, slider_orientation="h"):
        self.window = window
        self.holder_x = holder_x
        self.holder_y = holder_y
        self.holder_colour = holder_colour
        self.holder_width = holder_width
        self.holder_height = holder_height
        self.slider_x = slider_x
        self.slider_y = slider_y
        self.slider_width = slider_width
        self.slider_height = slider_height
        self.slider_colour = slider_colour
        self.new_colour = (0, 255, 0)
        self.change_colour = False
        self.slider_max_val = slider_max_val
        self.slider_min_val = slider_min_val
        self.slider_orientation = slider_orientation

    def display(self, text=None, text_x=None, text_y=None, text_size=None, colour=(0,0,0)):
        if text and text_x and text_y and text_size:
            display_text(text, text_size, (text_x, text_y), self.window, False, colour)
        if not self.change_colour:
            pygame.draw.rect(self.window, self.holder_colour, [self.holder_x, self.holder_y, self.holder_width, self.holder_height]) # holder
            pygame.draw.rect(self.window, self.slider_colour, [self.slider_x, self.slider_y, self.slider_width, self.slider_height]) # slider
        else:
            pygame.draw.rect(self.window, self.holder_colour, [self.holder_x, self.holder_y, self.holder_width, self.holder_height]) # holder
            pygame.draw.rect(self.window, self.new_colour, [self.slider_x, self.slider_y, self.slider_width, self.slider_height]) # slider
            self.change_colour = False

    def slider_event(self, mouse_x, mouse_y, window_width): # call this when a mouse click has been detected to move the slider
        moved = False
        if self.slider_orientation == "h":
            right_limit = self.slider_x + self.slider_width + self.holder_width
            # the right limit can sometimes stretch further then the holder in the x directions depending on the x positon of the slider
            # if there are any buttons adjacent to the slider horizontally it will interfere with the sliders position when the button is clicked
            # so the following if statement ensure right limit doesnt stretch further then the holder
            if right_limit > self.holder_x + self.holder_width:
                right_limit = self.holder_x + self.holder_width
            if (self.slider_x - self.holder_width <= mouse_x <= right_limit) and (self.slider_y <= mouse_y <= self.slider_y + self.slider_height): # slider has been clicked
                self.slider_x = mouse_x - 5 # move the slider
                moved = True
            # check to make sure slider stays within the holder
            if self.slider_x < self.holder_x: # slider is on the left edge of the holder
                self.slider_x = self.holder_x
            elif self.slider_x > window_width - (window_width - (self.holder_x + self.holder_width - self.slider_width)): # slider is on the right edge of the holder
                self.slider_x = window_width - (window_width - (self.holder_x + self.holder_width - self.slider_width))

        elif self.slider_orientation == "v":
            if (self.slider_x <= mouse_x <= self.slider_x + self.slider_width) and (self.holder_y <= mouse_y <= self.holder_y + self.holder_height):
                self.slider_y = mouse_y - 5 # move the slider
                moved = True
            # check to make sure slider stays within the holder
            if self.slider_y < self.holder_y: # slider is on the top edge of the holder
                self.slider_y = self.holder_y
            elif self.slider_y > self.holder_y + self.holder_height - self.slider_height: # slider is on the bottom edge of the holder
                self.slider_y = self.holder_y + self.holder_height - self.slider_height

        return moved

    def detect_mouse_over_slider(self, mouse_x, mouse_y):
         if (self.slider_x - 5 <= mouse_x <= self.slider_x + self.slider_width + 5) and (self.slider_y <= mouse_y <= self.slider_y + self.slider_height):
            return True
         return False

    def change_slider_colour(self, change_colour_to=(0, 255, 0)):
        self.change_colour = True
        self.new_colour = change_colour_to

    def mouse_scroll(self, direction):
        if self.slider_orientation == "v":
            if direction == "up":
                self.slider_y -= 5
            elif direction == "down":
                self.slider_y += 5

            # check to make sure slider stays within the holder
            if self.slider_y < self.holder_y: # slider is on the top edge of the holder
                self.slider_y = self.holder_y
            elif self.slider_y > self.holder_y + self.holder_height - self.slider_height: # slider is on the bottom edge of the holder
                self.slider_y = self.holder_y + self.holder_height - self.slider_height

    def scale(self): # call this method when the slider has moved
        if self.slider_orientation == "h":
            if self.slider_x > self.holder_x:
                # the slider_x is more then the holder_x so
                # a ratio can be calculated between the width of the holder and the current position of the slider_x
                # relative to the holder
                percent = float(self.slider_x + self.slider_width - self.holder_x) / self.holder_width
            else:
                percent = float(self.slider_x - self.holder_x) / self.holder_width
            total = (self.slider_max_val + abs(self.slider_min_val)) # total range of the slider
            value = (percent * total) # find the product of the percentage and total range of the slider to give an appropriate value
            if self.slider_min_val == 0:
                return value # value doesnt need to be changed because the value is already accurate
            if value > (total / 2.0):
                return (value - (total / 2.0))
            elif value < (total / 2.0):
                return (value - (total / 2.0) )
            else:
                return 0

        elif self.slider_orientation == "v":
            # this is the same as slider_orientation "h" but with width and x values replaced with height and y values
            if self.slider_y > self.holder_y:
                percent = float(self.slider_y + self.slider_height - self.holder_y) / self.holder_height
            else:
                percent = float(self.slider_y - self.holder_y) / self.holder_height
            total = (self.slider_max_val + abs(self.slider_min_val))
            value = (percent * total)
            if self.slider_min_val == 0:
                return value
            if value > (total / 2.0):
                return (value - (total / 2.0))
            elif value < (total / 2.0):
                return (value - (total / 2.0) )
            else:
                return 0

class Button:
    def __init__(self, window, button_x, button_y, button_width, button_height, button_colour,
    button_text, button_text_size, shadow_lines=True):
        self.window = window
        self.button_x = button_x
        self.button_y = button_y
        self.button_width = button_width
        self.button_height = button_height
        self.button_colour = button_colour
        self.button_text = button_text
        self.button_text_size = button_text_size
        self.rect = pygame.Rect(self.button_x, self.button_y, self.button_width, self.button_height)
        self.status = 0
        self.new_colour = (0, 255, 0)
        self.change_colour = False
        self.shadow_lines = shadow_lines

    def display(self, text_colour=(0,0,0)):
        if not self.change_colour:
            pygame.draw.rect(self.window, self.button_colour, self.rect)
        else:
            pygame.draw.rect(self.window, self.new_colour, self.rect)
            self.change_colour = False
        if self.shadow_lines:
            # draw some shadow lines
            pygame.draw.line(self.window, (0, 0, 0), (self.button_x, self.button_y), (self.button_x+self.button_width, self.button_y)) # top horizontal

            pygame.draw.line(self.window, (0, 0, 0), (self.button_x, self.button_y+self.button_height), # bottom horizontal
            (self.button_x+self.button_width, self.button_y+self.button_height))

            pygame.draw.line(self.window, (0, 0, 0), (self.button_x, self.button_y), (self.button_x, self.button_y+self.button_height)) # left vertical

            pygame.draw.line(self.window, (0, 0, 0), (self.button_x+self.button_width, self.button_y), # right horizontal
            (self.button_x+self.button_width, self.button_y+self.button_height))

        # display text in the middle of the button
        if self.button_text:
            display_text(self.button_text, self.button_text_size, (self.button_x + (self.button_width/2.0),
            (self.button_y + (self.button_height/2.0)) ) ,self.window, True, text_colour)

    def press(self):
        self.rect.inflate_ip(-6,-6) # give the appreance that the button is being pressed
        self.status = 1

    def unpress(self):
        self.rect.inflate_ip(6,6) # give the appreance that the button is being unpressed
        self.status = 0

    def is_focused(self,mouse_x, mouse_y): # check to see if the mouse position is on the button
        return self.rect.collidepoint(mouse_x,mouse_y) # returns boolean

    def change_button_colour(self, change_colour_to=(0,255,0)):
        self.change_colour = True
        self.new_colour = change_colour_to

class Text_box:
    """Class to display a text box to allow the user to input data"""
    def __init__(self, window, x, y, width, height, cap):
        self.window = window
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cap = cap # maximum number of characters text_box can store
        self.text = "" # used to store each character

    def display(self):
        # draw a box
        pygame.draw.line(self.window, (0, 0, 0), (self.x, self.y), (self.x+self.width, self.y)) # top horizontal

        pygame.draw.line(self.window, (0, 0, 0), (self.x, self.y+self.height), # bottom horizontal
        (self.x+self.width, self.y+self.height))

        pygame.draw.line(self.window, (0, 0, 0), (self.x, self.y), (self.x, self.y+self.height)) # left vertical

        pygame.draw.line(self.window, (0, 0, 0), (self.x+self.width, self.y), # right horizontal
        (self.x+self.width, self.y+self.height))

        display_text(self.text, 15,(self.x+3, self.y+(self.height/2)), self.window) # display the text in the text box

    def add_char(self, char):
        # call this when a key stroke is detected from the user so that it can be displayed in the text box
        if len(self.text) < self.cap: # ensure the characterlimit isnt exceeded
            self.text = self.text + str(char)

    def backspace(self):
        # call this when a backspace event is detected from the user, the last character will be removed
        self.text = self.text[:-1]

    def clear(self):
        # reset the text box so that there is no text in it
        self.text = ""

class Pipe(pygame.sprite.Sprite):
    """Sub Class for the pipes in game mode.These will have to be able detect collisions with other objects so pygame sprite class is inherited"""
    def __init__(self, x, y, orientation, res=None):
        super(Pipe, self).__init__() # call the parent class contructor to allow sprites to initialize
        if orientation == "up":
            self.image = load_image("pipe.png", res)
        else:
            self.image = load_image("pipe_upsidedown.png", res)
        self.rect = self.image.get_rect() # get the dimensions of the image as (x, y, width, height) which can be changed through the program
        self.rect.x = x
        self.rect.y = y
        self.orientation = orientation

    def collision(self, x, y): # check to see if a coordinate is in the pipe rect
    # check to see which part the coordinate has collided with either the pipes long side or its short side
        if self.rect.collidepoint(x, y):
            if self.orientation == "up":
                if y < self.rect.y + 25:
                    return "bottom"
                else:
                    return "side"
            else:
                if y > self.rect.y+self.rect.height - 25:
                    return "bottom"
                else:
                    return "side"

    def reset(self, x):
        # reset the x position of the pipe call when the x position is negative (the pipe has gone out of the screen)
        self.rect.x = x
