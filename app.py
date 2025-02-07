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
NBA_TEAMS = ['Milwaukee Bucks', 'Los Angeles Lakers', 'Orlando Magic']
NCAAFB_TEAMS = ['Wisconsin Badgers']
NCAABB_TEAMS = ['Wisconsin Badgers', 'Marquette Golden Eagles']
MLB_TEAMS = ['Milwaukee Brewers', 'Chicago Cubs']
FONT_PATH = '/home/scott.underwood/Documents/sports-sign/rpi-rgb-led-matrix/fonts/'

app = Flask(__name__)

class SportsDisplay:
    def __init__(self, nfl_teams, ncaafb_teams, nba_teams, ncaabb_teams, mlb_teams):
        self.teams = {'nfl': nfl_teams,
                      'ncaafb': ncaafb_teams,
                      'nba': nba_teams,
                      'ncaabb': ncaabb_teams,
                      'mlb': mlb_teams}
        self.current_display = None
        self.matrix = self.init_matrix()
        self.canvas = self.matrix.CreateFrameCanvas()


    def run(self):
        self.find_games()
        self.determine_games_to_display()


    def find_games(self):
        self.games = []
        for sport in ['nfl', 'ncaafb', 'nba', 'ncaabb', 'mlb']:
            self.games = self.games + get_current_games(sport, self.teams[sport], UTC_OFFSET)
            self.unique_statuses = list(set([game['status'] for game in self.games]))


    def determine_games_to_display(self):
        if len(self.games) == 0:
            self.run_display_no_games()
        if 'STATUS_IN_PROGRESS' in self.unique_statuses:
            self.games = [game for game in self.games if game['status'] == 'STATUS_IN_PROGRESS'] # only keep in progress games right now
            # function that runs in-progress game(s)
            self.run_display_live()
        else:
            # function that rotates through scheduled and final games
            self.run_display_not_live()


    def display_change_needed(self, game):
        if game == self.current_display:
            return False
        return True


    def run_display_not_live(self):
        # cycle through games, displaying one per 30 seconds
        for game in self.games:
            if self.display_change_needed(game):
                if game['status'] == 'STATUS_SCHEDULED':
            	    self.draw_pregame(game)
                elif game['status'] == 'STATUS_FINAL':
                    self.draw_postgame(game)
            time.sleep(30)

        self.run()


    def run_display_no_games(self):
        if self.display_change_needed('No games'):
            font = graphics.Font()
            font.LoadFont(FONT_PATH+'9x15B.bdf')
            self.canvas.Clear()
            color = graphics.Color(255, 255, 255)
            graphics.DrawText(self.canvas, font, 28, 14, color, 'NO GAMES')
            graphics.DrawText(self.canvas, font, 37, 28, color, 'TODAY!')
            self.current_display = 'No games'
            self.canvas = self.matrix.SwapOnVSync(self.canvas)

        time.sleep(30)
        self.run()


    def run_display_live(self):
        # cycle through games, displaying one per 30 seconds
        for game in self.games:
            if self.display_change_needed(game):
                self.draw_pregame(game)
            time.sleep(30)
        self.run()


    def init_matrix(self):
        options = RGBMatrixOptions()
        options.rows = 32
        options.chain_length = 4
        options.pwm_bits = 3
        options.pwm_lsb_nanoseconds = 300
        options.gpio_slowdown = 2
        return RGBMatrix(options = options)


    def draw_pregame(self, game):
        font_large = graphics.Font()
        font_large.LoadFont(FONT_PATH+'8x13B.bdf')

        self.canvas.Clear()

        # create team names
        away_rgb = tuple(int(game['away_color'][i:i+2], 16) for i in (0, 2, 4))
        away_color = graphics.Color(away_rgb[0], away_rgb[1], away_rgb[2])
        home_rgb = tuple(int(game['home_color'][i:i+2], 16) for i in (0, 2, 4))
        home_color = graphics.Color(home_rgb[0], home_rgb[1], home_rgb[2])
        text_color = graphics.Color(255, 255, 255)

        graphics.DrawText(self.canvas, font_large, 34 if len(game['away_abbreviation']) == 3 else 39, 28, text_color, game['away_abbreviation'])
        graphics.DrawText(self.canvas, font_large, 70 if len(game['home_abbreviation']) == 3 else 75, 28, text_color, game['home_abbreviation'])
        graphics.DrawText(self.canvas, font_large, 60, 28, text_color, '@')

        # write game time
        game_time = game['time']
        game_time_str = game_time.strftime('%I:%M %p')
        graphics.DrawText(self.canvas, font_large, 34, 14, text_color, game_time_str.split(' ')[0])
        graphics.DrawText(self.canvas, font_large, 78, 14, text_color, game_time_str.split(' ')[1])

        # create logos
        away_response = requests.get(game['away_logo'])
        away_logo = Image.open(BytesIO(away_response.content)).resize((32,32),1)
        self.canvas.SetImage(away_logo.convert("RGB"), 0, 0)
        home_response = requests.get(game['home_logo'])
        home_logo = Image.open(BytesIO(home_response.content)).resize((32,32),1)
        self.canvas.SetImage(home_logo.convert("RGB"), 96, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        self.current_display = game


    def draw_postgame(self, game):
        font_small = graphics.Font()
        font_small.LoadFont(FONT_PATH+'5x8.bdf')

        font_large = graphics.Font()
        font_large.LoadFont(FONT_PATH+'8x13B.bdf')

        self.canvas.Clear()

        # create team names
        away_rgb = tuple(int(game['away_color'][i:i+2], 16) for i in (0, 2, 4))
        away_color = graphics.Color(away_rgb[0], away_rgb[1], away_rgb[2])
        home_rgb = tuple(int(game['home_color'][i:i+2], 16) for i in (0, 2, 4))
        home_color = graphics.Color(home_rgb[0], home_rgb[1], home_rgb[2])
        text_color = graphics.Color(255, 255, 255)

        graphics.DrawText(self.canvas, font_large, 34 if len(game['away_abbreviation']) == 3 else 39, 30, text_color, game['away_abbreviation'])
        graphics.DrawText(self.canvas, font_large, 70 if len(game['home_abbreviation']) == 3 else 75, 30, text_color, game['home_abbreviation'])
        graphics.DrawText(self.canvas, font_large, 60, 30, text_color, '@')

        # write game score/time
        graphics.DrawText(self.canvas, font_small, 52, 19, text_color, 'FINAL')
        graphics.DrawText(self.canvas, font_large, 34 if int(game['away_score']) >= 100 else 39, 12, text_color, game['away_score'])
        graphics.DrawText(self.canvas, font_large, 70 if int(game['home_score']) >= 100 else 75, 12, text_color, game['home_score'])

        # create logos
        away_response = requests.get(game['away_logo'])
        away_logo = Image.open(BytesIO(away_response.content)).resize((32,32),1)
        self.canvas.SetImage(away_logo.convert("RGB"), 0, 0)
        home_response = requests.get(game['home_logo'])
        home_logo = Image.open(BytesIO(home_response.content)).resize((32,32),1)
        self.canvas.SetImage(home_logo.convert("RGB"), 96, 0)
        self.canvas = self.matrix.SwapOnVSync(self.canvas)

        self.current_display = game


    # def serve(self):
    #     app.run(host="0.0.0.0")


if __name__ == "__main__":
#    server = Process(target = serve)
#    server.start()
    # display_runner = Process(target = run_display, args = ['/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf'])
    # display_runner.start()
    display = SportsDisplay(NFL_TEAMS, NCAAFB_TEAMS, NBA_TEAMS, NCAABB_TEAMS, MLB_TEAMS)
    display.run()
