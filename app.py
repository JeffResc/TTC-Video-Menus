from random import randint
import pygame
import pytz
import json
from datetime import datetime, time
import calendar
import time as time_
import math
import psutil
import subprocess

def is_time_between(begin_time, end_time, check_time=None):
    # If check time is not given, default to current UTC time
    check_time = check_time or datetime.utcnow().time()
    if begin_time < end_time:
        return check_time >= begin_time and check_time <= end_time
    else: # crosses midnight
        return check_time >= begin_time or check_time <= end_time

def move(x, y, screen, bouncing_logo):
    screen.blit(bouncing_logo, (x, y))

def fill(surface, color):
    """Fill all pixels of the surface with color, preserve transparency."""
    w, h = surface.get_size()
    r, g, b, _ = color
    for x in range(w):
        for y in range(h):
            a = surface.get_at((x, y))[3]
            surface.set_at((x, y), pygame.Color(r, g, b, a))

def randColor():
    """Generate a random color."""
    return (randint(0, 255), randint(0, 255), randint(0, 255))

def initialize_gui(active, config):
    """Initialize the GUI."""
    print('Initializing GUI... (Active: ' + str(active) + ')')
    exit = False
    checktime = time_.time()

    if active == False:
        # Screensaver
        bouncing_logo = pygame.image.load('content/' + config['screensaver']['bouncing_logo'])
        bouncing_logo = pygame.transform.scale(bouncing_logo, (config['screensaver']['bouncing_logo_size'], config['screensaver']['bouncing_logo_size']))
        static_logo_1 = pygame.image.load('content/' + config['screensaver']['static_logo'])
        static_logo_1 = pygame.transform.scale(static_logo_1, (config['screensaver']['static_logo_size_x'], config['screensaver']['static_logo_size_y']))

        clock = pygame.time.Clock()
        img_size = bouncing_logo.get_rect().size
        screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        pygame.mouse.set_visible(False)

        infoObject = pygame.display.Info()
        print(infoObject)
        x = randint(math.floor(infoObject.current_w * 0.50), infoObject.current_w - math.floor(infoObject.current_w * 0.50))
        y = randint(math.floor(infoObject.current_h * 0.50), infoObject.current_h - math.floor(infoObject.current_h * 0.50))
        x_speed = config['screensaver']['x_speed']
        y_speed = config['screensaver']['y_speed']
        if config['screensaver']['change_color']:
            fill(bouncing_logo, pygame.Color(randColor()))

        while exit == False:
            screen.fill((0, 0, 0))
            screen.blit(static_logo_1, (math.floor(infoObject.current_w / 2) - (math.floor(config['screensaver']['static_logo_size_x'] / 2)), math.floor(infoObject.current_h / 2) - (config['screensaver']['static_logo_size_y'] / 2)))
            if (x + img_size[0] >= infoObject.current_w * config['screensaver']['num_displays']) or (x <= 0):
                x_speed = -x_speed
                x += x_speed
                if config['screensaver']['change_color']:
                    fill(bouncing_logo, pygame.Color(randColor()))
            if (y + img_size[1] >= infoObject.current_h) or (y <= 0):
                y_speed = -y_speed
                y += y_speed
                if config['screensaver']['change_color']:
                    fill(bouncing_logo, pygame.Color(randColor()))
            x += x_speed
            y += y_speed
            move(x, y, screen, bouncing_logo)
            pygame.display.update()
            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit = True
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    exit = True
            # Check if mode should change
            if time_.time() - checktime > config['check_interval']:
                checktime = time_.time()
                IST = pytz.timezone(config['timezone'])
                weekday = calendar.day_name[datetime.now(IST).today().weekday()].lower()
                todays_hours = config['hours'][weekday]
                still_active = is_time_between(time(int(todays_hours['start'].split(':')[0]),int(todays_hours['start'].split(':')[1])), time(int(todays_hours['end'].split(':')[0]),int(todays_hours['end'].split(':')[1])), datetime.now(IST).time())
                if still_active == True:
                    # switch to active mode
                    print('Switching to active')
                    pygame.quit()
                    initialize_gui(still_active, config)
                    break
    else:
        # player = vlc.Instance('--input-repeat=9999999999', '--no-video-title-show', '--mouse-hide-timeout=0', '--video-on-top', '--no-audio', '--no-video-title-show', '--no-metadata-network-access', '--no-osd')

        # media = player.media_new("content/0001-4069.mp4")

        # media_player = player.media_player_new()
        # media_player.set_media(media)

        # media_player.toggle_fullscreen()
        # media_player.play()

        subprocess.Popen(["cvlc", "--no-audio", "--no-video-title-show", "--no-metadata-network-access", "--no-osd", "--fullscreen", "-Iqt", "--repeat", 'content/' + config['active']['video']])

        while True:
            # Check if mode should change
            if time_.time() - checktime > config['check_interval']:
                checktime = time_.time()
                IST = pytz.timezone(config['timezone'])
                weekday = calendar.day_name[datetime.now(IST).today().weekday()].lower()
                todays_hours = config['hours'][weekday]
                still_active = is_time_between(time(int(todays_hours['start'].split(':')[0]),int(todays_hours['start'].split(':')[1])), time(int(todays_hours['end'].split(':')[0]),int(todays_hours['end'].split(':')[1])), datetime.now(IST).time())
                if still_active == False:
                    # switch to active mode
                    #media_player.stop()
                    for proc in psutil.process_iter():
                        if proc.name() == "vlc" or proc.name() == "vlc.exe":
                            proc.kill()
                    print('Switching to screensaver')
                    initialize_gui(still_active, config)
                    break

# Start, read JSON config, check mode, and initialize GUI
f = open('content/config.json')
config = json.load(f)
f.close()
if config['screensaver']['enabled']:
    IST = pytz.timezone(config['timezone'])
    weekday = calendar.day_name[datetime.now(IST).today().weekday()].lower()
    todays_hours = config['hours'][weekday]
    active = is_time_between(time(int(todays_hours['start'].split(':')[0]),int(todays_hours['start'].split(':')[1])), time(int(todays_hours['end'].split(':')[0]),int(todays_hours['end'].split(':')[1])), datetime.now(IST).time())
    initialize_gui(active, config)
else:
    initialize_gui(True, config)

pygame.quit()
