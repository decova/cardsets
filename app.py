###############################################
# PART 1 - Basic set-up and Classes
###############################################

import streamlit as st
import json
import os
from collections import defaultdict

# Constants
TRICKS_FILE = "saved_tricks.json"

def apply_custom_style():
    """
    Applies custom CSS styling to the Streamlit app.
    This includes styling for the main container, input fields, buttons, and results display.
    """
    st.markdown("""
        <style>
        /* Main app container styling */
        .stApp {
            white-space: pre-wrap !important;
            max-width: 760px;
            height: 1000px;
            margin: auto;
            padding: 20px 0;
            border: 2px solid #d5d5d5;
            border-radius: 10px;
        }

        /* Custom container for sections */
        .custom-container {
            display: block;
            border: 3px solid #ccc;
            border-radius: 4px;
            padding: 1rem;
            margin-bottom: 1rem;
            background-color: white;
        }

        /* Remove padding from block container */
        .block-container {
            padding-top: 0;
            padding-bottom: 0;
        }

        /* Hide empty divs */
        div:empty {
            display: none;
        }

        /* Header styling */
        .container-header {
            font-size: 1.2rem;
            font-weight: bold;
            margin-bottom: 1rem;
            color: #333;
            text-align: center;
        }

        /* Column padding fix */
        [data-testid="column"] > div {
            padding: 0 !important;
            padding-top: 25px !important;
        }

        /* First column (text input) needs no top padding */
        [data-testid="column"]:first-child > div {
            padding-top: 0 !important;
        }

        /* Input field styling */
        .stTextInput > div > div > input {
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 0.5rem;
            width: 400px !important;
        }

        /* Numbers input styling */
        input[type=number] {
            width: 60px !important;
            text-align: center !important;
        }

        /* Remove arrows from number inputs */
        input[type=number]::-webkit-inner-spin-button, 
        input[type=number]::-webkit-outer-spin-button { 
            -webkit-appearance: none; 
            margin: 0; 
        }

        /* Checkbox styling */
        .stCheckbox {
            margin: 0 !important;
        }

        /* Button styling */
        .stButton > button {
            width: 100%;
            border: 1px solid #ccc;
            background-color: #f8f9fa;
            color: #333;
            padding: 0.5rem;
            margin: 0 !important;
        }

        .stButton > button:hover {
            background-color: #e9ecef;
        }

        /* Trick container styling */
        .trick-container {
            border: 1px solid #ddd;
            border-radius: 2px;
            padding: 0.8rem;
            margin: 0.5rem 0;
            background-color: white;
        }

        /* Requirements container styling */
        .requirements-container {
            margin-left: 1rem;
            padding: 0.5rem;
            border-left: 2px solid #eee;
        }

        /* Delete button styling */
        .delete-button {
            color: red;
            cursor: pointer;
            float: right;
        }


        /* Expander header styling */
        .streamlit-expanderHeader {
            font-size: 1rem;
            color: #333;
        }

        activate button
        .stCheckBox {
        display:block;
        margin: 30px 0 0 0!important;
        }

        .stElementContainer {
        font-size:21px;
        }




        </style>

    """, unsafe_allow_html=True)

class CardMapping:
    """
    Handles card mapping and formatting operations.
    Converts between card numbers (0-51) and their string representations.
    """
    SUITS = ['♥', '♣', '♦', '♠']
    VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    
    @staticmethod
    def number_to_card(number):
        """
        Converts a card number (0-51) to its string representation.
        Example: 0 -> '♥A', 13 -> '♣A'
        """
        if not 0 <= number <= 51:
            raise ValueError(f"Invalid card number: {number}")
        suit_index = number // 13
        value_index = number % 13
        return f"{CardMapping.SUITS[suit_index]}{CardMapping.VALUES[value_index]}"
    
    @staticmethod
    def format_cards_list(numbers):
        """
        Formats a list of card numbers into a readable string representation.
        Now only showing symbols without suit names.
        """
        if not numbers:
            return "No cards"
        cards = [CardMapping.number_to_card(n) for n in numbers]
        return ", ".join(cards)
    
    @staticmethod
    def get_suit_name(number):
        """
        Returns the suit name for a given card number.
        Example: 0-12 -> 'Hearts', 13-25 -> 'Clubs'
        """
        suits_names = ['Hearts', 'Clubs', 'Diamonds', 'Spades']
        return suits_names[number // 13]


###############################################
# PART 2 - Logical Functions
###############################################

def save_tricks():
    """
    Saves the current state of tricks and next_id to a JSON file.
    Includes error handling for file operations.
    """
    tricks_data = {
        'tricks': st.session_state.tricks,
        'next_id': st.session_state.next_id
    }
    try:
        with open(TRICKS_FILE, 'w') as f:
            json.dump(tricks_data, f)
    except Exception as e:
        st.error(f"Error saving tricks: {str(e)}")

def load_tricks():
    """
    Loads previously saved tricks and next_id from JSON file.
    Includes error handling for file operations.
    """
    try:
        if os.path.exists(TRICKS_FILE):
            with open(TRICKS_FILE, 'r') as f:
                data = json.load(f)
                st.session_state.tricks = data['tricks']
                st.session_state.next_id = data['next_id']
    except Exception as e:
        st.error(f"Error loading tricks: {str(e)}")
        st.session_state.tricks = []
        st.session_state.next_id = 0

def format_results(combinations, total_remaining):
    """
    Formats the calculation results into a readable string representation.
    
    Args:
        combinations (dict): Dictionary containing trick combinations and their details
        total_remaining (int): Number of remaining cards
        
    Returns:
        str: Formatted string containing all results
    """
    results = []
    
    if combinations:
        total_sets = 0
        total_cards_used = 0
        
        # Header for individual calculations
        results.append("INDIVIDUAL CALCULATIONS\n")
        
        # Process each trick combination
        for trick_name, data in combinations.items():
            num_sets = data['sets']
            cards_used = data['cards_used']
            total_sets += num_sets
            total_cards_used += cards_used
            
            results.append(f"<strong>{trick_name}</strong>\n")
            results.append(f"Possible Sets: {num_sets}\n")
            results.append(f"Cards Used: {cards_used}\n")
            results.append("Requirements (example cards):\n")
            
            # Add requirement details
            for count, req_type in data['requirements']:
                if req_type == "identical":
                    results.append(f"{count} identical cards\n")
                    example_cards = list(range(min(count, 13)))
                    formatted_cards = CardMapping.format_cards_list(example_cards)
                    results.append(f"{formatted_cards}\n")
            results.append("\n")
        
        # Add summary section
        results.append("\nSUMMARY\n")
        results.append(f"Total Number of Sets: {total_sets}\n")
        results.append(f"Total Cards Used: {total_cards_used}\n")
        results.append(f"Remaining Cards: {total_remaining}\n")
        
        # Add remaining cards examples if any
        if total_remaining > 0:
            results.append("\nExample remaining cards:\n")
            example_remaining = list(range(min(13, total_remaining)))
            remaining_cards = CardMapping.format_cards_list(example_remaining)
            results.append(f"{remaining_cards}\n")
    else:
        results.append("No possible combinations found.\n")
        
    return "".join(results)

def calculate_sets(num_decks, requirements):
    """
    Calculates the possible number of sets and remaining cards for a single trick.
    
    Args:
        num_decks (int): Number of card decks available
        requirements (list): List of requirement tuples (count, type)
        
    Returns:
        tuple: (possible_sets, remaining_cards)
    """
    if not requirements:
        return 0, num_decks * 52

    # Check if we have enough decks for the maximum requirement
    max_cards_needed = max(count for count, req_type in requirements if req_type == "identical")
    if max_cards_needed > num_decks:
        return 0, num_decks * 52

    total_cards = num_decks * 52
    identical_reqs = []
    any_reqs = []
    
    # Separate requirements by type
    for count, req_type in requirements:
        if req_type == "identical":
            identical_reqs.append(count)
        else:
            any_reqs.append(count)

    # Special handling for pairs
    if len(identical_reqs) == 2 and identical_reqs[0] == identical_reqs[1]:
        cards_needed = identical_reqs[0]
        sets_per_number = num_decks // cards_needed
        number_pairs = 52 // 2
        possible_sets = sets_per_number * number_pairs
    else:
        possible_sets = total_cards // sum(identical_reqs) if identical_reqs else 0

    # Calculate used and remaining cards
    cards_per_set = sum(identical_reqs)
    used_cards = possible_sets * cards_per_set
    remaining_cards = total_cards - used_cards

    return int(possible_sets), remaining_cards

def calculate_max_combinations(num_decks, tricks_data):
    """
    Calculates the maximum possible combinations of tricks that can be performed
    with the given number of decks.
    
    Args:
        num_decks (int): Number of card decks available
        tricks_data (list): List of trick dictionaries containing requirements
        
    Returns:
        tuple: (combinations_dict, remaining_cards)
    """
    total_cards = num_decks * 52
    combinations = {}
    
    # Collect information about valid tricks
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
        
    # Calculate initial distribution
    available_cards = total_cards
    num_tricks = len(tricks_info)
    cards_per_trick = available_cards // num_tricks
    
    # Calculate target sets for each trick
    target_sets = []
    for trick in tricks_info:
        possible_sets = min(
            cards_per_trick // trick['cards_per_set'],
            trick['max_sets']
        )
        target_sets.append(possible_sets)
    
    # Use minimum target to ensure fairness
    min_target = min(target_sets)
    
    # Initial allocation
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
    
    # Distribute remaining cards
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


###############################################
# PART 3 - UI-components and main functions
###############################################

def add_trick():
    """
    Adds a new trick to the session state and saves it.
    Initializes with default values and increments the next_id counter.
    """
    new_trick = {
        'id': st.session_state.next_id,
        'name': f'New Trick {st.session_state.next_id}',
        'active': True,
        'requirements': [],
        'show_requirements': False
    }
    st.session_state.tricks.append(new_trick)
    st.session_state.next_id += 1
    save_tricks()

def delete_trick(trick_id):
    """
    Removes a trick from the session state by its ID and saves the updated state.
    
    Args:
        trick_id (int): ID of the trick to delete
    """
    st.session_state.tricks = [t for t in st.session_state.tricks if t['id'] != trick_id]
    save_tricks()
    st.rerun()  # Changed from st.experimental_rerun()

def add_requirement(trick):
    """
    Adds a new requirement to a trick with default values and saves the state.
    
    Args:
        trick (dict): The trick dictionary to add the requirement to
    """
    trick['requirements'].append([2, "identical"])
    save_tricks()

def delete_requirement(trick, index):
    """
    Removes a requirement from a trick at the specified index and saves the state.
    
    Args:
        trick (dict): The trick dictionary to remove the requirement from
        index (int): Index of the requirement to remove
    """
    trick['requirements'].pop(index)
    save_tricks()
    st.rerun()  # Added rerun here too for consistency

def main():
    """
    Main function that sets up and runs the Streamlit application.
    Handles the UI layout and interaction logic.
    """
    # Initialize app configuration
    st.set_page_config(page_title="Trick Sets Manager Version 1.3", layout="wide")
    apply_custom_style()
    
    # Initialize or load saved state
    if 'tricks' not in st.session_state:
        st.session_state.tricks = []
        st.session_state.next_id = 0
        load_tricks()

    # Deck Configuration Section
    st.markdown('<div class="container-header">Deck Configuration</div>', unsafe_allow_html=True)
    num_decks = st.number_input("Number of Decks:", min_value=1, value=6)

    # Tricksets Section
    st.markdown('<div class="container-header">Tricksets</div>', unsafe_allow_html=True)
    
    if st.button("Create New Trick Set"):
        add_trick()

    # Render each trick
    for trick in st.session_state.tricks:
        st.markdown('<div class="trick-container">', unsafe_allow_html=True)
        
        # Layout trick header with three columns
        col1, col2, col3 = st.columns([6, 2, 1])
        
        with col1:
            trick['name'] = st.text_input("Set Name:", 
                                        value=trick['name'], 
                                        key=f"name_{trick['id']}")
        with col2:
            st.markdown('<div style="height: 65px"></div>', unsafe_allow_html=True)  # 25px Verschiebung nach unten
            trick['active'] = st.checkbox("Active", 
                                        value=trick['active'],
                                        key=f"active_{trick['id']}")
        with col3:
            st.markdown('<div style="height: 65px"></div>', unsafe_allow_html=True)  # 25px Verschiebung nach unten
            if st.button("✕", key=f"delete_{trick['id']}"):
                delete_trick(trick['id'])

        # Requirements section
        with st.expander("Show Requirements"):
            if st.button("Add Requirement(s)", key=f"add_req_{trick['id']}"):
                add_requirement(trick)
                
            # Render each requirement
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
                        
        st.markdown('</div>', unsafe_allow_html=True)

    # Calculate Button and Results Section
    if st.button("Calculate Number of Sets"):
        active_tricks = [trick for trick in st.session_state.tricks 
                        if trick['active']]
        
        # Individual calculations
        results = []
        results.append("INDIVIDUAL CALCULATIONS\n")
        
        for trick in active_tricks:
            if trick['requirements']:
                possible_sets, remaining_cards = calculate_sets(
                    num_decks, 
                    trick['requirements']
                )
                results.append(f"{trick['name']}:\n")
                results.append(f"Possible Sets: {possible_sets}\n")
                results.append(f"Remaining Cards: {remaining_cards}\n")
        
        # Optimal combination calculation
        results.append("\nOPTIMAL COMBINATION OF ALL TRICKSETS\n")
        
        combinations, total_remaining = calculate_max_combinations(
            num_decks, 
            active_tricks
        )
        
        # Format and display results
        result_text = format_results(combinations, total_remaining)
        
        st.markdown('<div class="container-header">Possible Tricksets</div>', 
                   unsafe_allow_html=True)
        st.markdown(f'<pre class="results-area">{result_text}</pre>', 
                   unsafe_allow_html=True)

if __name__ == "__main__":
    main()
