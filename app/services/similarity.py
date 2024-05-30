import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = len(reader.pages)
        text = ""
        for page_num in range(num_pages):
            page_text = reader.pages[page_num].extract_text()
            # page = reader.getPage(page_num)
            text += page_text + "\n"
    return text


def split_text_into_lines(text):
    lines = text.split('\n')
    return [line.strip() for line in lines if line.strip()]


def calculate_similarity(lines):
    vectorizer = TfidfVectorizer().fit_transform(lines)
    vectors = vectorizer.toarray()
    cosine_matrix = cosine_similarity(vectors)
    return cosine_matrix


def find_similar_lines(cosine_matrix, lines, threshold=0.8):
    similar_lines = []
    for i in range(len(cosine_matrix)):
        for j in range(i + 1, len(cosine_matrix)):
            if cosine_matrix[i][j] >= threshold:
                similar_lines.append((i+1, lines[i], j+1, lines[j], cosine_matrix[i][j]))
    return similar_lines


def get_similarity(pdf_path, threshold=0.8):
    text = extract_text_from_pdf(pdf_path)
    lines = split_text_into_lines(text)
    cosine_matrix = calculate_similarity(lines)
    similar_lines = find_similar_lines(cosine_matrix, lines, threshold)

    similarity_matrix = []
    for line_num1, line1, line_num2,  line2, similarity in similar_lines:
        similarity_matrix.append({"Line " + str(line_num1): line1, "Line " + str(line_num2) : line2, "Similarity": similarity})
    if not similarity_matrix:
        return "No similarity found"
    return similarity_matrix


# pdf_path = 'C:\\Users\\novneet.patnaik\\Documents\\GitHub\\ML-OCR-DM\\app\\tmp\\CRO_Beginners_Guide.pdf'
# get_similarity(pdf_path, threshold=0.8)

# if _name_ == "_main_":
#     pdf_path = 'path_to_your_pdf.pdf'
#