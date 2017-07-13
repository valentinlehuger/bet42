from betlib.models.season import find_season, find_season_by_championship_years
from bson import ObjectId

class TestBetlibModelsSeason():

    def __init__ (self):
        print "init testBetlibModelSeason"

    def test_find_season(self):
        assert find_season({"championship": ObjectId("548c8ea4973404e997673c56") , "years": [2014, 2015]})

    def test_find_season_by_championship_years(self):

        assert find_season_by_championship_years("ligue_1", [2014, 2015]).get("_id", "") == ObjectId("549ac390249fe39f70587d80")

        assert find_season_by_championship_years("ligue_1", [2515, 2516]) is None
