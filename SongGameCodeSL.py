import musicbrainzngs
import re
import streamlit as st

# Initialize session state variables if they don't exist
if 'current_player_index' not in st.session_state:
    st.session_state.current_player_index = 0
if 'previous_song' not in st.session_state:
    st.session_state.previous_song = None
if 'used_songs' not in st.session_state:
    st.session_state.used_songs = set()
if 'game_messages' not in st.session_state:
    st.session_state.game_messages = []

# Set up the MusicBrainz API
musicbrainzngs.set_useragent("SongChainGame", "0.1", "eshaan.prashanth@gmail.com")


def rp(text):
    """Remove punctuation from a given text."""
    return re.sub(r'[^\w\s]', '', text)  # Removes anything that's not a letter, number, or whitespace


def convert_to_words(num):  
    if num == 0:  
        return "zero"  
    ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]  
    tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]  
    teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"]  
    words = ""  
    if num>= 1000:  
        words += ones[num // 1000] + " thousand "  
        num %= 1000  
    if num>= 100:  
        words += ones[num // 100] + " hundred "  
        num %= 100  
    if num>= 10 and num<= 19:  
        words += teens[num - 10] + " "  
        num = 0  
    elif num >= 20:  
        words += tens[num // 10] + " "  
        num %= 10  
    if num>= 1 and num<= 9:  
        words += ones[num] + " "  
    return words.strip() 

def convert_song_name(song_name):
    words = song_name.split()  # Split the song name into words
    converted_song_name = []

    for word in words:
        if word.isdigit():  # If the word is a number
            num = int(word)
            converted_song_name.append(convert_to_words(num))  # Convert the number to words
        else:
            converted_song_name.append(word)  # Keep the word as is if it's not a number

    # Join the words back into a sentence and apply rp to remove any non-letter characters
    final_song_name = " ".join(converted_song_name)
    return rp(final_song_name)  # Apply rp to ensure only letters and spaces
def validate_song(song_name, artist_name):
    try:
        results = musicbrainzngs.search_recordings(query=song_name.lower(), artist=artist_name.lower(), limit=1000000000000000)
        for recording in results['recording-list']:
            if recording['title'].lower() == song_name.lower():
                return True
            if rp(song_name.lower()) == rp(recording['title'].lower()):
                return True
        return False
    except Exception as e:
        print(f"Error during MusicBrainz API lookup: {e}")
        return False

def get_last_letter(word):
    word = word.strip().lower()  # Strip any extra spaces and convert to lowercase
    if word[-1].isdigit():
        numtowords = convert_to_words(int(word[-1]))
        return numtowords[-1]  # Return last character of word after conversion
    elif word.isnumeric():  # Handle entire numeric words like "21"
        wordnonum = convert_to_words(int(word))
        return wordnonum.strip().lower()[-1]  # Return last character of word after conversion
    else:
        return word[-1]  # Return the last letter if it's not numeric

st.title('Song Chain Game')
st.write("Rules: Each player must name a song and its artist. The song must start with the last letter of the previous song's name, and songs cannot be repeated.")

# Game interface
players = ["Player 1", "Player 2"]
current_player = players[st.session_state.current_player_index]

# Display game history
if st.session_state.game_messages:
    st.write("Game History:")
    for message in st.session_state.game_messages:
        st.write(message)

# Display current player's turn
st.subheader(f"{current_player}'s turn!")

# Show the required starting letter if there's a previous song
if st.session_state.previous_song:
    expected_start_letter = get_last_letter(st.session_state.previous_song)
    st.write(f"Your song must start with the letter '{expected_start_letter}'")

# Input fields
col1, col2 = st.columns(2)
with col1:
    song_name = st.text_input("Enter the song name:", key=f"song_input_{st.session_state.current_player_index}")
with col2:
    artist_name = st.text_input("Enter the artist's name:", key=f"artist_input_{st.session_state.current_player_index}")

# Submit button
if st.button("Submit Turn"):
    if song_name and artist_name:
        song_name = convert_song_name(song_name)
        
        # Validate the move
        valid_move = True
        error_message = None
        
        if st.session_state.previous_song:
            expected_start_letter = get_last_letter(st.session_state.previous_song)
            if not song_name.lower().startswith(expected_start_letter):
                valid_move = False
                error_message = f"The song must start with the letter '{expected_start_letter}'"

        if song_name.lower() in st.session_state.used_songs:
            valid_move = False
            error_message = "This song has already been used. Please choose a different song."

        if not validate_song(song_name, artist_name):
            valid_move = False
            error_message = "The specific song and artist combination could not be verified."

        if valid_move:
            # Update game state
            st.session_state.previous_song = song_name
            st.session_state.used_songs.add(song_name.lower())
            st.session_state.game_messages.append(f"{current_player}: {song_name} by {artist_name}")
            st.session_state.current_player_index = 1 - st.session_state.current_player_index
            st.success(f"Valid move! {song_name} by {artist_name}")
            st.rerun()
        else:
            st.error(error_message)
    else:
        st.error("Please enter both song name and artist name.")

# Reset button
if st.button("Reset Game"):
    st.session_state.current_player_index = 0
    st.session_state.previous_song = None
    st.session_state.used_songs = set()
    st.session_state.game_messages = []
    st.rerun()
