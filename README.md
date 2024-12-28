### **Inventor ChatBot**
An AI-driven chatbot application built with Flask and Python, designed to provide detailed information about inventors and their inventions.
The chatbot fetches data from Wikipedia and processes user queries using natural language processing techniques.

## Features

  - **Wikipedia Integration**
    - Retrieves summarized information about inventors from Wikipedia.
    - Checks if the queried individual is an inventor by analyzing their biography.

   - **Interactive Chat:**
     - Responds to user greetings, gratitude, and farewell messages.
     - Handles specific queries about inventors like their inventions, awards, birth, death, etc.
     - Provides "more" detailed information on request.

   - **Web Scraping:**
     - Scrapes additional details such as titles, awards, known-for attributes, birth and death dates, etc., from Wikipedia.

   - **NLP and Information Extraction:**
     - Uses NLTK for tokenization, lemmatization, and stopword removal.
     - Utilizes TF-IDF Vectorization and Cosine Similarity to generate responses.

   - **Flask-Based Interface:**
     - Simple and user-friendly web interface to interact with the chatbot.
     - Supports real-time communication with JSON-based responses.

   - **Customizable Responses:**
     - Allows further processing of user queries to extract and highlight specific information.
---

## Technologies Used

### Backend:
- **Flask:** Framework for web application development.
- **NLTK:** Library for natural language processing.
- **Beautiful Soup:** Used for web scraping.

### Frontend:
- **HTML Templates:** For rendering the chat interface.
- **JSON-Based Communication:** Facilitates interaction between frontend and backend.

### APIs:
- **Wikipedia REST API:** Fetches summary information.

### Machine Learning:
- **TF-IDF Vectorizer and Cosine Similarity:** For contextual response generation.

### Other Libraries:
- **Requests:** Used for API communication.
- **Re (Regular Expressions):** For cleaning and processing text.

---

## How It Works

### User Interaction:
- The chatbot greets the user and encourages them to ask about inventors.
- Users input a name or query, and the bot fetches relevant information.

### Data Fetching and Processing:
- Queries Wikipedia for summary data or scrapes the website for detailed information.
- Processes the fetched data to extract structured information.

### Response Generation:
- Responds with a summary, image, and additional details as needed.
- Allows users to explore more by asking follow-up questions.

### Contextual Flow:
- Keeps track of ongoing conversations and relevant data for better user experience.

---

## Use Cases
- **Educational Tools:** Helps students learn about inventors and their contributions.
- **Knowledge Exploration:** Enables users to quickly gather structured information about historical and contemporary figures.
- **Conversational AI Showcase:** Demonstrates the integration of NLP, scraping, and chatbot technologies.
