import re
def hashtag(des):
    pattern = re.compile("#(.*?)\s")
    result = pattern.search(des)
    if result:
        return result.group().replace(' ','')

def sport(des):
    sports_dict = {'soccer': 'Soccer', 'baseball': 'Baseball', 'nba': 'NBA', 'football': 'Fantasy Football',
                    'nfl': 'NFL', 'mlb': 'MLB', 'golf': 'Golf', 'tennis': 'Tennis',
                    'poker': 'Poker', 'college': 'College Football', 'motorsports': 'Motorsports'}
    token = des.split(' ')
    for each in token:
        if each.lower().replace('#', '') in sports_dict.keys():
            return sports_dict[each.lower().replace('#', '')]

    return None

def team(des):
    team_dict = {'raptors':'Toronto Raptors', 'toronto':'Toronto Raptors',
                'sfgiants':'SF Giants',
                'white':'White Sox',
                'dallas_cowboys':'Dallas Cowboys', 'cowboys': 'Dallas Cowboys',
                'dortmund':'Borussia Dortmund',
                'barcelona':'FC Barcelona',
                'ohio':'Ohio State Buckeyes',
                'indians':'Cleveland Indians',
                'Aggie':'Aggie',
                'liverpool':'Liverpool',
                'bruins': 'Boston Bruins',
                'spurs':'Spurs',
                'bayren':'FC Bayren', 'fcbayren': 'FC Bayren',
                'mardrid':'Real Mardrid',
                'vikings':'Minnesota Vikings',
                'worriors':'Golden State Worriors',
                'lakers':'LA Lakers', 'laker': 'LA Lakers',
                'arsenal':'Arsenal',
                'uga':'UGA',
                'blackhawks':'Blackhawks',
                'ucla':'UCLA Men',
                'packers':'Green Bay Packers',
                'dodgers':'LA Dodgers',
                'wildcats':'Arizona Wildcats',
                'chefs':'Kansas City Chefs',
                'tigers':'Detroit Tigers',
                'raiders':'Oakland Raiders', 'oakland': 'Oakland Raiders',
                'athletics': 'Athletics',
                'cubs':'Chicago Cubs',
                'braves':'Atlanta Braves',
                'villa':'Aston Villa',
                'red':'Red Sox',
                'bvb':'BVB',
                'everton':'Everton F.C.',
                'grizzlies':'Grizzlies',
                'redskins':'Washington Redskins', 'reds': 'Washington Redskins',
                'united':'Newcastle United',
                'ducks':'Oregon Ducks',
                'blues':'St. Louis Blues',
                'rockets':'Houston Rockets',
                'odu':'ODU',
                'astros':'Astros',
                'nationals':'Washinton Nationals',
                'utes':'Utah Utes',
                'tide':'Alabama Crimson Tide',
                'ravens':'Baltimore Ravens',
                'husker':'Nebraska Husker',
                'wild':'Minnesota Wild',
                'rangers':'Texas Rangers',
                'utd':'Man Utd',
                'giant':'New York Giant',
                'falcons':'Atlanta Falcons',
                'stl':'STL Cards',
                'cardinals':'Arizona Cardinals',
                'gators':'Florida Gators',
                'mu':'MU',
                'flames':'Calary Flames',
                'oilers':'Edmonton Oilers',
                'timbers':'Portland Timbers',
                'bills':'Buffalo Bills',
                'panthers':'Carolina Panthers',
                'bears':'Chicago Bears',
                'bengals':'Cincinnati Bengals',
                'browns':'Cleveland Browns',
                'broncos':'Denver Broncos',
                'lions':'Ditroit Lions',
                'texans':'Houston Texans',
                'colts':'Indianapoolis Colts',
                'jaguars':'Jacksonville Jaguars',
                'dolphins':'Miami Dolphins',
                'patriots':'New England Patriots',
                'saints':'New Orleans Saints',
                'jets':'New York Jets',
                'eagles':'Philadelphia Eagles',
                'steelers':'Pittsburgh Steelers',
                'chargers':'San Diego Chargers',
                '49ers':'San Francisco 49ers',
                'seahawks':'Seattle Seahawks',
                'rams':'St Louis Rams',
                'buccaneers':'Tampa Bay Buccaneers',
                'titans':'Tennessee Titans'}
    token = des.split(' ')
    for each in token:
        if each.lower() in team_dict.keys():
            return team_dict[each.lower()]
    
    return None

def label(des):
    pattern = re.compile('#(.*?)\s')
    result = pattern.search(des)
    if result:
        return result.group()
    
    pattern = re.compile('\"(.*?)\"')
    result = pattern.search(des)
    if result:
        return result.group().replace('"', '')
    
    pattern = re.compile('labeled\s(.*?)\s')
    result = pattern.search(des)
    if result:
        return result.group().replace('labeled ', '')
    
    return None

def weather(des):
    rain_pattern = re.compile('rain')
    result = rain_pattern.search(des.lower())
    if result:
        return 'Rain'
    
    snow_pattern = re.compile('snow')
    result = snow_pattern.search(des.lower())
    if result:
        return 'Snow'
    
    return None

print(weather('will it Rain tommorow'))