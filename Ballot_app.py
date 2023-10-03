import streamlit as st
from collections import namedtuple

# Define the Pair namedtuple
Pair = namedtuple('Pair', ['winner', 'loser'])

# Global variables for Tideman
MAX = 9
preferences = [[0 for _ in range(MAX)] for _ in range(MAX)]
locked = [[False for _ in range(MAX)] for _ in range(MAX)]
pairs = [Pair(winner=None, loser=None) for _ in range(MAX * (MAX - 1) // 2)]
pair_count = 0
candidate_count = 0
candidate_names = []

def record_preferences(ranks):
    global preferences
    for i in range(len(ranks)):
        for j in range(i + 1, len(ranks)):
            preferences[ranks[i]][ranks[j]] += 1

def add_pairs():
    global pairs, pair_count, candidate_count
    for i in range(candidate_count):
        for j in range(candidate_count):
            if preferences[i][j] > preferences[j][i]:
                pairs[pair_count] = Pair(winner=i, loser=j)
                pair_count += 1

def sort_pairs():
    global pairs, pair_count
    pairs = sorted(pairs[:pair_count], key=lambda pair: preferences[pair.winner][pair.loser] - preferences[pair.loser][pair.winner], reverse=True)

def has_cycle(winner, loser):
    if winner == loser:
        return True
    for i in range(candidate_count):
        if locked[loser][i] and has_cycle(winner, i):
            return True
    return False

def lock_pairs():
    global pairs, pair_count
    for i in range(pair_count):
        if not has_cycle(pairs[i].winner, pairs[i].loser):
            locked[pairs[i].winner][pairs[i].loser] = True

def get_winners():
    global candidate_count, candidate_names
    sources = []
    for i in range(candidate_count):
        is_source = True
        for j in range(candidate_count):
            if locked[j][i]:
                is_source = False
                break
        if is_source:
            sources.append(candidate_names[i])
    return sources

def main():
    global candidate_count, candidate_names

    st.title("Tideman Voting System")

    # Number of candidates
    candidate_count = st.number_input("Enter number of candidates (between 1 to 9):", min_value=1, max_value=9, value=3, step=1)
    candidate_names = [st.text_input(f"Enter name for candidate {i+1}:") for i in range(candidate_count)]

    # Number of voters
    voter_count = st.number_input("Enter number of voters:", min_value=1, max_value=100, value=5, step=1)

    # Collect votes
    all_votes = []
    submit_active = True
    for i in range(voter_count):
        st.subheader(f"Voter {i+1}")
        votes = []
        options = candidate_names.copy()
        for j in range(candidate_count):
            vote = st.selectbox(f"Rank {j+1}:", options=["Select a candidate"] + options, key=f"voter_{i}_rank_{j}")
            if vote == "Select a candidate":
                submit_active = False
            else:
                options.remove(vote)
            votes.append(vote)
        all_votes.append(votes)

    if st.button("Submit") and submit_active:
        # Convert votes to ranks and record preferences
        global preferences, locked, pairs, pair_count
        preferences = [[0 for _ in range(MAX)] for _ in range(MAX)]
        locked = [[False for _ in range(MAX)] for _ in range(MAX)]
        pairs = [Pair(winner=None, loser=None) for _ in range(MAX * (MAX - 1) // 2)]
        pair_count = 0

        for votes in all_votes:
            ranks = [candidate_names.index(vote) for vote in votes]
            record_preferences(ranks)

        # Add pairs, sort them, lock pairs, and get the winner
        add_pairs()
        sort_pairs()
        lock_pairs()

        # Determine and display the winner
        winners = get_winners()
        if len(winners) == 1:
            st.write(f"The winner is: {winners[0]}")
        elif len(winners) > 1:
            winners_str = ", ".join(winners)
            st.write(f"There is a tie between: {winners_str}")
        else:
            st.write("No Winner!")

        # Display the points for each candidate
        st.subheader("Points for Each Candidate")
        for i, candidate in enumerate(candidate_names):
        # Count the number of times candidate 'i' is preferred over other candidates
            points = sum(1 for j in range(candidate_count) if preferences[i][j] > preferences[j][i])
            st.write(f"{candidate}: {points} matchups won")

if __name__ == "__main__":
    main()