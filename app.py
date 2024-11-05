import streamlit as st
import json
import os
from dataclasses import dataclass
from typing import List, Tuple, Dict

# Reuse your existing CardMapping class
class CardMapping:
    SUITS = ['♥', '♣', '♦', '♠']
    VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    @staticmethod
    def format_cards_list(numbers):
        if not numbers:
            return "No cards"
            
        cards = [CardMapping.number_to_card(n) for n in numbers]
        suits = [CardMapping.get_suit_name(n) for n in numbers]
        
        sorted_cards = {}
        for card, suit in zip(cards, suits):
            if suit not in sorted_cards:
                sorted_cards[suit] = []
            sorted_cards[suit].append(card)
            
        output = []
        for suit in ['Hearts', 'Clubs', 'Diamonds', 'Spades']:
            if suit in sorted_cards:
                output.append(f"{suit}: {', '.join(sorted_cards[suit])}")
                
        return "\n".join(output)

    @staticmethod
    def number_to_card(number):
        if not 0 <= number <= 51:
            raise ValueError(f"Invalid card number: {number}")
        
        suit_index = number // 13
        value_index = number % 13
        
        return f"{CardMapping.SUITS[suit_index]}{CardMapping.VALUES[value_index]}"

    @staticmethod
    def get_suit_name(number):
        suits_names = ['Hearts', 'Clubs', 'Diamonds', 'Spades']
        return suits_names[number // 13]

@dataclass
class Trick:
    title: str
    active: bool
    requirements: List[Tuple[int, str]]

def calculate_sets(num_decks: int, requirements: List[Tuple[int, str]]) -> Tuple[int, int]:
    # Your existing calculate_sets function here
    if not requirements:
        return 0, num_decks * 52

    max_cards_needed = max(count for count, req_type in requirements if req_type == "identical")
    if max_cards_needed > num_decks:
        return 0, num_decks * 52

    total_cards = num_decks * 52
    
    identical_reqs = []
    any_reqs = []
    for count, req_type in requirements:
        if req_type == "identical":
            identical_reqs.append(count)
        else:
            any_reqs.append(count)
    
    if len(identical_reqs) == 2 and identical_reqs[0] == identical_reqs[1]:
        cards_needed = identical_reqs[0]
        sets_per_number = num_decks // cards_needed
        number_pairs = 52 // 2
        possible_sets = sets_per_number * number_pairs
    else:
        possible_sets = total_cards // sum(identical_reqs)
            
    cards_per_set = sum(req for req in identical_reqs)
    used_cards = possible_sets * cards_per_set
    remaining_cards = total_cards - used_cards

    return int(possible_sets), remaining_cards

def calculate_max_combinations(num_decks: int, tricks: List[Trick]) -> Tuple[Dict, int]:
    # Your existing calculate_max_combinations function here
    # (Keep the implementation, just update the type hints)
    total_cards = num_decks * 52
    combinations = {}
    
    tricks_info = []
    for trick in tricks:
        if not trick.requirements:
            continue
            
        cards_per_set = sum(count for count, req_type in trick.requirements 
                          if req_type == "identical")
        
        max_sets, _ = calculate_sets(num_decks, trick.requirements)
        
        if max_sets > 0:
            tricks_info.append({
                'title': trick.title,
                'cards_per_set': cards_per_set,
                'max_sets': max_sets,
                'requirements': trick.requirements
            })
    
    if not tricks_info:
        return {}, total_cards
        
    available_cards = total_cards
    num_tricks = len(tricks_info)
    cards_per_trick = available_cards // num_tricks
    
    target_sets = []
    for trick in tricks_info:
        possible_sets = min(
            cards_per_trick // trick['cards_per_set'],
            trick['max_sets']
        )
        target_sets.append(possible_sets)
    
    min_target = min(target_sets)
    
    for trick in tricks_info:
        sets_for_trick = min_target
        cards_needed = sets_for_trick * trick['cards_per_set']
        
        if cards_needed <= available_cards:
            combinations[trick['title']] = {
                'sets': sets_for_trick,
                'cards_used': cards_needed,
                'requirements': trick['requirements']
            }
            available_cards -= cards_needed
    
    while available_cards > 0:
        added_sets = False
        for trick in tricks_info:
            if trick['title'] in combinations:
                current = combinations[trick['title']]
                
                if (current['sets'] < trick['max_sets'] and 
                    available_cards >= trick['cards_per_set']):
                    
                    current['sets'] += 1
                    current['cards_used'] += trick['cards_per_set']
                    available_cards -= trick['cards_per_set']
                    added_sets = True
                    
        if not added_sets:
            break
    
    return combinations, available_cards

# Initialize session state
if 'tricks' not in st.session_state:
    st.session_state.tricks = []

# App title
st.title('Card Trick Set Manager')

# Deck configuration
st.header('Deck Configuration')
num_decks = st.number_input('Number of Decks:', min_value=1, value=1)

# Tricks management
st.header('Trick Sets')

# Add new trick
if st.button('Add New Trick Set'):
    st.session_state.tricks.append(Trick(
        title="New Trick",
        active=True,
        requirements=[]
    ))

# Display and edit tricks
for i, trick in enumerate(st.session_state.tricks):
    with st.expander(f"Trick Set {i+1}: {trick.title}"):
        # Title and active status
        new_title = st.text_input('Title:', trick.title, key=f"title_{i}")
        new_active = st.checkbox('Active', trick.active, key=f"active_{i}")
        
        # Requirements
        st.subheader('Requirements')
        new_requirements = []
        for j, (count, req_type) in enumerate(trick.requirements):
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                new_count = st.number_input('Count:', min_value=1, value=count, key=f"count_{i}_{j}")
            with col2:
                new_type = st.selectbox('Type:', ['identical', 'any'], 
                                      index=0 if req_type == 'identical' else 1,
                                      key=f"type_{i}_{j}")
            with col3:
                if st.button('Remove', key=f"remove_{i}_{j}"):
                    continue
            new_requirements.append((new_count, new_type))
        
        if st.button('Add Requirement', key=f"add_req_{i}"):
            new_requirements.append((1, 'identical'))
        
        # Update trick
        st.session_state.tricks[i] = Trick(
            title=new_title,
            active=new_active,
            requirements=new_requirements
        )
        
        # Delete trick
        if st.button('Delete Trick Set', key=f"delete_{i}"):
            st.session_state.tricks.pop(i)
            st.experimental_rerun()

# Calculate results
if st.button('Calculate Sets'):
    st.header('Results')
    
    # Get active tricks
    active_tricks = [trick for trick in st.session_state.tricks if trick.active]
    
    # Individual calculations
    st.subheader('Individual Calculations')
    for trick in active_tricks:
        if trick.requirements:
            possible_sets, remaining_cards = calculate_sets(num_decks, trick.requirements)
            st.write(f"**{trick.title}:**")
            st.write(f"- Possible Sets: {possible_sets}")
            st.write(f"- Remaining Cards: {remaining_cards}")
    
    # Optimal combination
    st.subheader('Optimal Combination')
    combinations, total_remaining = calculate_max_combinations(num_decks, active_tricks)
    
    if combinations:
        total_sets = 0
        total_cards_used = 0
        
        for trick_name, data in combinations.items():
            st.write(f"\n**{trick_name}:**")
            num_sets = data['sets']
            cards_used = data['cards_used']
            total_sets += num_sets
            total_cards_used += cards_used
            
            st.write(f"- Sets: {num_sets}")
            st.write(f"- Cards Used: {cards_used}")
            
            st.write("Requirements:")
            for count, req_type in data['requirements']:
                if req_type == "identical":
                    st.write(f"- {count} identical cards")
                    example_cards = list(range(min(count, 13)))
                    st.write(CardMapping.format_cards_list(example_cards))
                else:
                    st.write(f"- {count} any cards")
        
        # Summary
        st.subheader('Summary')
        st.write(f"Total Number of Sets: {total_sets}")
        st.write(f"Total Cards Used: {total_cards_used}")
        st.write(f"Remaining Cards: {total_remaining}")
        
        if total_remaining > 0:
            st.write("\nExamples of remaining cards:")
            example_remaining = list(range(min(13, total_remaining)))
            st.write(CardMapping.format_cards_list(example_remaining))
    else:
        st.write("No possible combinations found.")
