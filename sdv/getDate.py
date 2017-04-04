from math import floor, ceil
from flask_babel import _, lazy_gettext

day_list = {'1':lazy_gettext('1st'),
               '2':lazy_gettext('2nd'),
               '3':lazy_gettext('3rd'),
               '4':lazy_gettext('4th'),
               '5':lazy_gettext('5th'),
               '6':lazy_gettext('6th'),
               '7':lazy_gettext('7th'),
               '8':lazy_gettext('8th'),
               '9':lazy_gettext('9th'),
               '10':lazy_gettext('10th'),
               '11':lazy_gettext('11th'),
               '12':lazy_gettext('12th'),
               '13':lazy_gettext('13th'),
               '14':lazy_gettext('14th'),
               '15':lazy_gettext('15th'),
               '16':lazy_gettext('16th'),
               '17':lazy_gettext('17th'),
               '18':lazy_gettext('18th'),
               '19':lazy_gettext('19th'),
               '20':lazy_gettext('20th'),
               '21':lazy_gettext('21st'),
               '22':lazy_gettext('22nd'),
               '23':lazy_gettext('23rd'),
               '24':lazy_gettext('24th'),
               '25':lazy_gettext('25th'),
               '26':lazy_gettext('26th'),
               '27':lazy_gettext('27th'),
               '28':lazy_gettext('28th')}

season_list = {'0':lazy_gettext('Spring'),
               '1':lazy_gettext('Summer'),
               '2':lazy_gettext('Autumn'),
               '3':lazy_gettext('Winter')}

def get_date_string(dayOfMonthForSaveGame,seasonForSaveGame,yearForSaveGame):
    daystring = day_list.get(str(dayOfMonthForSaveGame),str(dayOfMonthForSaveGame))
    seastring = season_list.get(str(seasonForSaveGame),str(seasonForSaveGame))
    formatted_string = daystring + _(' of ') + seastring + _(', Year ') + str(yearForSaveGame)
    return formatted_string

def get_date_data(statsDaysPlayed):
    dayOfMonthForSaveGame = int(((statsDaysPlayed - 1) % 28) + 1)
    yearForSaveGame = int(floor((statsDaysPlayed - dayOfMonthForSaveGame) / (28*4)) + 1)
    seasonForSaveGame = int((floor((statsDaysPlayed - dayOfMonthForSaveGame)/28)) - ((yearForSaveGame-1)*4))
    return str(dayOfMonthForSaveGame), str(seasonForSaveGame), str(yearForSaveGame)

def get_date(data):
    if data.get('dayOfMonthForSaveGame') != None and data.get('seasonForSaveGame') != None and data.get('yearForSaveGame') != None:
        return get_date_string(data['dayOfMonthForSaveGame'],data['seasonForSaveGame'],data['yearForSaveGame'])
    else:
        assert data.get('statsDaysPlayed') != None
        return get_date_string(*get_date_data(data['statsDaysPlayed']))