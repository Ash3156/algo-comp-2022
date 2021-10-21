#!usr/bin/env python3
import json
import sys
import os

INPUT_FILE = 'testdata.json' # Constant variables are usually in ALL CAPS

class User:
    def __init__(self, name, gender, preferences, grad_year, responses):
        self.name = name
        self.gender = gender
        self.preferences = preferences
        self.grad_year = grad_year
        self.responses = responses


# Takes in two user objects and outputs a float denoting compatibility
def compute_score(user1, user2):
    # overall view was survey responses matter the most - a perfect match (score = 1.0) is for two users who's preferences match
    # the other user, have the same grad_year, and have identical responses (plus some random stuff like same first letter).
    # We have a "weight" that reduces the score from responses + random stuff by some factor (decreases for differing grad years).
    # Current version has preference matches between 1-2, non-preference matches between 0-1 (could ignore 0-1 if not interested).
    # Range of values (ignoring 0-1 and 1-2 ranges) on this data is min score .04 (Ashley/Chiara) and max .47 (Ashley/Melissa).

    weight = 1.0

    # grad_year analysis - weights very subjective
    grad_diff_weights = {0:1, 1:0.9, 2:0.7, 3:0.5}
    grad_diff = abs(user1.grad_year - user2.grad_year)
    weight *= grad_diff_weights[grad_diff]

    # response analysis
    response_score = 0
    for i in range(len(user1.responses)):
        if user1.responses[i] == user2.responses[i]:
            response_score += 1

    # name analysis - if first letter of name matches, worth 1 question ("21" questions to match on)
    if user1.name[0] == user2.name[0]:
        response_score += 1
    print(response_score)
    final_score = (response_score / 21.0) * weight

    if user2.gender in user1.preferences and user1.gender in user2.preferences:
        # another way is normalized score 0-2, where 0-1 is for "friend" matches and 1-2 is preference matches 
        # - if dont care then set weight=0 before line 42
        final_score += 1

    return final_score

if __name__ == '__main__':
    # Make sure input file is valid
    if not os.path.exists(INPUT_FILE):
        print('Input file not found')
        sys.exit(0)

    users = []
    with open(INPUT_FILE) as json_file:
        data = json.load(json_file)
        for user_obj in data['users']:
            new_user = User(user_obj['name'], user_obj['gender'],
                            user_obj['preferences'], user_obj['gradYear'],
                            user_obj['responses'])
            users.append(new_user)

    for i in range(len(users)-1):
        for j in range(i+1, len(users)):
            user1 = users[i]
            user2 = users[j]
            score = compute_score(user1, user2)
            print('Compatibility between {} and {}: {}'.format(user1.name, user2.name, score))
