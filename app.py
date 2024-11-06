import streamlit as st
import json
from collections import defaultdict

# Custom styling für die gesamte App
def apply_custom_style():
    st.markdown("""
        <style>
        /* Grundlegende Reset-Styles */
        .stApp {
            max-width: 960px;
            margin: 0 auto;
            padding: 1rem;
        }
        
        /* Container-Styles */
        .custom-container {
            border: 2px solid #ccc;
            border-radius: 4px;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: #f5f5f5;
        }
        
        /* Header-Styles */
        .container-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
        }
        
        /* Input-Feld-Styles */
        .stTextInput > div > div > input {
            border: 1px solid #ccc;
            border-radius: 2px;
            padding: 0.5rem;
        }
        
        /* Checkbox-Styles */
        .stCheckbox {
            margin: 0.5rem 0;
        }
        
        /* Button-Styles */
        .stButton > button {
            width: 100%;
            border: 1px solid #ccc;
            background-color: #f8f9fa;
            color: #333;
            padding: 0.5rem;
            margin: 0.5rem 0;
        }
        
        .stButton > button:hover {
            background-color: #e9ecef;
        }
        
        /* Trick-Container-Style */
        .trick-container {
            border: 1px solid #ddd;
            border-radius: 2px;
            padding: 0.8rem;
            margin: 0.5rem 0;
            background-color: white;
        }
        
        /* Requirements-Container */
        .requirements-container {
            margin-left: 1rem;
            padding: 0.5rem;
            border-left: 2px solid #eee;
        }
        
        /* Delete-Button */
        .delete-button {
            color: red;
            cursor: pointer;
            float: right;
        }
        
        /* Results-Bereich */
        .results-area {
            font-family: monospace;
            padding: 1rem;
            background-color: white;
            border: 1px solid #ddd;
            white-space: pre-wrap;
        }
        
        /* Expander-Style */
        .streamlit-expanderHeader {
            font-size: 1rem;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

# Initialisiere Session State falls noch nicht vorhanden
if 'tricks' not in st.session_state:
    st.session_state.tricks = []
    
if 'next_id' not in st.session_state:
    st.session_state.next_id = 0

class CardMapping:
    SUITS = ['♥', '♣', '♦', '♠']
    VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    @staticmethod
    def number_to_card(number):
        if not 0 <= number <= 51:
            raise ValueError(f"Invalid card number: {number}")
        suit_index = number // 13
        value_index = number % 13
        return f"{CardMapping.SUITS[suit_index]}{CardMapping.VALUES[value_index]}"
    
    @staticmethod
    def format_cards_list(numbers):
        if not numbers:
            return "No cards"
        cards = [CardMapping.number_to_card(n) for n in numbers]
        suits = [CardMapping.get_suit_name(n) for n in numbers]
        sorted_cards = defaultdict(list)
        for card, suit in zip(cards, suits):
            sorted_cards[suit].append(card)
        output = []
        for suit in ['Hearts', 'Clubs', 'Diamonds', 'Spades']:
            if sorted_cards[suit]:
                output.append(f"{suit}: {', '.join(sorted_cards[suit])}")
        return "\n".join(output)
    
    @staticmethod
    def get_suit_name(number):
        suits_names = ['Hearts', 'Clubs', 'Diamonds', 'Spades']
        return suits_names[number // 13]

def calculate_sets(num_decks, requirements):
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
        possible_sets = total_cards // sum(identical_reqs) if identical_reqs else 0

    cards_per_set = sum(identical_reqs)
    used_cards = possible_sets * cards_per_set
    remaining_cards = total_cards - used_cards

    return int(possible_sets), remaining_cards

def calculate_max_combinations(num_decks, tricks_data):
    total_cards = num_decks * 52
    combinations = {}
    
    # Sammle Informationen über alle Tricks
    tricks_info = []
    for trick in tricks_data:
        if not trick['requirements']:
            continue
            
        cards_per_set = sum(count for count, req_type in trick['requirements'] 
                          if req_type == "identical")
        
        max_sets, _ = calculate_sets(num_decks, trick['requirements'])
        
        if max_sets > 0:
            tricks_info.append({
                'title': trick['name'],
                'cards_per_set': cards_per_set,
                'max_sets': max_sets,
                'requirements': trick['requirements']
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

def add_trick():
    new_trick = {
        'id': st.session_state.next_id,
        'name': f'New Trick {st.session_state.next_id}',
        'active': True,
        'requirements': [],
        'show_requirements': False
    }
    st.session_state.tricks.append(new_trick)
    st.session_state.next_id += 1

def delete_trick(trick_id):
    st.session_state.tricks = [t for t in st.session_state.tricks if t['id'] != trick_id]

def add_requirement(trick):
    trick['requirements'].append([2, "identical"])

def delete_requirement(trick, index):
    trick['requirements'].pop(index)

def main():
    st.set_page_config(page_title="Trick Sets Manager Version 1.3", layout="wide")
    apply_custom_style()

    # Deck Configuration
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    st.markdown('<div class="container-header">Deck Configuration</div>', unsafe_allow_html=True)
    num_decks = st.number_input("Number of Decks:", min_value=1, value=6)
    st.markdown('</div>', unsafe_allow_html=True)

    # Tricksets
    st.markdown('<div class="custom-container">', unsafe_allow_html=True)
    st.markdown('<div class="container-header">Tricksets</div>', unsafe_allow_html=True)
    
    if st.button("Create New Trick Set"):
        add_trick()

    # Render each trick
    for trick in st.session_state.tricks:
        st.markdown('<div class="trick-container">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([3, 1, 0.5])
        
        with col1:
            trick['name'] = st.text_input("Set Name:", 
                                        value=trick['name'], 
                                        key=f"name_{trick['id']}")
        with col2:
            trick['active'] = st.checkbox("Active", 
                                        value=trick['active'], 
                                        key=f"active_{trick['id']}")
        with col3:
            if st.button("✕", key=f"delete_{trick['id']}"):
                delete_trick(trick['id'])
                st.experimental_rerun()

        # Requirements
        with st.expander("Show Requirements"):
            if st.button("Add Requirement(s)", key=f"add_req_{trick['id']}"):
                add_requirement(trick)
                
            for i, (count, req_type) in enumerate(trick['requirements']):
                col1, col2, col3 = st.columns([1, 2, 0.5])
                
                with col1:
                    trick['requirements'][i][0] = st.number_input(
                        "Count:", 
                        min_value=1, 
                        value=count,
                        key=f"count_{trick['id']}_{i}"
                    )
                with col2:
                    trick['requirements'][i][1] = st.selectbox(
                        "Type:",
                        ["identical", "any"],
                        index=0 if req_type == "identical" else 1,
                        key=f"type_{trick['id']}_{i}"
                    )
                with col3:
                    if st.button("✕", key=f"delete_req_{trick['id']}_{i}"):
                        delete_requirement(trick, i)
                        st.experimental_rerun()
                        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Calculate button
    if st.button("Calculate Number of Sets"):
        # Get active tricks with their requirements
        active_tricks = [trick for trick in st.session_state.tricks 
                        if trick['active']]
        
        results = "Individual Calculations:\n"
        results += "======================\n\n"
        
        for trick in active_tricks:
            if trick['requirements']:
                possible_sets, remaining_cards = calculate_sets(
                    num_decks, 
                    trick['requirements']
                )
                results += f"{trick['name']}:\n"
                results += f"Possible Sets: {possible_sets}\n"
                results += f"Remaining Cards: {remaining_cards}\n\n"
        
        # Optimal combination calculation
        results += "\nOptimal Combination of all Tricksets:\n"
        results += "==================================\n\n"
        
        combinations, total_remaining = calculate_max_combinations(
            num_decks, 
            active_tricks
        )
        
        if combinations:
            total_sets = 0
            total_cards_used = 0
            
            for trick_name, data in combinations.items():
                num_sets = data['sets']
                cards_used = data['cards_used']
                total_sets += num_sets
                total_cards_used += cards_used
                
                results += f"{trick_name}:\n"
                results += f"Sets: {num_sets}\n"
                results += f"Cards Used: {cards_used}\n"
                
                # Requirements with card value display
                results += "Requirements:\n"
                for count, req_type in data['requirements']:
                    if req_type == "identical":
                        results += f"- {count} identical cards (Example for one set:\n"
                        example_cards = list(range(min(count, 13)))
                        formatted_cards = CardMapping.format_cards_list(example_cards)
                        formatted_cards = formatted_cards.replace('\n', '\n  ')
                        results += f"  {formatted_cards})\n"
                    else:
                        results += f"- {count} any cards\n"
                results += "\n"
            
            # Summary
            results += "Summary:\n"
            results += "========\n"
            results += f"Total Number of Sets: {total_sets}\n"
            results += f"Total Cards Used: {total_cards_used}\n"
            results += f"Remaining Cards: {total_remaining}\n"
            
            if total_remaining > 0:
                results += "\nExamples of remaining cards:\n"
                example_remaining = list(range(min(13, total_remaining)))
                remaining_cards = CardMapping.format_cards_list(example_remaining)
                results += remaining_cards + "\n"
        else:
            results += "No possible combinations found."
            
        # Display results
        st.markdown('<div class="custom-container">', unsafe_allow_html=True)
        st.markdown('<div class="container-header">Possible Tricksets</div>', 
                   unsafe_allow_html=True)
        st.markdown(f'<pre class="results-area">{results}</pre>', 
                   unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
