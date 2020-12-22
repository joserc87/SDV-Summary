# from sdv-summary / upload.farm


def get_player_info(xmldata):
    playerTags = [
        "name",
        "farmName",
        "dateStringForSaveGame",
        "millisecondsPlayed",
        "dayOfMonthForSaveGame",
        "seasonForSaveGame",
        "yearForSaveGame",
    ]
    root = xmldata.getRoot()
    player = root.find("player")
    info = {}

    # Collect information stored in the player tag
    for tag in playerTags:
        try:
            if player.find(tag).text != None:
                info[tag] = player.find(tag).text
        except:
            pass
    info["uniqueIDForThisGame"] = int(root.find("uniqueIDForThisGame").text)

    season = root.find("currentSeason").text
    info["currentSeason"] = season

    return info


def main():
    pass


if __name__ == "__main__":
    main()
