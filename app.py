from flask import Flask, render_template
from get_data import get_current_games
from io import BytesIO
from multiprocessing import Process
from PIL import Image
import requests
# from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time


UTC_OFFSET = -5
NFL_TEAMS = ['Green Bay Packers', 'Washington Commanders']
NBA_TEAMS = ['Milwaukee Bucks', 'Utah Jazz', 'Orlando Magic']
NCAAFB_TEAMS = ['Wisconsin Badgers']
NCAABB_TEAMS = ['Wisconsin Badgers', 'Marquette Golden Eagles']
MLB_TEAMS = ['Milwaukee Brewers', 'Chicago Cubs']
FONT_FILE = '/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf'

app = Flask(__name__)

class SportsDisplay:
    def __init__(self, nfl_teams, ncaafb_teams, nba_teams, ncaabb_teams, mlb_teams):
        self.teams = {'nfl': nfl_teams, 
                      'ncaafb': ncaafb_teams, 
                      'nba': nba_teams, 
                      'ncaabb': ncaabb_teams, 
                      'mlb': mlb_teams}
        
    
    def run(self):
        self.find_games()
        self.determine_games_to_display()


    def find_games(self):
        self.games = []
        for sport in ['nfl', 'ncaafb', 'nba', 'ncaabb', 'mlb']:
            self.games = self.games + get_current_games(sport, self.teams[sport], UTC_OFFSET)
            self.unique_statuses = list(set([game['status'] for game in self.games]))


    def determine_games_to_display(self):
        if 'STATUS_IN_PROGRESS' in self.unique_statuses:
            self.games = [game for game in self.games if game['status'] == 'STATUS_IN_PROGRESS'] # only keep in progress games right now
            # function that runs in-progress game(s)
            # self.run_display_live()
        else:
            # function that rotates through scheduled and final games
            self.run_display_not_live()


    def run_display_not_live(self):
        self.matrix = self.init_matrix()
        self.canvas = self.matrix.CreateFrameCanvas()

        # cycle through games, displaying one per 30 seconds
        for game in self.games:
            print(game)
            self.draw_game(game)
            time.sleep(30)


    def init_matrix(self):
        options = RGBMatrixOptions()
        options.rows = 32
        options.chain_length = 4
        options.pwm_bits = 3
        options.pwm_lsb_nanoseconds = 300
        options.gpio_slowdown = 2
        return RGBMatrix(options = options)


    def draw_game(self, game):
        font = graphics.Font()
        font.LoadFont(FONT_FILE)

        canvas.Clear()

        # create logos
        away_response = requests.get(game['away_logo'])
        away_logo = Image.open(BytesIO(away_response.content)).resize((32,32),1)
        canvas.SetImage(away_logo.convert("RGB"), 0, 0)
        home_response = requests.get(game['home_logo'])
        home_logo = Image.open(BytesIO(home_response.content)).resize((32,32),1)
        canvas.SetImage(home_logo.convert("RGB"), 96, 0)
        canvas = self.matrix.SwapOnVSync(canvas)

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

    # def serve(self):
    #     app.run(host="0.0.0.0")


if __name__ == "__main__":
#    server = Process(target = serve)
#    server.start()
    # display_runner = Process(target = run_display, args = ['/home/scott.underwood/Documents/sports-sign/sports-display/6x10.bdf'])
    # display_runner.start()
    display = SportsDisplay(NFL_TEAMS, NCAAFB_TEAMS, NBA_TEAMS, NCAABB_TEAMS, MLB_TEAMS)
    display.run()
