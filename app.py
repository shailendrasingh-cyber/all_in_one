import streamlit as st
import fitz  # PyMuPDF
from googletrans import Translator
import os
from io import BytesIO

# Function to download TXT file
def download_txt(content):
    txt_file = BytesIO()
    txt_file.write(content.encode('utf-8'))
    txt_file.seek(0)
    st.download_button(label="Download TXT", data=txt_file, file_name="translated_content.txt", mime="text/plain")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text()
        return text
    except Exception as e:
        st.exception(f"Error extracting text from PDF: {e}")
        return None

# Function to translate text using Google Translate
def translate_text(text):
    try:
        translator = Translator()
        translated_result = translator.translate(text, dest='hi')
        if translated_result.text:
            return translated_result.text
        else:
            return "Translation not available"
    except Exception as e:
        st.exception(f"Error translating text: {e}")
        return None

# Function to load the corpus for Hindi spell checking
def load_corpus():
    with open('hindi_corpus.txt', encoding='utf-8') as file:
        corpus = [word.strip() for word in file]
    return corpus

# Function to calculate Levenshtein Distance
def levenshtein_distance(s, t):
    rows = len(s) + 1
    cols = len(t) + 1
    dist = [[0 for x in range(cols)] for x in range(rows)]

    for i in range(1, rows):
        dist[i][0] = i

    for i in range(1, cols):
        dist[0][i] = i
        
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0
            else:
                cost = 1
            dist[row][col] = min(dist[row - 1][col] + 1,      # deletion
                                  dist[row][col - 1] + 1,      # insertion
                                  dist[row - 1][col - 1] + cost) # substitution

    return dist[row][col]

# Function to get correct word for Hindi spell checking
def get_correct_word(word, corpus):
    min_dis = 100
    correct_word = ""
    for s in corpus:
        cur_dis = levenshtein_distance(s, word)
        if min_dis > cur_dis:
            min_dis = cur_dis
            correct_word = s
    return correct_word

# Function to process input text for Hindi spell checking
def process_input_text(input_text, corpus):
    corrected_text = []
    lines = input_text.split('\n')
    for line_num, line in enumerate(lines, start=1):
        words = line.strip().split()
        corrected_line = []
        for word_num, word in enumerate(words, start=1):
            if word not in corpus:
                corrected = get_correct_word(word, corpus)
                corrected_line.append(f"At Line: {line_num} Word No. {word_num}: {word} -> {corrected}")
            else:
                corrected_line.append(word)
        corrected_text.append(' '.join(corrected_line))
    return '\n'.join(corrected_text)

# Main Streamlit app
def main():

    st.markdown(
        """
        <style>
        .reportview-container {
            background-color: #f0f0f0; /* Grey color */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.title('PDF Translator & Hindi Spell Checker')
    
    # Home page with instructions
    st.markdown("""
        ## Welcome to PDF Translator & Hindi Spell Checker App
        
        This app allows you to translate PDF files from English to Hindi and perform Hindi spell checking on text files.
        
        To get started, choose an option from the sidebar on the left.
    
        This is  a full-featured translation or OCR applicationS
    """)

    # Sidebar options
    option = st.sidebar.selectbox(
        "Select Tool:",
        ("Home", "PDF Translator (English to Hindi)", "Hindi Spell Checker")
    )

    if option == "Home":
        pass  # Home page is already displayed
    elif option == "PDF Translator (English to Hindi)":
        st.subheader("English to Hindi Translator")

        # File upload for PDF translation
        uploaded_file = st.file_uploader("Upload a PDF", type=['pdf'])
        if uploaded_file is not None:
            upload_folder = 'uploads'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            pdf_content = extract_text_from_pdf(file_path)

            if pdf_content is None:
                st.error('Error extracting text from PDF')
            else:
                translated_content = translate_text(pdf_content)

                if translated_content is None:
                    st.error('Error translating text')
                else:
                    # Display translated content
                    st.text_area("Translated Content", translated_content, height=400)

                    # Download button for TXT
                    st.markdown("---")
                    st.subheader("Download Translated Content")
                    download_btn_txt = st.button("Download as TXT")

                    if download_btn_txt:
                        download_txt(translated_content)

            os.remove(file_path)
    elif option == "Hindi Spell Checker":
        st.subheader("Hindi Spell Checker")

        # Upload input text file for spell checking
        uploaded_file = st.file_uploader("Upload a text file", type=['txt'])
        if uploaded_file is not None:
            input_text = uploaded_file.getvalue().decode("utf-8")
            
            # Load corpus for spell checking
            corpus = load_corpus()

            # Process input text
            corrected_text = process_input_text(input_text, corpus)

            # Display corrected text
            st.text_area("Corrected Text", value=corrected_text, height=300)

            # Offer download option for corrected text
            st.subheader("Download Corrected Text")
            st.download_button(
                label="Download Corrected Text",
                data=corrected_text.encode('utf-8'),
                file_name="corrected_text.txt",
                mime="text/plain"
            )
            st.info("Please wait while the Hindi spell checker is processing. Note: This tool may not be 100% accurate but has good accuracy.")

if __name__ == "__main__":
    main()
