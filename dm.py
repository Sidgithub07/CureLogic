import PyPDF2

search_words = ['Health', 'Homeopathy', 'Medicine', 'Expert system', 'Treatment', 'article','Repertorization','Homeopathic']

starting_page = 1

pdf_files =['Homoeopathy Pakistan.pdf']


def search_in_pdf(file_path):
    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        
        found_words = {word: [] for word in search_words} 
        
        for page_num in range(starting_page - 1, len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            
            for word in search_words:
                if word in text:
                    found_words[word].append(page_num + 1)  # Append the page number (1-indexed)
        
        return found_words


for pdf_file in pdf_files:
    print(f"Searching in file: {pdf_file}")
    results = search_in_pdf(pdf_file)
    
    for word, pages in results.items():
        if pages:
            pages_str = ', '.join(map(str, pages))
            print(f"String '{word}' Is Found In The PDF File on pages: {pages_str}")
        else:
            print(f"String '{word}' Not Found")
    print("\n" + "-"*50 + "\n")