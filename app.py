from flask import Flask, render_template
from get_data import get_current_games
from io import BytesIO
from multiprocessing import Process
from PIL import Image
import requests
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time


UTC_OFFSET = -5
NFL_TEAMS = ['Green Bay Packers', 'Washington Commanders']
NBA_TEAMS = ['Milwaukee Bucks', 'Washington Wizards']
NCAAFB_TEAMS = ['Wisconsin Badgers']
NCAABB_TEAMS = ['Wisconsin Badgers', 'Marquette Golden Eagles']
MLB_TEAMS = ['Milwaukee Brewers', 'Chicago Cubs']

app = Flask(__name__)

class SportsDisplay:
    def __init__(self, nfl_teams, ncaaff_teams, nba_teams, ncabb_teams, mlb_teams):
        self.nfl_teams = nfl_teams
        self.ncaaff_teams = ncaaff_teams
        self.nba_teams = nba_teams
        self.ncaabb_teams = ncaabb_teams
        self.mlb_teams = mlb_teams


def run_display(font_file):
    # station code and direction will be sent on init
    matrix = init_matrix()
    canvas = matrix.CreateFrameCanvas()

    nba_games = get_current_games('nba', NBA_TEAMS, UTC_OFFSET)
    draw_game(matrix, canvas, font_file, nba_games[0])
    while True:
        nba_games = get_current_games('nba', NBA_TEAMS, UTC_OFFSET)
        draw_game(matrix, canvas, font_file, nba_games[0])
        time.sleep(5)


def init_matrix():
    options = RGBMatrixOptions()
    options.rows = 32
    options.chain_length = 4
    options.pwm_bits = 3
    options.pwm_lsb_nanoseconds = 300
    options.gpio_slowdown = 2
    return RGBMatrix(options = options)


def draw_game(matrix, canvas, font_file, game):
    font = graphics.Font()
    font.LoadFont(font_file)

    canvas.Clear()

    # create logos
    away_response = requests.get(game['away_logo'])
    away_logo = Image.open(BytesIO(away_response.content)).resize((32,32),1)
    canvas.SetImage(away_logo.convert("RGB"), 0, 0)
    home_response = requests.get(game['home_logo'])
    home_logo = Image.open(BytesIO(home_response.content)).resize((32,32),1)
    canvas.SetImage(home_logo.convert("RGB"), 96, 0)
    canvas = matrix.SwapOnVSync(canvas)

    # create team names
#    graphics.DrawText(canvas, font, 0, 26, red_color, game['away_location'])
#    graphics.DrawText(canvas, font, 32, 28, red_color, game['away_team'])
    away_rgb = tuple(int(game['away_color'][i:i+2], 16) for i in (0, 2, 4))
    away_color = graphics.Color(away_rgb[0], away_rgb[1], away_rgb[2])
#    away_color = graphics.Color(2, 247, 96)
    away_color = graphics.Color(0, 71, 27)
    graphics.DrawText(canvas, font, 36, 30, away_color, game['away_abbreviation'])
    home_rgb = tuple(int(game['home_color'][i:i+2], 16) for i in (0, 2, 4))
    home_color = graphics.Color(home_rgb[0], home_rgb[1], home_rgb[2])
    graphics.DrawText(canvas, font, 74, 30, home_color, game['home_abbreviation'])
    graphics.DrawText(canvas, font, 61, 30, away_color, '@')

def serve():
    app.run(host="0.0.0.0")


if __name__ == "__main__":
#    server = Process(target = serve)
#    server.start()
    display_runner = Process(target = run_display, args = ['/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf'])
    display_runner.start()
