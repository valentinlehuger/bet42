from betlib.models.game import find_games, update_game
from betlib.models.team import find_team_by_link, add_team_alias, add_link_alias, remove_team

links_to_merge = {
    # FROM     :     TO
    "/teams/brazil/sao-paulo-futebol-clube/302/": "/teams/brazil/sao-paulo/33109/"             #Sao Paulo
}



for link in links_to_merge:

    team = find_team_by_link(link)
    main_team = find_team_by_link(links_to_merge[link])

    if team is None or team["_id"] == main_team["_id"]:
        continue
    add_team_alias(main_team["name"], team["name"])
    add_link_alias(main_team["link"], team["link"])

    for g in find_games({"team_H": team["_id"]}):
        update_game({"_id": g["_id"]}, {"team_H": main_team["_id"]})

    for g in find_games({"team_A": team["_id"]}):
        update_game({"_id": g["_id"]}, {"team_A": main_team["_id"]})

    remove_team({"_id": team["_id"]})



# mettre a jour le main team [OK]
# mettre a jour tous les matchs avec link_to_merge [OK]
# supprimer la team a merger [OK]
# updater find_team_by_link [OK]
