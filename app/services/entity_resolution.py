import PyPDF2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz


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


def preprocess_text(text):
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    return pd.DataFrame(lines, columns=['text'])


def calculate_similarity(df):
    vectorizer = TfidfVectorizer().fit_transform(df['text'])
    vectors = vectorizer.toarray()
    similarity_matrix = cosine_similarity(vectors)
    return similarity_matrix


def entity_resolution(df, threshold=80):
    similar_pairs = []
    for i in range(len(df)):
        for j in range(i + 1, len(df)):
            similarity = fuzz.token_sort_ratio(df.iloc[i]['text'], df.iloc[j]['text'])
            if similarity >= threshold:
                similar_pairs.append((i, j, similarity))
    return similar_pairs


def find_entities(pdf_path, threshold=80):
    text = extract_text_from_pdf(pdf_path)
    df = preprocess_text(text)
    similarity_matrix = calculate_similarity(df)
    matches = entity_resolution(df, threshold)

    for (index1, index2, similarity) in matches:
        print(f"Similarity: {similarity}% between line {index1 + 1} and line {index2 + 1}:")
        print(f"Line {index1 + 1}: {df.iloc[index1]['text']}")
        print(f"Line {index2 + 1}: {df.iloc[index2]['text']}")
        print()


# pdf_path = 'C:\\Users\\novneet.patnaik\\Documents\\GitHub\\ML-OCR-DM\\app\\tmp\\CRO_Beginners_Guide.pdf'
# find_entities(pdf_path, threshold=80)
