import enum
import numpy as np
from typing import List, Tuple

from numpy.core.numeric import identity

def run_matching(scores: List[List], gender_id: List, gender_pref: List) -> List[Tuple]:
    """
    TODO: Implement Gale-Shapley stable matching!
    :param scores: raw N x N matrix of compatibility scores. Use this to derive a preference rankings.
    :param gender_id: list of N gender identities (Male, Female, Non-binary) corresponding to each user
    :param gender_pref: list of N gender preferences (Men, Women, Bisexual) corresponding to each user
    :return: `matches`, a List of (Proposer, Acceptor) Tuples representing monogamous matches

    Some Guiding Questions/Hints:
        - This is not the standard Men proposing & Women receiving scheme Gale-Shapley is introduced as
        - Instead, to account for various gender identity/preference combinations, it would be better to choose a random half of users to act as "Men" (proposers) and the other half as "Women" (receivers)
            - From there, you can construct your two preferences lists (as seen in the canonical Gale-Shapley algorithm; one for each half of users
        - Before doing so, it is worth addressing incompatible gender identity/preference combinations (e.g. gay men should not be matched with straight men).
            - One easy way of doing this is setting the scores of such combinations to be 0
            - Think carefully of all the various (Proposer-Preference:Receiver-Gender) combinations and whether they make sense as a match
        - How will you keep track of the Proposers who get "freed" up from matches?
        - We know that Receivers never become unmatched in the algorithm.
            - What data structure can you use to take advantage of this fact when forming your matches?
        - This is by no means an exhaustive list, feel free to reach out to us for more help!
    """
    # choose half of population randomly to be proposers
    proposers = list(np.random.choice(len(scores), len(scores)//2, replace=False))
    receivers = []
    for i in range(len(scores)):
        if i not in proposers:
            receivers.append(i)

    # now we compile the rankings for each list, taking into account various gender identity/preference combos
    # helper function to do for proposers list and receivers list
    def score_sort(p_or_r):
        final = []
        to_match = receivers if p_or_r == proposers else proposers
        # we grab scores, modify as necessary based on preference/gender matchups
        for i in range(len(scores) // 2):
            ind_scores = []
            for j in to_match:
                ind_score = scores[p_or_r[i]][j]
                if gender_pref[p_or_r[i]] == 'Men' and gender_id[j] != 'Male':
                    ind_score = 0
                if gender_pref[p_or_r[i]] == 'Women' and gender_id[j] != 'Female':
                    ind_score = 0
                ind_scores.append((ind_score, j))
            final.append(ind_scores)
        # sort the individual lists, reverse for receivers
        if p_or_r == proposers:
            for i in final:
                i.sort()
        else:
            for i in final:
                i.sort(reverse=True)
        # we only care about the ranking now that we've sorted, so remove the scores
        final_clean = []
        for l in final:
            final_l = []
            for t in l:
                final_l.append(t[1])
            final_clean.append(final_l)        
        return final_clean
    proposer_scores = score_sort(proposers)
    receiver_scores = score_sort(receivers)

    # preparing to do regular gale shapley - need to convert given ids to indexes in 
    # proposer_scores and receiver_scores list, this is id_matching
    id_matching = [-1] * len(scores)
    for l_index, id in enumerate(proposers):
        id_matching[id] = l_index
    # same for receivers
    for l_index, id in enumerate(receivers):
        id_matching[id] = l_index

    # current matches, we change this as we go through below algorithm - initialize to
    # value we know means no_match, e.g., a number we know doesn't correspond to a 
    # proposer
    no_match = min(proposers) - 1
    matchings = [no_match] * len(receivers)

    # helper function for matching process - sets new match, removes all rankings up to 
    # this match in receiver's score list in future (we sorted this in rev!), lower ranks will
    # not appear in their score list anymore so the elif in Gale Shapley below will not be 
    # entered by these lower matches (AKA we ensure only have "trade ups" if enter that)
    def match_two(prop, receiver):
        matchings[id_matching[receiver]] = prop
        while receiver_scores[id_matching[receiver]][-1] != prop:
            receiver_scores[id_matching[receiver]].pop()

    # Gale Shapley cases
    while(proposers != []):
        # take advantage of pop to just grab props highest pref (proposer_scores sorted
        #  low to high) - can't use a for loop since proposers can be unmatched/fail to match
        prop = proposers.pop()
        # need pop() to get prop's highest pref, but also remove it if they fail (so later loops
        # have them trying second highest, third, etc)
        rec = proposer_scores[id_matching[prop]].pop()
        # unmatched receiver is easy, just match
        if matchings[id_matching[rec]] == no_match:
            match_two(prop, rec)
        # only entered when prop is better than old rec match - see match_two function above
        elif prop in receiver_scores[id_matching[rec]]:
            proposers.append(matchings[id_matching[rec]])
            match_two(prop, rec)
        # prop got shot down :(
        else:
            proposers.append(prop)

    # put these matchings into matches, format is proposer, receiver
    matches = []
    for r in receivers:
        matches.append((matchings[id_matching[r]], r))
    # print(matches)
    return matches

if __name__ == "__main__":
    raw_scores = np.loadtxt('raw_scores.txt').tolist()
    genders = []
    with open('genders.txt', 'r') as file:
        for line in file:
            curr = line[:-1]
            genders.append(curr)

    gender_preferences = []
    with open('gender_preferences.txt', 'r') as file:
        for line in file:
            curr = line[:-1]
            gender_preferences.append(curr)

    gs_matches = run_matching(raw_scores, genders, gender_preferences)