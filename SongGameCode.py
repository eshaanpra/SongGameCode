import musicbrainzngs
import re

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

def main():
    print("Welcome to the Song Chain Game!")
    print("Rules: Each player must name a song and its artist. The song must start with the last letter of the previous song's name, and songs cannot be repeated.")

    players = ["Player 1", "Player 2"]
    current_player_index = 0
    previous_song = None
    used_songs = set()

    while True:
        current_player = players[current_player_index]
        print(f"{current_player}'s turn!")

        invalid_attempt = False

        while True:
            if invalid_attempt:
                print("Please try again.")

            song_name = input(f"{current_player}, enter the song name: ").strip()
            artist_name = input(f"{current_player}, enter the artist's name: ").strip()

            song_name = convert_song_name(song_name)
            
            if artist_name == "":
                print("Please enter an artist.")
                invalid_attempt = True
                continue
            if previous_song:
                expected_start_letter = get_last_letter(previous_song)
                if not song_name.lower().startswith(expected_start_letter):
                    print(f"The song must start with the letter '{expected_start_letter}'.")
                    invalid_attempt = True
                    continue

            if song_name.lower() in used_songs:
                print("This song has already been used. Please choose a different song.")
                invalid_attempt = True
                continue

            if not validate_song(song_name, artist_name):
                print("The specific song and artist combination could not be verified.")
                invalid_attempt = True
                continue

            invalid_attempt = False
            break

        print(f"Valid move! {song_name} by {artist_name}")
        previous_song = song_name
        used_songs.add(song_name.lower())

        # Switch to the next player
        current_player_index = 1 - current_player_index

if __name__ == "__main__":
    main()
