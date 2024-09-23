import re
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextLine, LTChar
from collections import defaultdict, Counter
import string

search_words = ['nausea', 'headache']
starting_page = 1
context_window = 5  # Adjust this for more or less context around the found word
frequency_threshold = 50  # Reduce noise by filtering out very frequent words
pdf_files = ["Homoeopathy Pakistan.pdf"]

# Helper function to identify capitalized words and group consecutive capitalized words
def is_capitalized(word):
    return word and word[0].isupper()  # Check if the word is not empty before accessing the first character

# Remove unwanted words or common noise that are still capitalized
common_noise = {
    "The", "Of", "In", "To", "A", "And", "Is", "On", "For", "With", "By", "At", 
    "An", "This", "That", "It", "He", "She", "They", "Them", "You", "We", "Not", 
    "If", "As", "His", "Her", "But", "So", "Are", "Be", "Or", "Was", "Were", 
    "Will", "Can", "Had", "Has", "Have", "There", "Which", "Such", "Who", 
    "Whom", "Some", "More", "Any", "From", "About", "Into", "Through","While","Digestion","Despite","Women","Local","Along","After","Severe","Dizziness","Nausea","Later","Young","Malaria","Sometimes","Vomiting","Provided","Then","However","Food","During"
}

# Function to count word frequencies throughout the PDF
def count_word_frequencies(file_path):
    word_counter = Counter()
    
    for page_layout in extract_pages(file_path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        current_word = ""
                        for char in text_line:
                            if isinstance(char, LTChar):
                                word = char.get_text().strip()
                                # Count capitalized words longer than 3 letters
                                if len(word) > 3 and word.isalpha() and is_capitalized(word):
                                    word_counter[word] += 1
    return word_counter

# Function to search for symptoms and extract nearby potential medicine names
def search_and_extract_medicine(file_path, word_frequencies):
    found_words = {word: [] for word in search_words}
    medicines_found = {word: set() for word in search_words}

    for page_layout in extract_pages(file_path):
        page_num = page_layout.pageid

        if page_num >= starting_page:
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    words = []
                    for text_line in element:
                        if isinstance(text_line, LTTextLine):
                            current_word = ""
                            for char in text_line:
                                if isinstance(char, LTChar):
                                    if char.get_text().isspace():
                                        if current_word:
                                            words.append(current_word)
                                            current_word = ""
                                    else:
                                        current_word += char.get_text()

                            if current_word:
                                words.append(current_word)

                    # Join words and split them into lowercase form for keyword matching
                    text = ' '.join(words).strip()
                    lower_words = text.lower().split()

                    for word in search_words:
                        lower_word = word.lower()

                        if lower_word in lower_words:
                            found_words[word].append(page_num)

                            word_index = lower_words.index(lower_word)
                            start = max(0, word_index - context_window)
                            end = min(len(words), word_index + context_window + 1)

                            # Extract potential medicines: group consecutive capitalized words
                            potential_medicine = ""
                            for i in range(start, end):
                                nearby_word = words[i].strip(string.punctuation).strip()

                                # Ensure the word is not empty before processing
                                if nearby_word and is_capitalized(nearby_word) and len(nearby_word) > 3 and word_frequencies[nearby_word] <= frequency_threshold and nearby_word not in common_noise:
                                    if potential_medicine:
                                        potential_medicine += " " + nearby_word
                                    else:
                                        potential_medicine = nearby_word
                                else:
                                    if potential_medicine:
                                        medicines_found[word].add(potential_medicine)
                                        potential_medicine = ""

                            if potential_medicine:
                                medicines_found[word].add(potential_medicine)

    return found_words, medicines_found

# Main execution logic
for pdf_file in pdf_files:
    print(f"Scanning {pdf_file} to count word frequencies...")
    word_frequencies = count_word_frequencies(pdf_file)

    print(f"Searching in file: {pdf_file}")
    results, medicines = search_and_extract_medicine(pdf_file, word_frequencies)
    
    for word, pages in results.items():
        if pages:
            pages_str = ', '.join(map(str, pages))
            print(f"String '{word}' is found in the PDF file on pages: {pages_str}")
            if medicines[word]:
                medicines_str = ', '.join(medicines[word])
                print(f"Possible medicines for '{word}' found: {medicines_str}")
            else:
                print(f"No specific medicines found for '{word}' in the nearby text.")
        else:
            print(f"String '{word}' not found.")
    
    print("\n" + "-"*50 + "\n")
