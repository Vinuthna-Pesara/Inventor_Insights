from flask import Flask, render_template, request, jsonify
import nltk
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('punkt')
import requests
import re
from bs4 import BeautifulSoup
import string
from time import sleep
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

class ChatBot():
    def __init__(self):
        self.reset()
    def reset(self):
        self.end_chat = False
        self.got_topic = False
        self.title = None
        self.text_data = []
        self.sentences = []
        self.para_indices = []
        self.current_sent_idx = None
        self.punctuation_dict = str.maketrans({p: None for p in string.punctuation})
        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.key_info = {}
        self.photo_url = None
        self.api_key_info={}



    def chat(self, text):
        if self.end_chat:
            print('ChatBot >>  See you soon! Bye!')
            self.reset()
        while not self.end_chat:
            if text.lower().strip() in ['bye', 'quit', 'exit']:
                self.end_chat = True
                return 'See you soon! Bye!'
            elif text.lower().strip() in ['hello', 'hi', 'hey']:
                return "Hello! Ask your question."
            elif text.lower().strip() in ['thank you', 'thanks']:
                return "You're welcome! If you have any more questions, feel free to ask!"
            elif text.lower().strip() == 'more':
                if self.current_sent_idx is not None:
                    return self.text_data[self.para_indices[self.current_sent_idx]]
                else:
                    return "Please input your query first!"
            elif not self.got_topic:
                return self.fetch_wikipedia_info(text),self.scrape_wiki(text)
            else:
                if self.handle_keywords(text):
                    return self.handle_keywords(text)
                self.sentences.append(text)
                return self.respond()
        else:
            # Use scrape_wiki for processing data like querying, generating detailed responses, etc.
            processed_info = self.scrape_wiki(text)
            return processed_info

    def fetch_wikipedia_info(self, name):
        """Fetches information about a person from Wikipedia."""
        self.name = name.strip()
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{name.replace(' ', '_')}"

        try:
            response = requests.get(url)
            if response.status_code != 200:
                self.reset()
                return "Could not fetch information. Please check the name or try another person."

            data = response.json()
            summary = data.get('extract', "No summary available.")
            self.photo_url = data.get('thumbnail', {}).get('source', None)

            # Check if the person is an inventor
            if not any(keyword in summary.lower() for keyword in ["inventor", "invention", "discovery", "scientist"]):
                # If not an inventor, try to fetch their profession from the summary
                profession = self.extract_profession(summary)
                person_name = self.name if self.name else "The person specified"
                self.reset()
                return f"The information fetched suggests that {person_name} is not an inventor. They are a {profession}. Please try another name if you were looking for an inventor."

            # Extract key information
            self.api_key_info['summary'] = summary

            self.got_topic = True
            return {
                'summary': f"About {self.name}: {self.api_key_info['summary']}",
                'image_url': self.photo_url
            }

        except Exception as e:
            self.reset()
            return f"An error occurred: {e}"

    def extract_profession(self, summary):
        """Extracts the profession from the summary."""
        professions = [
            "actor", "cricketer", "actress", "author", "singer", "director", "scientist",
            "engineer", "politician", "entrepreneur", "teacher", "doctor",
            "musician", "philosopher", "inventor", "artist", "writer", "comedian"
        ]

        for profession in professions:
            if profession in summary.lower():
                return profession.capitalize()

        return "professional"
    def extract_key_info(self, soup):
        def extract_info(header_text, key):
            info = []
            header = soup.find('th', string=re.compile(header_text, re.IGNORECASE))
            if header:
                data = header.find_next('td')
                if data:
                    items = data.find_all('li')
                    if items:
                        info = [item.get_text(strip=True) for item in items]
                    else:
                        info = [data.get_text(strip=True)]
            return info

        # Extracting key details like Born, Awards, Known for
        self.key_info['known_for'] = extract_info("Known for", 'known_for')
        self.key_info['awards'] = extract_info("Awards", 'awards')
        self.key_info['title'] = extract_info("Title", 'title')

        # Add extraction for "Born" or birth date
        self.key_info['born'] = extract_info("Born", 'born')

        # Add extraction for "Died" or death date
        self.key_info['died'] = extract_info("Died", 'died')

        # Add extraction for spouse and children, if any
        self.key_info['spouse'] = extract_info("Spouse", 'spouse')
        self.key_info['children'] = extract_info("Children", 'children')

    def handle_keywords(self, text):
        keywords = {
            "list of inventions": "title",
            "discovery": "title",
            "known for": "known_for",
            "award": "awards",
            "born": "born",  # Added 'born' to match user queries like "When was Einstein born?"
            "death": "died",  # Added 'death' to capture death-related queries
            "spouse": "spouse",
            "children": "children"
        }
        for keyword, info_type in keywords.items():
            if keyword in text.lower():
                return '\n'.join(self.key_info.get(info_type, []))
        return None

    def respond(self):
        vectorizer = TfidfVectorizer(tokenizer=self.preprocess)
        tfidf = vectorizer.fit_transform(self.sentences)
        scores = cosine_similarity(tfidf[-1], tfidf)
        self.current_sent_idx = scores.argsort()[0][-2]
        scores = scores.flatten()
        scores.sort()
        value = scores[-2]
        if value != 0:
            response = self.sentences[self.current_sent_idx]
        else:
            response = "I am not sure. Sorry!"
            self.reset()
        if self.sentences:
            del self.sentences[-1]

        return response

    def scrape_wiki(self, topic):
        topic = topic.lower().strip().capitalize().split(' ')
        topic = '_'.join(topic)
        try:
            link = 'https://en.wikipedia.org/wiki/' + topic
            data = requests.get(link).content
            soup = BeautifulSoup(data, 'html.parser')

            # Extract paragraphs and description lists
            p_data = soup.findAll('p')
            dd_data = soup.findAll('dd')
            p_list = [p for p in p_data]
            dd_list = [dd for dd in dd_data]

            for tag in p_list + dd_list:
                a = []
                for i in tag.contents:
                    if i.name != 'sup' and i.string is not None:
                        stripped = ' '.join(i.string.strip().split())
                        a.append(stripped)
                self.text_data.append(' '.join(a))

            # Populate sentences and paragraph indices
            for i, para in enumerate(self.text_data):
                sentences = nltk.sent_tokenize(para)
                self.sentences.extend(sentences)
                index = [i] * len(sentences)
                self.para_indices.extend(index)

            # Extract title and check if it's found
            title_tag = soup.find('h1')
            if title_tag:
                self.title = title_tag.string
            else:
                raise Exception("Title not found")

            self.got_topic = True
            self.extract_key_info(soup)

            # Extract summary
            summary = '\n'.join(self.text_data[:2])
            summary = re.sub(r'\[\d+\]', '', summary)
            summary = re.sub(r'\([^)]*\)', '', summary)
            if self.title:
                summary = f"{self.title} - {summary}"


        except Exception as e:
            return f'Error: {e}. Please input some other topic!'


    def preprocess(self, text):
        text = text.lower().strip().translate(self.punctuation_dict)
        words = nltk.word_tokenize(text)
        words = [w for w in words if w not in self.stopwords]
        return [self.lemmatizer.lemmatize(w) for w in words]

chatbot = ChatBot()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message') #
    response = chatbot.chat(user_input)
    title = chatbot.name if chatbot.got_topic else "Welcome! Ask about an inventor."

    if isinstance(response, tuple):
        summary, _ = response
        if isinstance(summary, dict):
            return jsonify({
                'response': summary.get('summary', ''),
                'image_url': chatbot.photo_url if chatbot.photo_url else '',
                'title': title
            })
        else:
            return jsonify({'response': summary, 'image_url': '', 'title': title})
    elif isinstance(response, dict):
        return jsonify({
            'response': response.get('summary', ''),
            'image_url': chatbot.photo_url if chatbot.photo_url else '',
            'title': title
        })
    else:
        return jsonify({'response': response, 'image_url': '', 'title': title})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
