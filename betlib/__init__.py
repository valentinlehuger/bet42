import os

def get_bet_dir():
    bet_dir = os.environ["BET_PATH"]
    if bet_dir is None:
        print "BET_PATH environnement variable unset."
    return bet_dir

def get_user_password():
    bet_dir = get_bet_dir()
    with open(bet_dir + ".mongolab_register", "r") as f:
        lines = [x.replace("\n", "") for x in f.readlines()]
        f.close()
        if len(lines) == 2:
            return {"user": lines[0], "password":lines[1]}
    return None

# if __name__ == '__main__':
#         print get_user_password()
