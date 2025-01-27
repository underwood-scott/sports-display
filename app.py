from get_data import get_current_games
from flask import Flask, render_template
from multiprocessing import Process
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time

app = Flask(__name__)


def run_display(font_file):
    # station code and direction will be sent on init
    nfl_games = get_current_games('nfl', ['Green Bay Packers', 'Washington Commanders'], -5)
    canvas = init_matrix()

    # prev_lines = []
    # prev_cars = []
    # prev_dests = []
    # prev_times = []

    draw_display(canvas, font_file, nfl_games[0])

    # while True:
    #     force_update = False
    #     if station_code_receiver.poll():
    #         station_code = station_code_receiver.recv()
    #     if direction_receiver.poll():
    #         direction = direction_receiver.recv()
    #     if incidents_check_count == 12: # check for incidents every minute
    #         force_update = True
    #         station = get_station_by_code(station_code)
    #         if station == None:
    #             logging.error("Could not find station for code: {}", station_code)
    #         line_codes = get_line_codes_from_station(station)
    #         incidents = get_incidents(line_codes, api_key)
    #         for incident in incidents:
    #             logging.info("Calling draw_incident for: {}".format(incident))
    #             draw_incident(canvas, font_file, incident)
    #         incidents_check_count = 0

    #     prev_lines, prev_cars, prev_dests, prev_times = show_train_times(api_key, font_file, canvas, station_code, direction, prev_lines, prev_cars, prev_dests, prev_times, force_update)
        
    #     time.sleep(5)
    #     incidents_check_count += 1


def init_matrix():
    options = RGBMatrixOptions()
    options.rows = 32
    options.chain_length = 4
    options.pwm_bits = 3
    options.pwm_lsb_nanoseconds = 300
    options.gpio_slowdown = 2
    return RGBMatrix(options = options)


def draw_display(canvas, font_file, game):
    height_delta = 8
    width_delta = 6

    total_width = 128

    font = graphics.Font()
    font.LoadFont(font_file)
    red_color = graphics.Color(255,0,0)

    canvas.Clear()
    graphics.DrawText(canvas, font, 0, 7, red_color, game['home_team'] + " @ " + game['away_team'])


def start_display():
    run_display('/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf')
    while True:
        run_display('/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf')
        time.sleep(5)

def serve():
    app.run(host="0.0.0.0")

if __name__ == "__main__":
    server = Process(target = serve)
    server.start()
    display_runner = Process(target = start_display)
    display_runner.start()
