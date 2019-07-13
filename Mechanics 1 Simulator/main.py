import pygame, mechanics # pygame GUI module
from os import path # use os to allow us to access data_folder
from pygame.locals import *
from win32api import GetSystemMetrics # use win32api to allow us to get monitor resoloution
import random
pygame.mixer.pre_init(44100, -16, 2, 2048)
pygame.init()

data_folder = "main_data"
save_file = path.join(data_folder, "saved.txt")
leaderboard = path.join(data_folder, "leaderboard.txt")

# Global Constants and Variables
FPS = 60.0
SIZE = (GetSystemMetrics(0), GetSystemMetrics(1)) # collect the (width, height) of the monitor
WIDTH, HEIGHT = SIZE[0], SIZE[1]

flags = FULLSCREEN | DOUBLEBUF
window = pygame.display.set_mode(SIZE, flags)
pygame.display.set_caption("Projectile Simulator")
clock = pygame.time.Clock()

# define global rects which will be used in many subroutines
menu_rect = pygame.Rect(WIDTH-130, 40, 130, 290)
save_menu_rect = pygame.Rect((WIDTH/2)-125, (HEIGHT/2)-125, 250, 250)
saved_rect = pygame.Rect([(WIDTH/2)-125, (HEIGHT/2)-125, 250, 100])
text_y = HEIGHT - 135

# load any bit mapped graphics and sounds
earth = mechanics.load_image("earth2.png", (50, 50), (255, 255, 255))
mars = mechanics.load_image("mars2.png", (50, 50), (255, 255, 255))
bg = mechanics.load_image("bg.png", (WIDTH, HEIGHT-300))

sound = True
try: # try and except to prevent program from halting if the user has no audio output device
    click_sound = pygame.mixer.Sound(path.join(data_folder, "click2.wav"))
    ding_sound = pygame.mixer.Sound(path.join(data_folder, "ding.ogg"))
except Exception:
    sound = False

exit_button = mechanics.Button(window, WIDTH-40, 0, 40, 20, (180, 0, 0), "X", 15)
back_button = mechanics.Button(window, 0, HEIGHT-50, 80, 50, (180, 0, 0), "Back", 15)

def save_projectile(file_name, name, initial_speed, angle, height):
    """Subroutine to save initial values of projectile (initial speed, angle and height) in a text file"""
    write_to = open(file_name, "a") # open the filename with append mode so previous data in the file arent deleted
    # "-" symbol used to indicate the next data item in the text file
    # so if projectile with name "p" was saved with values 12,45,0 where saved it would look like
    # p-12-45-0
    write_to.write(name+"-"+str(initial_speed)+"-"+str(angle)+"-"+str(height)+"\n")
    write_to.close()

def load_projectile(file_name, name):
    """Function to return initial values of a saved projectile (initial speed, angle and height) from a text file"""
    load_from = open(file_name, "r") # open the filename with the read mode
    name_len = len(name)
    found = False
    # first find the given name in the text file
    for line in load_from.readlines(): # get all the lines from the file as a list
        if name in line:
            # the position in the line of each value is known so string slicing can be used to gather them
            initial_speed, angle, height = line[1+name_len:5+name_len], line[6+name_len:10+name_len], line[11+name_len:14+name_len]
            found = True
            break
    load_from.close()
    if found:
        return float(initial_speed), float(angle), float(height)

def metre_to_pixels(height, zoom):
    """Subroutine to convert a given height in Metres to Pixels"""
    # To convert between Metres and pixels use:
    # Meters = Pixels / FPS
    # at 60 fps 60 pixels maps to one real life metre
    # the zoom also effects this at 60 fps and zoom=2 30 pixels will map to one metre
    # so Metres = Pixels / (FPS / Zoom) or Pixels = Metres * (FPS / Zoom)
    # the change_values only takes pixels below the top of the screen as an argument
    # so the height of where the ball will start in metres needs to be converted to pixels below the top of the screen
    return ((HEIGHT-185)-(height * (FPS / (zoom+1))))

def display_height(y1, y2, colour, height):
    """Subroutine to display the initial vertical height of a projectile"""
    pygame.draw.line(window, colour, (35, y1), (35, y2), 3) # display the vertical line representing the height
    pygame.draw.polygon(window, colour, ((20, y2), (35, y2+15), (50, y2)))
    mechanics.display_text(str(height)+" M", 15, (35, y2-10), window, True, (0, 200, 0))

def settings_menu(window, colour, live_data_button, ball_colour_button, trajectory_button, trajectory_colour_button, information_button,earth_button, mars_button):
    """Subroutine to display settings dropdowm menu"""
    pygame.draw.line(window, colour, (WIDTH-65, 20), (WIDTH-65, 40), 3)
    pygame.draw.rect(window, colour, menu_rect)
    live_data_button.display()
    ball_colour_button.display()
    trajectory_button.display()
    trajectory_colour_button.display()
    information_button.display()
    earth_button.display()
    mars_button.display()
    window.blit(earth, [WIDTH-130, 260])
    window.blit(mars, [WIDTH-65, 260])
    mechanics.display_text("g=9.8",10,(WIDTH-120, 310), window)
    mechanics.display_text("g=3.711",10,(WIDTH-60, 310), window)

def save_menu(window, colour, xy, initial_speed, angle, height, save_button2, text_box):
    """Subroutine to display save menu"""
    x, y = xy
    pygame.draw.rect(window, colour, save_menu_rect)
    # draw the text
    mechanics.display_text("NAME : ",15,((WIDTH/2)-125, (HEIGHT/2)-100), window)
    mechanics.display_text("Speed : "+str(initial_speed),10,((WIDTH/2)-125, (HEIGHT/2)+40), window)
    mechanics.display_text("Angle : "+str(angle),10,((WIDTH/2)-125, (HEIGHT/2)+70), window)
    mechanics.display_text("Height : "+str(height),10,((WIDTH/2)-125, (HEIGHT/2)+100), window)
    # draw the buttons
    if save_button2.is_focused(x, y): save_button2.change_button_colour()
    save_button2.display()
    text_box.display()

def load_menu(window, colour, xy, load_button2, text_box):
    """Subroutine to display load menu"""
    x, y = xy
    pygame.draw.rect(window, colour, save_menu_rect)
    # draw the text
    mechanics.display_text("NAME : ",15,((WIDTH/2)-125, (HEIGHT/2)-100), window)
    # draw the buttons
    if load_button2.is_focused(x, y): load_button2.change_button_colour()
    load_button2.display()
    text_box.display()

def saved(window, colour):
    """Subroutine to display a confirmation that the game has been saved after the user clicks the save2 button"""
    pygame.draw.rect(window, colour, saved_rect)
    mechanics.display_text("PROJECTILE SAVED!",15,((WIDTH/2), (HEIGHT/2)-80), window, True)

def get_lowest_score(file_name):
    """Function to return the lowest score (numerical value) from the leaderboard"""
    load_from = open(file_name)
    lines = load_from.readlines()
    # incase the text file doesnt have any high scores check this to stop an error
    if len(lines) == 0:
        load_from.close()
        return None
    # the last line (fifth line since the text file will only hold top 5 scores)
    # in the text file will contain the lowest score
    # as when the scores are saved they are saved in order biggest to smallest
    load_from.close()
    line_num = len(lines) - 1 # this is the last line in the text file which will contain the lowest score
    return int(lines[line_num].split(" ",1)[0]) # return the number (score) before the first space as an int

def insert_line(filename, index, value):
    """Subroutine to insert a line in a text file then move every other line down one"""
    load_from = open(filename, "r")
    contents = load_from.readlines() # get all lines in text file as list of lines
    load_from.close()

    contents.insert(index, value) # insert a value in contents list at position index

    write_to = open(filename, "w")
    contents = "".join(contents) # join contents into one string
    write_to.write(contents) # write this to write_to
    write_to.close() # close the text file

def remove_lowest_score(file_name):
    """Subroutine to remove the lowest score (last line of the leaderboard) from the leaderboard"""
    load_from = open(file_name, "r")
    lines = load_from.readlines() # get all the lines from load_from in a list
    load_from.close()

    lines = lines[:-1] # remove last item in the list lines

    write_to = open(file_name, "w")
    contents = "".join(lines) # join contents into one string
    write_to.write(contents)
    write_to.close()

def get_score_line(file_name, score):
    """Function to return which line the new score needs to go in"""
    lines = open(file_name, 'r').readlines() # get all the lines from load_from in a list
    for i in range(len(lines)): # for i=0 to the number of lines in the file
        if int(lines[i].split(" ",1)[0]) < score: # if the score in that line is less then the current score
            return i # return i because this is the line we want to replace

def load_leaderboard(window, file_name):
    load_from = open(file_name, "r")
    x = 0
    for line in load_from.readlines():
        # in the text file it saves score then name like this: 20 fady
        # The score needs to be displayed like this: fady 20
        # so split the string around the first space and swap
        line = line.strip("\n")
        mechanics.display_text(line.split(" ",1)[1], 15,((WIDTH/2)-250, (HEIGHT/2)-115 + x), window, False)
        mechanics.display_text(line.split(" ",1)[0], 15,((WIDTH/2)-100, (HEIGHT/2)-115 + x), window, False)
        x += 25
    load_from.close()

def add_to_leaderboard(file_name, name, score):
    write_to = open(file_name, "a") # open the filename with append mode so previous data in the file arent deleted
    load_from = open(file_name, "r")
    lines_len = len(load_from.readlines())
    # find the lowest score
    lowest_score = get_lowest_score(file_name)
    if lowest_score is None: # text file is empty
        write_to.write(str(score)+" "+str(name)+"\n")
    elif lines_len < 5: # there is some data but not 5 scores
        if score > lowest_score:
            line_num = get_score_line(leaderboard, score) # this returns which line the new score should go in
            insert_line(leaderboard, line_num, str(score)+" "+str(name)+"\n") # insert the new score in the leaderboard
        else:
            write_to.write(str(score)+" "+str(name)+"\n")
    else: # scoreboard is full
        if score > lowest_score:
            line_num = get_score_line(leaderboard, score) # this returns which line the new score should go in
            remove_lowest_score(leaderboard) # remove last item
            insert_line(leaderboard, line_num, str(score)+" "+str(name)+"\n") # insert the new score in the leaderboard


def game_over(window, colour, try_again_button, text_box, save_button, xy, saved):
    """Subroutine to display game over message and leaderboard"""
    x, y = xy
    pygame.draw.rect(window, colour, [(WIDTH/2)-250, (HEIGHT/2)-200, 500, 400])
    pygame.draw.line(window, (0, 0, 0), ((WIDTH/2)-250, (HEIGHT/2)-170), ((WIDTH/2)+250, (HEIGHT/2)-170))
    pygame.draw.line(window, (160, 200, 120), ((WIDTH/2)-250, (HEIGHT/2)-120), ((WIDTH/2)-50, (HEIGHT/2)-120), 3)
    pygame.draw.line(window, (140, 200, 140), ((WIDTH/2)-50, (HEIGHT/2)-120), ((WIDTH/2)-50, (HEIGHT/2)+25), 3)
    pygame.draw.line(window, (120, 200, 160), ((WIDTH/2)-250, (HEIGHT/2)+25), ((WIDTH/2)-50, (HEIGHT/2)+25), 3)
    try_again_button.display()
    text_box.display()
    if save_button.is_focused(x, y) and not saved: save_button.change_button_colour()
    save_button.display()
    mechanics.display_text("GAME OVER!",15,((WIDTH/2), (HEIGHT/2)-180), window, True)
    mechanics.display_text("TOP SCORES",15,((WIDTH/2)-250, (HEIGHT/2)-160), window, False)
    mechanics.display_text("NAME",15,((WIDTH/2)-250, (HEIGHT/2)-140), window, False)
    mechanics.display_text("SCORE",15,((WIDTH/2)-100, (HEIGHT/2)-140), window, False)
    load_leaderboard(window, leaderboard)

def help_box(xy, text, colour, width=225, height=40):
    """Subroutine to display help box, input text as a list with each list element representing one line of text"""
    x, y = xy
    pygame.draw.rect(window, colour, (x, y+20, width, height))
    i = 0
    for line in text:
        mechanics.display_text(line, 10, (x+2, y+22+i), window)
        i += 20

def check_colour(ball_colour, trajectory_colour):
    """Subroutine which returns the rgb colour given a value between 0-2"""
    if trajectory_colour == 0:
        trajectory_colour_rgb = (255, 0, 0)
    elif trajectory_colour == 1:
        trajectory_colour_rgb = (0, 255, 0)
    else:
        trajectory_colour_rgb = (0, 0, 255)

    if ball_colour == 0:
        ball_colour_rgb = (255, 0, 0)
    elif ball_colour == 1:
        ball_colour_rgb = (0, 255, 0)
    else:
        ball_colour_rgb = (0, 0, 255)

    return ball_colour_rgb, trajectory_colour_rgb

def get_gap_rect(bottom_pipe, top_pipe):
    """Soubroutine to get the invisible rectangle between two pipes"""
    return pygame.Rect(top_pipe.rect.x, (top_pipe.rect.y + top_pipe.rect.height), top_pipe.rect.width, (bottom_pipe.rect.y - top_pipe.rect.y - top_pipe.rect.height))

def check_collision(top_pipe, bottom_pipe, particle):
    """Function to depending on the type of the collision reverse either x or y velocity of the projectile"""
    collision = False
    collision_status = top_pipe.collision(particle.x+particle.width, particle.y)
    if collision_status == "bottom":
        particle.yvelocity = -particle.yvelocity
        collision = True
    elif collision_status == "side":
        particle.x = top_pipe.rect.x - particle.width
        particle.xvelocity = -particle.xvelocity
        collision = True
    collision_status = bottom_pipe.collision(particle.x+particle.width, particle.y+particle.height)
    if collision_status == "bottom":
        particle.yvelocity = -particle.yvelocity
        collision = True
    elif collision_status == "side":
        particle.x = bottom_pipe.rect.x - particle.width
        particle.xvelocity = -particle.xvelocity
        collision = True
    return collision

def start_menu():
    """Subroutine to display the start menu which takes to scientific mode or game mode"""
    scientific_mode_button = mechanics.Button(window, (WIDTH/2)-400, (HEIGHT/2)-250, 200, 150, (224, 224, 224), "Scientific Mode", 15)
    game_mode_button = mechanics.Button(window, (WIDTH/2)+200, (HEIGHT/2)-250, 200, 150, (224, 224, 224), "Game Mode", 15)
    particle = mechanics.Projectile(window=window, window_width=WIDTH, window_height=HEIGHT/2,initial_speed=-5, angle=140, realtime=False, y=(HEIGHT/2)+50, x=(WIDTH/2)-400,
    yacc=-2)
    loop = True

    while loop:
        for event in pygame.event.get(): # get all the events then loop through them all
            if event.type == pygame.QUIT:
                loop = False # exit the loop
            elif event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE: # if the user has clicked the escape key
                    loop = False # exit the loop
            elif event.type == MOUSEBUTTONDOWN and event.button == 1: # a single right click for the button
                x, y = event.pos
                if scientific_mode_button.is_focused(x, y): # if the scientific mode button is clicked
                    return True # return True for scientific mode
                elif game_mode_button.is_focused(x, y): # if the game mode button is clicked
                    return False # return False for game mode
                elif exit_button.is_focused(x, y): # if the exit button is clicked
                    loop = False

        window.fill((0, 0, 0)) # make the entire screen black
        x, y = pygame.mouse.get_pos() # get the current position of the mouse as (x, y)
        # make the button interactive by checking if the user is hovering over the button then changing its colour
        if scientific_mode_button.is_focused(x, y): scientific_mode_button.change_button_colour((255, 255, 255))
        elif game_mode_button.is_focused(x, y): game_mode_button.change_button_colour((255, 255, 255))
        elif exit_button.is_focused(x, y): exit_button.change_button_colour((255, 0, 0))

        # display the buttons
        scientific_mode_button.display()
        game_mode_button.display()
        exit_button.display()
        particle.display()
        particle.move()
        particle.draw_trajectory((255, 0, 0))
        if particle.check_below_point((HEIGHT/2)+50):
            particle.stop()
        pygame.display.update() # update the screen

def game_mode():
    particle = mechanics.Projectile(window, window_width=WIDTH, window_height=HEIGHT-150, initial_speed=0, angle=0, realtime=True, graphic_name="ball.png", colour_key=(0,0,0), x=300, y=HEIGHT-185)
    slider_width, slider_height = 15, 40
    slider_x, slider_y = 277, 10
    slider1_x, slider1_y = 535, 60
    slider2_x, slider2_y = 175, 110
    slider_colour = (0, 200, 0)

    # there will be multiple sliders so each one needs its own object
    button = mechanics.Button(window, 750, 60, 75, 40, (0, 200, 0), "GO!", 15) # go button
    slider = mechanics.slider(window, 175, 20, (224, 224, 224), 500, 20, slider_x, slider_y, slider_width, slider_height, slider_colour, 0, 30)
    slider1 = mechanics.slider(window, 175, 70, (224, 224, 224), 500, 20, slider1_x, slider1_y, slider_width, slider_height, slider_colour, 0, 90)
    slider2 = mechanics.slider(window, 175, 120, (224, 224, 224), 500, 20, slider2_x, slider2_y, slider_width, slider_height, slider_colour, 0, 8)
    initial_speed, angle, height = round(slider.scale(), 1), round(slider1.scale(), 1), round(slider2.scale(), 1)

    try_again_button = mechanics.Button(window, (WIDTH/2)-250, (HEIGHT/2)+160, 500, 40, (0, 200, 0), "Try Again", 15)
    save_button =  mechanics.Button(window, (WIDTH/2)+100, (HEIGHT/2)+100, 100, 40, (0, 200, 0), "Save Score", 10)
    text_box = mechanics.Text_box(window, (WIDTH/2)+75, (HEIGHT/2)+50, 150, 40, 12)

    # initiliase the pipes. There will be 3 pairs
    mid_screen = HEIGHT / 2
    gap = 300 # this is the number of pixels between bottom pipe and top pipe in the y axis

    random_pos = random.randint(600, 1200)
    # the gap between the pipes needs to be constant so variable gap is used
    # middle of the screen is calculated then there will be gap/2 pixels above midscreen and gap/2 pixels below midscreen (y axis)
    # for bottom pipe (mid_screen + (gap/2) as y coordinate and (HEIGHT - 150 - (mid_screen + (gap/2)) as pixels below y coordinate to HEIGHT - 150
    # for the height position of the gap to be different for each pair of pipes random adjustment is used

    # random adjustment is added to (mid_screen + gap/2) then the length of the gap must be changed accordingly
    # (mid_screen + gap/2 <= HEIGHT - 150 - random_adjustment) and (m- gap/2 >= 150 - random_adjustment). If not then an error will occur
    # because the program will try to scale the pipe image to a negative size when loading the image
    # so upper and lower limits for random adjustment can be calculated by rerranging each inequality
    lower = -(mid_screen - (gap/2) - 150)
    upper = -(mid_screen + (gap/2) - HEIGHT + 150)
    random_adjustment = random.randint(lower, upper)
    bottom_pipe = mechanics.Pipe(random_pos, (mid_screen + (gap/2) + random_adjustment), "up", (100,  HEIGHT - 150 - (mid_screen + (gap/2) + random_adjustment) ))
    # for top pipe 150 as y coordinate and (mid_screen - (gap/2) - 150)) as pixels above (mid_screen - gap/2) to 150
    # then random adjustment is applied
    top_pipe = mechanics.Pipe(random_pos, 150, "down", (100, mid_screen - (gap/2) + random_adjustment - 150))

    random_pos = random.randint(random_pos+750, random_pos+1050) # random_pos needs to be after the previous random_pos
    random_adjustment = random.randint(lower, upper) # this is the random height of the pipes
    bottom_pipe2 = mechanics.Pipe(random_pos, (mid_screen + (gap/2) + random_adjustment), "up", (100,  HEIGHT - 150 - (mid_screen + (gap/2) + random_adjustment) ))
    top_pipe2 = mechanics.Pipe(random_pos, 150, "down", (100, mid_screen - (gap/2) + random_adjustment - 150))

    random_pos = random.randint(random_pos+750, random_pos+1050)
    random_adjustment = random.randint(lower, upper)
    bottom_pipe3 = mechanics.Pipe(random_pos, (mid_screen + (gap/2) + random_adjustment), "up", (100,  HEIGHT - 150 - (mid_screen + (gap/2) + random_adjustment) ))
    top_pipe3 = mechanics.Pipe(random_pos, 150, "down", (100, mid_screen - (gap/2) + random_adjustment - 150))
    last_rect_x = random_pos # keeps track of the x position of the last pipe

    pipe_group = pygame.sprite.Group(bottom_pipe, top_pipe, bottom_pipe2, top_pipe2, bottom_pipe3, top_pipe3)

    gap_rect = get_gap_rect(bottom_pipe, top_pipe)
    gap_rect2 = get_gap_rect(bottom_pipe2, top_pipe2)
    gap_rect3 = get_gap_rect(bottom_pipe3, top_pipe3)
    start_particle = False
    loop = True
    collision = False
    saved = False
    x_offset = 0
    trajectory_x_offset = x_offset
    mid = 300
    distance = 0 # cumulative value for distance travelled
    pipes_cleared = 0
    height = 0
    rect_counter = 1

    while loop:
        if top_pipe.rect.x + top_pipe.rect.width < 0: # reset the position of the pipes when they go off the screen
            if last_rect_x < WIDTH: # make sure the pipe has to spawn outside the users view (off the screen)
                spawn = WIDTH
            else:
                spawn = int(last_rect_x)
            # give the pipe a random x pos between x of the last pipe + 400 and x of the last pipe + 1600
            random_pos = random.randint(spawn+700, spawn+1050)
            last_rect_x = random_pos # now make this the last rect x position
            top_pipe.reset(random_pos)
            bottom_pipe.reset(random_pos)
            gap_rect = get_gap_rect(bottom_pipe, top_pipe)

        elif top_pipe2.rect.x + top_pipe2.rect.width < 0: # reset the position of the pipes when they go off the screen
            if last_rect_x < WIDTH:
                spawn = WIDTH
            else:
                spawn = int(last_rect_x)
            random_pos = random.randint(spawn+700, spawn+1050)
            last_rect_x = random_pos
            top_pipe2.reset(random_pos)
            bottom_pipe2.reset(random_pos)
            gap_rect2 = get_gap_rect(bottom_pipe2, top_pipe2)

        elif top_pipe3.rect.x + top_pipe3.rect.width < 0: # reset the position of the pipes when they go off the screen
            if last_rect_x < WIDTH:
                spawn = WIDTH
            else:
                spawn = int(last_rect_x)
            random_pos = random.randint(spawn+700, spawn+1050)
            last_rect_x = random_pos
            top_pipe3.reset(random_pos)
            bottom_pipe3.reset(random_pos)
            gap_rect3 = get_gap_rect(bottom_pipe3, top_pipe3)
        #---------dealing with collision---------#
        # has the ball collided with the any of the pipes?
        if not collision:
            collision = check_collision(top_pipe, bottom_pipe, particle)
            if not collision:
                collision = check_collision(top_pipe2, bottom_pipe2, particle)
                if not collision:
                    collision = check_collision(top_pipe3, bottom_pipe3, particle)
        # check to see if the ball went between the pipes
        # find which current rect is the latest rect
        latest_rect = [gap_rect, gap_rect2, gap_rect3][rect_counter -1]
        if latest_rect.collidepoint(particle.x + particle.width, particle.y) and not collision: # pipe has been cleared
            if sound:
                ding_sound.play()
            pipes_cleared += 1
            rect_counter = (rect_counter + 1) % 3 # there are only 3 rect gaps so mod 3
        if particle.y < 150: # collided with the top
            particle.y = 150
            particle.yvelocity = (-particle.yvelocity)/2
            collision = True
        #---------------------------------------#

        # work out how far the ball has moved forward for the x_offset
        if particle.x > mid:
            x_offset = particle.x - mid
            # move all the other sprites backwards
            top_pipe.rect.x -= x_offset
            bottom_pipe.rect.x -= x_offset
            top_pipe2.rect.x -= x_offset
            bottom_pipe2.rect.x -= x_offset
            top_pipe3.rect.x -= x_offset
            bottom_pipe3.rect.x -= x_offset
            trajectory_x_offset = x_offset
            # now change the position of the pipes according to the x_offset and keep the ball central
            particle.x -= x_offset
            gap_rect.x -= x_offset
            gap_rect2.x -= x_offset
            gap_rect3.x -= x_offset
            last_rect_x -= x_offset
        else:
            x_offset = 0

        for event in pygame.event.get(): # get any events such as keyboard presses and mouse clicks
            if event.type == pygame.QUIT:
                loop = False
            elif event.type == pygame.KEYDOWN: # key press
                if event.key == K_ESCAPE:
                    loop = False
                elif event.key == K_BACKSPACE:
                    text_box.backspace()
                elif event.key < 256: # ensure the event.key can be represented using ascii
                    text_box.add_char(chr(event.key))
            elif pygame.mouse.get_pressed()[0]: # supports holding down the mouse for the slider
                x,y  = pygame.mouse.get_pos()
                # slider_event method will move the slider if the given (x,y) position of the mouse click is in range for the slider.
                #  It will also return a boolean to indicate if it has moved the sliders position.
                if slider.slider_event(x, y, WIDTH): initial_speed = round(slider.scale(), 1)
                elif slider1.slider_event(x, y, WIDTH): angle = round(slider1.scale(), 1)
                elif slider2.slider_event(x, y, WIDTH): height = round(slider2.scale(), 1)

            if event.type == MOUSEBUTTONDOWN and event.button == 1: # a single right click for the button
                x, y = event.pos
                if exit_button.is_focused(x, y):
                    loop = False
                elif back_button.is_focused(x, y):
                    loop = False
                    return True
                elif button.is_focused(x, y) and not collision and not particle.is_moving():
                    if sound:
                        click_sound.play()
                    button.press()
                    particle.change_values(initial_speed, angle, metre_to_pixels(height, 0))
                    particle.restart()
                    start_particle = True
                    distance += round(particle.calculation(height, range_=True))
                elif try_again_button.is_focused(x, y) and collision and not particle.is_moving():
                    # restart the game by resetting variables
                    try_again_button.press()
                    start_particle = False
                    collision = False
                    saved = False
                    random_adjustment = random.randint(lower, upper)
                    random_pos = random.randint(600, 1200)
                    bottom_pipe.__init__(random_pos, (mid_screen + (gap/2) + random_adjustment), "up", (100,  HEIGHT - 150 - (mid_screen + (gap/2) + random_adjustment) ))
                    top_pipe.__init__(random_pos, 150, "down", (100, mid_screen - (gap/2) + random_adjustment - 150))

                    random_pos = random.randint(random_pos+700, random_pos+1050)
                    random_adjustment = random.randint(lower, upper)
                    bottom_pipe2.__init__(random_pos, (mid_screen + (gap/2) + random_adjustment), "up", (100,  HEIGHT - 150 - (mid_screen + (gap/2) + random_adjustment) ))
                    top_pipe2.__init__(random_pos, 150, "down", (100, mid_screen - (gap/2) + random_adjustment - 150))

                    random_pos = random.randint(random_pos+750, random_pos+1050)
                    random_adjustment = random.randint(lower, upper)
                    bottom_pipe3.__init__(random_pos, (mid_screen + (gap/2) + random_adjustment), "up", (100,  HEIGHT - 150 - (mid_screen + (gap/2) + random_adjustment) ))
                    top_pipe3.__init__(random_pos, 150, "down", (100, mid_screen - (gap/2) + random_adjustment - 150))
                    last_rect_x = random_pos # keeps track of the x position of the last pipe

                    distance = 0
                    pipes_cleared = 0
                    rect_counter = 1
                    gap_rect = get_gap_rect(bottom_pipe, top_pipe)
                    gap_rect2 = get_gap_rect(bottom_pipe2, top_pipe2)
                    gap_rect3 = get_gap_rect(bottom_pipe3, top_pipe3)
                    text_box.clear()
                elif save_button.is_focused(x, y) and collision and not saved:
                    add_to_leaderboard(leaderboard, text_box.text, pipes_cleared)
                    saved = True
            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if button.status: button.unpress()
                elif try_again_button.status: try_again_button.unpress()

        window.fill((0, 0, 0))
        window.blit(bg, [0, 150]) # blit the background onto the window

        # draw top rectangle
        pygame.draw.rect(window, (128,128,128), [0, 0, WIDTH, 150])
        x, y = pygame.mouse.get_pos()
        if slider.detect_mouse_over_slider(x, y): slider.change_slider_colour()
        elif slider1.detect_mouse_over_slider(x, y): slider1.change_slider_colour()
        elif slider2.detect_mouse_over_slider(x, y): slider2.change_slider_colour()
        elif button.is_focused(x, y) and not collision: button.change_button_colour()
        elif try_again_button.is_focused(x, y) and collision: try_again_button.change_button_colour()
        elif exit_button.is_focused(x, y): exit_button.change_button_colour((255, 0, 0))
        elif back_button.is_focused(x, y): back_button.change_button_colour((0, 200, 0))

        slider.display((str(initial_speed)+" M/S : Speed"), 15, 20, 15)
        slider1.display((str(angle)+" Deg : Angle"), 15, 70, 15)
        slider2.display((str(height)+" M : Height"), 15, 120, 15)
        button.display()
        exit_button.display()

        # draw bottom rectangle
        pygame.draw.rect(window, (128,128,128), [0, HEIGHT-150, WIDTH, 150])
        back_button.display()
        mechanics.display_text("Distance travelled : "+str(distance)+" M", 15, (20, text_y), window)
        mechanics.display_text("Pipes cleared : "+str(pipes_cleared), 15, (320, text_y), window)

        if not particle.is_moving():
            particle.draw_start_path(initial_speed, angle, ( (height * FPS) ) ) # draw the black start path to help the user

        # move the projectile
        if start_particle:
            particle.display()
            particle.move()
            particle.draw_offset_trajectory((255, 0, 0), trajectory_x_offset)
            if particle.check_floor_collision():
                particle.stop()
        pipe_group.draw(window)
        if collision:
            game_over(window, (224, 224, 244), try_again_button, text_box, save_button, (x, y), saved)
        pygame.display.update()
        clock.tick(FPS)

def scientific_mode():
    particle = mechanics.Projectile(window, window_width=WIDTH, window_height=HEIGHT-150,initial_speed=0, angle=0, realtime=True)

    slider_width, slider_height = 15, 40
    slider_x, slider_y = 277, 10
    slider1_x, slider1_y = 535, 60
    slider2_x, slider2_y = 175, 110
    slider_colour = (0, 200, 0)

    # there will be multiple sliders so each one needs its own object
    slider = mechanics.slider(window, 175, 20, (224, 224, 224), 500, 20, slider_x, slider_y, slider_width, slider_height, slider_colour, 0, 60)
    slider1 = mechanics.slider(window, 175, 70, (224, 224, 224), 500, 20, slider1_x, slider1_y, slider_width, slider_height, slider_colour, -90, 90)
    slider2 = mechanics.slider(window, 175, 120, (224, 224, 224), 500, 20, slider2_x, slider2_y, slider_width, slider_height, slider_colour, 0, 120)
    zoomer = mechanics.slider(window, 10, 180,   (224, 224, 224), 20, 150,  0,        180,       40,           15,            slider_colour, 0, 10, "v")
    initial_speed, angle, height, zoom = round(slider.scale(), 1), round(slider1.scale(), 1), round(slider2.scale(), 1), round(zoomer.scale())
    initial_zoom = zoom

    # there will be multiple buttons so each one needs its own object
    button = mechanics.Button(window, 750, 60, 75, 40, (0, 200, 0), "GO!", 15) # go button
    pause_button = mechanics.Button(window, WIDTH-480, 150, 25, 25, (50, 50, 50), None, None, False) # no text, shapes are going to be used instead
    settings_button = mechanics.Button(window, WIDTH-90, 0, 50, 20, (224, 224, 224), "Settings", 10) # setting button
    hold_trajectory_button = mechanics.Button(window, WIDTH-590, 150, 100, 25, (50, 50, 50), "Hold Trajectory", 10, False)
    save_button =  mechanics.Button(window, WIDTH-140, 0, 50, 20, (224, 224, 224), "Save", 10) # save button
    save_button2 = mechanics.Button(window, (WIDTH/2)-37, (HEIGHT/2)-20, 75, 40, (0, 200, 0), "SAVE", 15) # save button within the save menu rect
    load_button = mechanics.Button(window, WIDTH-190, 0, 50, 20, (224, 224, 224), "Load", 10) # load button
    load_button2 = mechanics.Button(window, (WIDTH/2)-37, (HEIGHT/2)-20, 75, 40, (0, 200, 0), "LOAD", 15) # load button within the load menu rect
    text_box = mechanics.Text_box(window, (WIDTH/2)-50, (HEIGHT/2)-115, 150, 40, 12)

    # buttons which are only displayed with the drop down menu---------------------------------
    live_data_button = mechanics.Button(window, WIDTH-105, 60, 80, 30, (0,255, 0), "Show live data", 10)
    ball_colour_button = mechanics.Button(window, WIDTH-105, 100, 80, 30, (255, 0, 0), "Ball colour", 10)
    trajectory_button = mechanics.Button(window, WIDTH-105, 140, 80, 30, (0, 255, 0), "Trace Path", 10)
    trajectory_colour_button = mechanics.Button(window, WIDTH-105, 180, 80, 30, (255, 0, 0), "Path colour", 10)
    information_button = mechanics.Button(window, WIDTH-105, 220, 80, 30, (0, 255, 0), "Information box", 10)
    earth_button = mechanics.Button(window, WIDTH-130, 260, 50, 50, (255, 255, 0), None, None, False) # no text earth image will be used instead
    mars_button = mechanics.Button(window, WIDTH-65, 260, 50, 50, (224, 224, 224), None, None, False)
    #---------------------------------------------------------------------------------------------

    calculated = False
    start_particle = False
    loop = True
    pause = False
    floor_contact = False

    display_menu = False
    display_save_menu = False
    display_load_menu = False
    display_saved = False
    live_data = True
    trajectory = True
    information_boxes = True

    g_earth = True
    g_mars = False

    ball_colour = 0 # 0=red, 1=green, 2=blue
    ball_colour_rgb = (255, 0, 0) # defualt colour is red

    trajectory_colour = 0 # 0=red, 1=green, 2=blue
    trajectory_colour_rgb = (255, 0, 0) # defualt colour is red
    static_projectiles = []

    while loop: # the main loop of the program where all the drawing occurs
        for event in pygame.event.get(): # get any events such as keyboard presses and mouse clicks
            if event.type == pygame.QUIT:
                loop = False
            elif event.type == pygame.KEYDOWN: # key press
                if event.key == K_ESCAPE:
                    loop = False
                elif event.key == K_SPACE:
                    if not display_save_menu: # stop space cuasing projectile restarting when the user is entering a name into the text box
                        if floor_contact:
                            particle.restart()
                            floor_contact = False
                        else:
                            if not pause:
                                pause = True
                                particle.pause()
                            else:
                                pause = False
                                particle.start_from_pause()
                if display_save_menu or display_load_menu: # the save menu is open so allow the user to enter a name for their projectile
                    if event.key == K_BACKSPACE:
                        text_box.backspace()
                    else:
                        if event.key < 256: # ensure the event.key can be represented using ascii
                            text_box.add_char(chr(event.key))
            elif pygame.mouse.get_pressed()[0]: # supports holding down the mouse for the slider
                pos = pygame.mouse.get_pos()
                # slider_event method will move the slider if the given (x,y) position of the mouse click is in range for the slider.
                #  It will also return a boolean to indicate if it has moved the sliders position.
                if slider.slider_event(pos[0], pos[1], WIDTH): initial_speed = round(slider.scale(), 1)
                elif slider1.slider_event(pos[0], pos[1], WIDTH): angle = round(slider1.scale(), 1)
                elif slider2.slider_event(pos[0], pos[1], WIDTH): height = round(slider2.scale(), 1)
                elif zoomer.slider_event(pos[0], pos[1], WIDTH):
                    zoom = round(zoomer.scale())



            if event.type == MOUSEBUTTONDOWN and event.button == 1: # a single right click for the button
                x, y = event.pos[0], event.pos[1]

                if ball_colour_rgb == (255, 255, 0) and trajectory_colour_rgb == (255, 255, 0): # the ball must be highlighted (so it must be clicked by the user)
                    if hold_trajectory_button.is_focused(x, y):
                        hold_trajectory_button.press()
                        ball_colour_rgb, trajectory_colour_rgb = check_colour(ball_colour, trajectory_colour) # reset colour from highlighted to normal
                        # the current projectile needs to be kept on the screen as requested by the user, so a new object will be made for the current projectile
                        # the new object can only be drawn to the screen and cant move and is added to the list of static projectile. Every item in static_projectiles list will be displayed
                        static_projectiles.append(mechanics.StaticProjectile(window, trajectory_colour_rgb, particle.position, particle.x, particle.y, particle.width, particle.height, ball_colour_rgb))


                # reset the colour of the ball after a click so it is unhighlighted
                ball_colour_rgb, trajectory_colour_rgb = check_colour(ball_colour, trajectory_colour)
                particle.colour = ball_colour_rgb

                if not menu_rect.collidepoint(x, y): # if somewhere other then the menu rect is clicked then stop displaying the menu (to close it)
                    display_menu = False

                if not save_menu_rect.collidepoint(x, y):
                    display_save_menu = False
                    display_load_menu = False # save menu and load menu share the same rect
                    text_box.clear()

                if not saved_rect.collidepoint(x, y):
                    display_saved = False

                if button.is_focused(x, y): # if the "GO" is clicked
                    if sound:
                        click_sound.play()
                    button.press()
                    particle.change_values(initial_speed, angle, metre_to_pixels(height, zoom))
                    particle.restart()
                    start_particle = True
                    calculated = False
                    pause = False
                    floor_contact = False
                    initial_zoom = zoom

                elif pause_button.is_focused(x, y):
                    pause_button.press()
                    if not pause:
                        pause = True
                        particle.pause()
                    else:
                        pause = False
                        particle.start_from_pause()

                elif settings_button.is_focused(x, y):
                    display_menu = True

                elif live_data_button.is_focused(x, y) and display_menu:
                    live_data = not live_data
                    if live_data:
                        live_data_button.button_colour = (0, 255, 0)
                    else:
                        live_data_button.button_colour = (255, 0, 0)

                elif ball_colour_button.is_focused(x, y) and display_menu:
                    ball_colour = (ball_colour + 1) % 3
                    ball_colour_rgb, trajectory_colour_rgb = check_colour(ball_colour, trajectory_colour)
                    ball_colour_button.button_colour = ball_colour_rgb
                    particle.colour = ball_colour_rgb

                elif trajectory_button.is_focused(x, y) and display_menu:
                    trajectory = not trajectory
                    if trajectory:
                        trajectory_button.button_colour = (0, 255, 0)
                    else:
                        trajectory_button.button_colour = (255, 0, 0)

                elif trajectory_colour_button.is_focused(x, y) and display_menu:
                    trajectory_colour = (trajectory_colour + 1) % 3
                    ball_colour_rgb, trajectory_colour_rgb = check_colour(ball_colour, trajectory_colour)
                    trajectory_colour_button.button_colour = trajectory_colour_rgb

                elif information_button.is_focused(x, y) and display_menu:
                    information_boxes = not information_boxes
                    if information_boxes:
                        information_button.button_colour = (0, 255, 0)
                    else:
                        information_button.button_colour = (255, 0, 0)

                elif earth_button.is_focused(x, y) and display_menu:
                    g_mars = False
                    g_earth = True
                    calculated = False
                    earth_button.button_colour = (255, 255, 0)
                    mars_button.button_colour = (224, 224, 224)
                    particle.yacc = 9.8 # acceleration due to gravity on earth is 9.8 ms^-2
                    particle.initial_yacc = 9.8

                elif mars_button.is_focused(x, y) and display_menu:
                    g_mars = True
                    g_earth = False
                    calculated = False
                    earth_button.button_colour = (224, 224, 224)
                    mars_button.button_colour = (255, 255, 0)
                    particle.yacc = 3.711 # acceleration due to gravity on mars is 3.711 ms^-2
                    particle.initial_yacc = 3.711

                elif exit_button.is_focused(x, y):
                    loop = False

                elif back_button.is_focused(x, y):
                    loop = False
                    return True

                elif save_button.is_focused(x, y):
                    display_save_menu = True

                elif save_button2.is_focused(x, y) and display_save_menu:
                    # the save button has been clicked so the initial speed, angle and height need to be saved in a text file
                    if text_box.text != "": # empty strings cant be loaded later on so its pointless to save them
                        save_projectile(save_file, text_box.text, initial_speed, angle, height)
                        display_save_menu = False # close the save menu as the projectile has been saved
                        display_saved = True # now display a message telling the user the game has been saved
                        text_box.clear()

                elif load_button.is_focused(x, y):
                    display_load_menu = True

                elif load_button2.is_focused(x, y) and display_load_menu:
                    # load the chosen projectile into the program
                    if text_box.text != "": # empty strings can cuase the program to crash when loading
                        values = load_projectile(save_file, text_box.text)
                        if values is not None:
                            initial_speed, angle, height = values
                        text_box.clear()
                        display_load_menu = False

                elif particle.is_focused(x, y) and particle.xvelocity == 0:
                    # highlight the ball yellow when it is clicked
                    trajectory_colour_rgb = (255, 255, 0)
                    ball_colour_rgb = (255, 255, 0)
                    particle.colour = ball_colour_rgb

                else:
                    for p in static_projectiles: # check if static projectiles have been clicked
                        if p.is_focused(x, y):
                            static_projectiles.remove(p) # remove this static projectile if it is clicked

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if button.status: button.unpress()
                elif pause_button.status: pause_button.unpress()
                elif hold_trajectory_button.status: hold_trajectory_button.unpress()

            # support mouse scrolling for the zoom slider
            elif event.type == MOUSEBUTTONDOWN and event.button == 4:
                zoomer.mouse_scroll("up")
                zoom = round(zoomer.scale())
            elif event.type == MOUSEBUTTONDOWN and event.button == 5:
                zoomer.mouse_scroll("down")
                zoom = round(zoomer.scale())

        window.fill((0, 0, 0))

        if pause:
            # make sure that when paused velocities to display wont be 0.0
            xv, yv = particle.pause_xvelocity, -particle.pause_yvelocity
        else:
            xv, yv = particle.xvelocity, -particle.yvelocity

        if live_data:

            mechanics.display_text("x velocity : "+str(xv), 10, (WIDTH-430, 150), window, colour=(224, 224, 224))
            mechanics.display_text("y velocity : "+str(yv, ), 10, (WIDTH-430, 165), window, colour=(224, 224, 224))
            mechanics.display_text("Speed : "+str(particle.get_speed(pause)), 10, (WIDTH-430, 180), window, colour=(224, 224, 224))

            xd, yd = particle.get_distance()  # get the x and y displacement in pixels first
            # now convert them to metres
            xd = round(xd / (FPS / (initial_zoom+1)), 1)
            yd = round(yd / (FPS / (initial_zoom+1)), 1)
            mechanics.display_text("x displacement : "+str(xd), 10, (WIDTH-260, 150), window, colour=(224, 224, 224))
            mechanics.display_text("y displacement : "+str(-yd), 10, (WIDTH-260, 165), window, colour=(224, 224, 224))

        # draw top rectangle for input data
        pygame.draw.rect(window, (128,128,128), [0, 0, WIDTH, 150])
        pos = pygame.mouse.get_pos()
        x, y = pos[0], pos[1]
        # make the sliders and buttons interactive by allowing help boxes to be displayed and button/slider to change colour
        if slider.detect_mouse_over_slider(x, y): slider.change_slider_colour()
        elif slider1.detect_mouse_over_slider(x, y): slider1.change_slider_colour()
        elif slider2.detect_mouse_over_slider(x, y):
            slider2.change_slider_colour()
            if information_boxes: help_box((x, y), ["Set the initial height of the projectile"], (224, 224, 224), width=190)
        elif zoomer.detect_mouse_over_slider(x, y):
            zoomer.change_slider_colour()
            if information_boxes: help_box((x, y), ["Scale down the projectiles flight path", "so it doesnt go off screen", "(Projectile flight will still be real time)"], (224, 224, 224), height=60)
        elif button.is_focused(x, y): button.change_button_colour()
        elif settings_button.is_focused(x, y): settings_button.change_button_colour((255, 255, 255))
        elif exit_button.is_focused(x, y): exit_button.change_button_colour((255, 0, 0))
        elif back_button.is_focused(x, y): back_button.change_button_colour((0, 200, 0))
        elif save_button.is_focused(x, y):
            save_button.change_button_colour((255, 255, 255))
            if information_boxes: help_box((x-100, y), ["Click me to save initial values", "Speed, Angle and Height"], (224, 224, 224))
        elif load_button.is_focused(x, y):
            load_button.change_button_colour((255, 255, 255))
            if information_boxes: help_box((x-100, y), ["Click me to load initial values Speed", "Angle and Height from a previous save"], (224, 224, 224))
        elif hold_trajectory_button.is_focused(x, y) and information_boxes: help_box((x, y), ["Highlight the projectile by clicking it", "Then click me and I will keep it on screen",
        "To delete held projectile just click it"], (224, 224, 224), height=70)
        elif pause_button.is_focused(x, y):
            if information_boxes:
                if pause:
                    help_box((x, y), ["Click me to start the current projectile", "from a pause"], (224, 224, 224))
                else:
                    help_box((x, y), ["Click me to pause the current projectile"], (224, 224, 224))
        elif particle.is_focused(x, y) and not particle.is_moving() and  information_boxes: help_box((x, y-50), ["Click me to highlight me"], (224, 224, 224), width=130, height=20)
        # display buttons and sliders
        slider.display((str(initial_speed)+" M/S : Speed"), 15, 20, 15)
        slider1.display((str(angle)+" Deg : Angle"), 15, 70, 15)
        slider2.display((str(height)+" M : Height"), 15, 120, 15)
        button.display()
        settings_button.display()
        exit_button.display()
        hold_trajectory_button.display((224, 224, 244))
        save_button.display()
        load_button.display()


        # conditionally display menus
        if display_menu:
            settings_menu(window, (224, 224, 224), live_data_button, ball_colour_button, trajectory_button, trajectory_colour_button, information_button, earth_button, mars_button)
        elif display_save_menu:
            save_menu(window, (224, 224, 224), (pos[0],pos[1]), initial_speed, angle, height, save_button2, text_box)
        elif display_saved:
            saved(window, (224, 224, 224))
        elif display_load_menu:
            load_menu(window, (224, 224, 224), (pos[0],pos[1]), load_button2, text_box)

        # draw bottom rectangle for ouput data
        pygame.draw.rect(window, (128,128,128), [0, HEIGHT-150, WIDTH, 150])
        back_button.display()
        if not calculated:
            max_altitude, time_of_flight = round(particle.calculation(height, distance_max_height=True), 3), round(particle.calculation(height,time_of_flight=True), 3)
            range_, time_max_height = round(particle.calculation(height, range_=True), 3), round(particle.calculation(height, time_max_height=True), 3)
            calculated = True # stop the program from being wasteful with processing power by only calculating once per projectile
        mechanics.display_text("Maximum altitude : "+str(max_altitude)+" M", 15, (20, text_y), window) # (text, text_size, position, window)
        mechanics.display_text("Range : "+str(range_)+" M", 15, (320, text_y), window)
        mechanics.display_text("Time of flight : "+str(time_of_flight)+" S", 15, (500, text_y), window)
        mechanics.display_text("Time at maximum altitude : "+str(time_max_height)+" S", 15, (750, text_y), window)

        # draw buttons, slider and text in the middle black rectangle
        zoomer.display("Scale : "+str(zoom), 5, 160, 15, (200, 210, 15))
        pause_button.display()
        display_height(HEIGHT-150, metre_to_pixels(height, zoom)+15, ball_colour_rgb, height)
        if pause:
            pygame.draw.polygon(window, (0, 200, 0), ((WIDTH-475, 157), (WIDTH-475, 167), (WIDTH-460, 162))) # draw a triangle indicating the projectile is paused
        else:
            # draw two rectangles indicating the projectile is not paused
            pygame.draw.rect(window, (0, 200, 0), [WIDTH-475, 155, 5, 15])
            pygame.draw.rect(window, (0, 200, 0), [WIDTH-465, 155, 5, 15])

        # display each static projectile
        for p in static_projectiles:
            p.draw_trajectory()
            p.display()

        # move the projectile
        if start_particle:
            particle.display()
            particle.move(initial_zoom+1)
            if trajectory:
                particle.draw_trajectory(trajectory_colour_rgb)
            particle.draw_angle()
            particle.write_text(text_colour=(0, 255, 0))
            if particle.check_floor_collision():
                particle.stop()
                floor_contact = True
        pygame.display.update()
        clock.tick(60)

def main():
    loop = True
    while loop is not None:
        # modes will return None when the user clicks the exit program button
        # modes will return True for scientific mode
        # modes will return False for game mode
        mode = start_menu()
        loop = mode

        if mode is True:
            loop = scientific_mode()
        elif mode is False:
            loop = game_mode()

    pygame.quit()

if __name__ == '__main__':
    main()
