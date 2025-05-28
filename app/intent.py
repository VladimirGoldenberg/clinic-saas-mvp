import os
import xml.etree.ElementTree as ET
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
import nltk

nltk.download('wordnet')
nltk.download('omw-1.4')

class SuperChatbot:
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.root = self.load_xml()
        self.steps, self.titles = self.extract_steps()
        self.tfidf_matrix, self.vectorizer = self.compute_tfidf()

    def load_xml(self):
        tree = ET.parse(self.xml_path)
        return tree.getroot()

    def clean_text(self, text):
        if text is None:
            return ""
        text = re.sub(r'<.*?>', '', text)
        text = re.sub(r'&\w+;', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def expand_query_with_synonyms(self, query):
        synonyms = set()
        for word in query.split():
            for syn in wordnet.synsets(word):
                for lemma in syn.lemmas():
                    synonyms.add(lemma.name().replace('_', ' '))
        return query + ' ' + ' '.join(synonyms)

    def extract_steps(self):
        extracted_steps = []
        titles = []
        unique_steps = set()

        for storyboard in self.root.findall(".//storyboard"):
            title = storyboard.get("title", "Unknown Title")
            type_attr = storyboard.get("type", "")

            if "command sequencer" in type_attr.lower():
                steps = []
                for ce in storyboard.findall(".//ce"):
                    step_text = ce.find("stringProp[@name='text']")
                    if step_text is not None:
                        cleaned_text = self.clean_text(step_text.text)
                        if cleaned_text and cleaned_text not in unique_steps:
                            steps.append(f"- {cleaned_text}")
                            unique_steps.add(cleaned_text)

                if steps:
                    extracted_steps.append("\n".join(steps))
                    titles.append(title)

        return extracted_steps, titles

    def compute_tfidf(self):
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(self.steps)
        return tfidf_matrix, vectorizer

    def answer_question(self, query):
        expanded_query = self.expand_query_with_synonyms(query)
        query_vector = self.vectorizer.transform([expanded_query])
        similarity_scores = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
        best_match_idx = similarity_scores.argmax()

        if similarity_scores[best_match_idx] > 0.01:
            return f"**{self.titles[best_match_idx]}**\n{self.steps[best_match_idx]}"
        else:
            return "I couldn't find relevant information on that. Please refine your question."
