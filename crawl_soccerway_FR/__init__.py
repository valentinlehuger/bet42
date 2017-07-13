from bson import ObjectId

team_id_wrong = {
    # Arsenal de sarandi instead of Arsenal FC
    "559189ef973404276afa60c6": {
        "link": "sarandi",
        "new_id": ObjectId("55b238b7b878bc0aa8ce07a4")
    }
}

def         get_correct_team_id(team_id, link):
    # print team_id, link
    if str(team_id) in team_id_wrong and team_id_wrong[str(team_id)]["link"] in link:
        # print "here <="
        return team_id_wrong[str(team_id)]["new_id"]
    else:
        return team_id
