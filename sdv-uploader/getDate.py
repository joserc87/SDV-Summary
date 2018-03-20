from math import floor, ceil

day_list = {'1':'1st',
               '2':'2nd',
               '3':'3rd',
               '4':'4th',
               '5':'5th',
               '6':'6th',
               '7':'7th',
               '8':'8th',
               '9':'9th',
               '10':'10th',
               '11':'11th',
               '12':'12th',
               '13':'13th',
               '14':'14th',
               '15':'15th',
               '16':'16th',
               '17':'17th',
               '18':'18th',
               '19':'19th',
               '20':'20th',
               '21':'21st',
               '22':'22nd',
               '23':'23rd',
               '24':'24th',
               '25':'25th',
               '26':'26th',
               '27':'27th',
               '28':'28th'}

season_list = {'0':'Spring',
               '1':'Summer',
               '2':'Autumn',
               '3':'Winter'}

def get_date_string(dayOfMonthForSaveGame,seasonForSaveGame,yearForSaveGame):
    daystring = day_list.get(str(dayOfMonthForSaveGame),str(dayOfMonthForSaveGame))
    seastring = season_list.get(str(seasonForSaveGame),str(seasonForSaveGame))
    # formatted_string = daystring + _(' of ') + seastring + _(', Year ') + str(yearForSaveGame)
    formatted_string = '{} of {}, Year {}'.format(daystring,seastring,yearForSaveGame)
    return formatted_string

def preprocess_data(data):
    if data.get('dayOfMonthForSaveGame') != None and int(data.get('dayOfMonthForSaveGame')) > 28:
        data['dayOfMonthForSaveGame'] = str(int(data.get('dayOfMonthForSaveGame')) % 28)
        data['seasonForSaveGame'] = str(int(data['seasonForSaveGame']) + 1)
    if data.get('seasonForSaveGame') != None and int(data.get('seasonForSaveGame')) > 3:
        data['seasonForSaveGame'] = str(int(data.get('seasonForSaveGame')) % 4)
        data['yearForSaveGame'] = str(int(data['yearForSaveGame']) + 1)
    return data

def get_date_data(statsDaysPlayed):
    dayOfMonthForSaveGame = int(((statsDaysPlayed - 1) % 28) + 1)
    yearForSaveGame = int(floor((statsDaysPlayed - dayOfMonthForSaveGame) / (28*4)) + 1)
    seasonForSaveGame = int((floor((statsDaysPlayed - dayOfMonthForSaveGame)/28)) - ((yearForSaveGame-1)*4))
    return str(dayOfMonthForSaveGame), str(seasonForSaveGame), str(yearForSaveGame)

def get_date(data):
    data = preprocess_data(data)
    if data.get('dayOfMonthForSaveGame') != None and data.get('seasonForSaveGame') != None and data.get('yearForSaveGame') != None:
        return get_date_string(data['dayOfMonthForSaveGame'],data['seasonForSaveGame'],data['yearForSaveGame'])
    else:
        return None


def main():
    data = {'dayOfMonthForSaveGame':29,
            'seasonForSaveGame':3,
            'yearForSaveGame':2,
            'statsDaysPlayed':197+28}
    print(get_date(data))
    print(get_date_string(*get_date_data(data.get('statsDaysPlayed'))))

if __name__ == "__main__":
    main()