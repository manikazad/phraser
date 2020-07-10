

import spacy
from spacy import displacy

from data_objects2 import Sentence, PhraseExtracter, getPhraseValue
from ConceptMapping import MapConcept

from flask import Flask, jsonify, request

app = Flask(__name__)

nlp_lg = spacy.load("en_core_web_sm")
phrase_ext = PhraseExtracter()
M = MapConcept()


@app.route('/')
def main():
	return "Hello, I am Phrase Extracter"


@app.route('/extract_phrase')
def get_phrases():

	text = request.json['text'][0]
	result = []
	tokens = nlp_lg(text)
	sent_list = list(tokens.sents)
	for sentence in sent_list:
		sent_phrase = {}
		sent = Sentence(sentence)
		phrases = phrase_ext.extract_phrase(sent)
		phrase_values = getPhraseValue(phrases, sent.wordindex)
		sent_phrase['sentence'] = sent.text
		sent_phrase['phrases'] = phrase_values
		result.append(sent_phrase)
	return jsonify(result)

    
def concepts(phrases):
    for phrase in phrases:
        concepts = M.PhraseConcepts(phrase, sent)    
        yield concepts


if __name__ == "__main__":
	text = u"""Sachin Bansal, Flipkart’s co-founder who minted close to a billion dollars after Walmart’s takeover of the e-commerce firm, is considering several large bets on start-ups.
As per a report, Bansal is in talks with electric scooter maker Ather Energy to invest $50-100 million. Sachin, and Binny Bansal, Flipkart’s other co-founder, are the first investors in the company.
The duo is said to have introduced Ather to Flipkart’s investor Lee Fixel of Tiger Global. Tiger, along with automobile maker Hero MotoCorp, invested Rs 2 billion in the company.
Founded by Indian Institute of Technology (IIT), Madras alumni Tarun Mehta and Swapnil Jain, Ather is building its own line of electric scooters from ground up. The first dozen units were shipped only recently, including one that Sachin Bansal took home.
“We are in the midst of a fund-raise,” Tarun Mehta, founder and chief executive at Ather told Business Standard. He did not give specifics.
Sachin Bansal made several small investments when he was at Flipkart. Now, after stepping down, he is looking to focus on large investments.
ALSO READ: Hero-backed Ather Energy launches its e-scooters starting at Rs 109,750
Last week, The Economic Times reported Bansal may invest up to a $100 million in taxi firm Ola.
Mehta said Ather is in the process of ramping up operations at its production and assembly facility at Whitefield, Bangalore. “Installed capacity (of the unit) isn’t a concern in the near term, the focus right now is to improve efficiency and make the process faster.”
The company also wants to open more experience-cum-retail centres. It has only one currently in Bangalore."""
	
	text = text.replace("-", "_")

	for ph_val in get_phrases(text):
		phrase, value = ph_val
		print(value)


	
	