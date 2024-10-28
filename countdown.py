import sys, json
from urllib.request import urlopen, Request
from datetime import datetime, timezone, timedelta

# Attempt the import of the pytz library, or try to install if not found
try:
    import pytz
except ImportError:
    try:
        import subprocess
        # Redirect stdout to void since rainmeter directly reads from stdout
        subprocess.check_call(['pip', 'install', 'pytz'],stdout=subprocess.DEVNULL)
        import pytz  # Try importing again
    except Exception as e:
        print("Error installing pytz:", str(e), end="")
        exit(1)

# Need a dictionary of teams to easily reference for valid team abbreviations and quick access to their team name
# Due to some teams not following convention I've had to improvise on a couple
teams_dict = {"ANA":"ANA Ducks", "BOS":"BOS Bruins", "BUF":"BUF Sabres", "CGY":"CGY Flames", "CAR":"CAR Hurricanes", "CHI":"CHI Blackhawks",
              "COL":"COL Avalanche", "CBJ":"CLB Blue Jackets", "DAL":"DAL Stars", "DET":"DET Red Wings", "EDM":"EDM Oilers", "FLA":"FLA Panthers", "LAK":"LA Kings", 
              "MIN":"MIN Wild", "MTL":"MTL Canadiens", "NSH":"NSH Predators", "NJD":"NJ Devils", "NYI":"NY Islanders", "NYR":"NY Rangers", "OTT":"OTT Senators",
              "PHI":"PHI Flyers", "PIT":"PIT Penguins", "SJS":"SJ Sharks", "SEA":"SEA Kraken", "STL":"STL Blues", "TBL":"TB Lightning", "TOR":"TOR Maple Leafs",
              "UTA":"UTA Hockey Club","VAN":"VAN Canucks", "VGK":"VGS Golden Knights", "WSH":"WSH Capitals", "WPG":"WPG Jets"}

header={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'}

def is_before_utc_timestamp(utc_timestamp):
    # Get current UTC time
    current_utc_time = datetime.now(tz=timezone.utc)
    # Convert utc_timestamp into a datetime object to compare
    given_utc_time = datetime.strptime(utc_timestamp, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=timezone.utc)

    # If the current utc time is before the provided time, return true
    return current_utc_time < given_utc_time

def is_dst_active():
    # Get the set time zone
    time_zone = pytz.timezone(sys.argv[2])
    
    current_time = pytz.utc.localize(datetime.now())

    # Compare time deltas to determine whether or not DST adjustment is in place
    return current_time.astimezone(time_zone).dst() != timedelta(0)

def team_abbr_to_full_name(team_abbr):
    return teams_dict[team_abbr]

team_abbr = sys.argv[1].upper()

# Check if they added an invalid team
if team_abbr not in teams_dict.keys():
    print("INVALID TEAM ABBR: ",team_abbr, end="")
    exit(1)

schedule_url = "https://api-web.nhle.com/v1/club-schedule-season/{abbr}/now".format(abbr=team_abbr)
# Make the NHL API request for the current season schedule, we need to set a fake user agent or we'll get a forbidden response
request = Request(schedule_url,headers=header)

# Open the URL and parse the response data into a json dictionary so we can begin querying 
with urlopen(request) as response:
    schedule_data = json.loads(response.read())

# Get the standings data so each team's record can be parsed out
standings_url = "https://api-web.nhle.com/v1/standings/{date}".format(date=datetime.today().strftime('%Y-%m-%d'))
request = Request(standings_url,headers=header)
with urlopen(request) as response:
    standings_data = json.loads(response.read())

for game in schedule_data["games"]:
    before = is_before_utc_timestamp(game["startTimeUTC"])
    game_type = int(game["gameType"])
    # The NHL API denotes pre-season games as game type '1'
    if before and game_type != 1:
        # Rainmeter will check the stdout stream so we output the following information formatted as such:
        #
        # dst
        # startTimeUTC
        # team vs./@ other team
        # team record
        # other team record
        # We can do any parsing or pull info using regex as necessary through rainmeter
        print(is_dst_active())
        print(game["startTimeUTC"])


        # Grab team abbreviations so we can output the set teams vs. or @ the opposing team
        home_team_abbr = game["homeTeam"]["abbrev"]
        away_team_abbr = game["awayTeam"]["abbrev"]
        if game["homeTeam"]["abbrev"] == team_abbr:
            print(teams_dict[team_abbr],"vs.",teams_dict[away_team_abbr])
        else:
            print(teams_dict[team_abbr],'@',teams_dict[home_team_abbr])
        break

team_record = "0 - 0 - 0"
away_record = "0 - 0 - 0"
for placement in standings_data["standings"]:
    abbr = placement["teamAbbrev"]["default"]
    wins = int(placement["wins"])
    losses = int(placement["losses"])
    otlosses = int(placement["otLosses"])
    record = "{wins} - {losses} - {otlosses}".format(wins=wins,losses=losses,otlosses=otlosses)
    if abbr == team_abbr:
        team_record = record
    elif abbr == home_team_abbr or abbr == away_team_abbr:
        away_record = record

print(team_record)
print(away_record,end="")