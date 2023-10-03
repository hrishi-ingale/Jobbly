from flask import Flask, request, render_template
import configparser
import requests
import json
from metaphor_python import Metaphor
import openai
import re
app = Flask(__name__)

config = configparser.ConfigParser()

config.read('/Users/hrishiingale/Desktop/Projects/Jobbly/util.cfg')
METAPHOR_SECRET_KEY = config.get('API_KEYS', 'META_KEY')
PROSPERO_SECRET_KEY = config.get('API_KEYS', 'PROSPERO_KEY')
OPEN_AI_SECREY_KEY = config.get('API_KEYS', 'OPENAPI_KEY')



def get_metaphor_data(position_type):
    metaphor = Metaphor(METAPHOR_SECRET_KEY)
    response = metaphor.search(
        position_type + "",
        num_results=25,
        use_autoprompt=True,
    )
    return str(response)
def convert_urls_to_links(text):
    url_pattern = r'https?://\S+'
    result_with_links = re.sub(url_pattern, r'<a href="\g<0>">\g<0></a>', text)
    return result_with_links

def get_linkedin_email(profile_url):
    url = "https://api.prospeo.io/linkedin-email-finder"
    required_headers = {
        'Content-Type': 'application/json',
        'X-KEY': PROSPERO_SECRET_KEY
    }
    data = {
        'url': profile_url
    }
    response = requests.post(url, json=data, headers=required_headers)
    try:
        if response.status_code == 200:
            json_data = response.json()
            return json.dumps(json_data)
        else:
            return None
    except Exception as e:
        return None
@app.route('/')
def home():
   return render_template('index.html')
   
def generate_response(metaphor_data, linkedin, num):
    openai.api_key = OPEN_AI_SECREY_KEY 
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": linkedin},
            {"role": "system", "content": metaphor_data},
            {"role": "user", "content": "Match " +num+ " jobs to canidate by determining skills as seen in their linkedin data that are seen in the metaphor data. Don't use company's in candidates linkedIn Make sure the jobs are for the year seen, if not, don't return it and return another one. Follow the format as seen: 1. [Name of Company][Name of position][Link to Position][Why fit] "
             }
        ]
    )

    return response.choices[0].message['content']

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        position_type = request.form.get("user_input2")
        num_of_inputs = request.form.get("user_input3")
        print(user_input)
        meta_data = get_metaphor_data(position_type)
        linkedin = get_linkedin_email(user_input)
        comparison = generate_response(meta_data, linkedin, num_of_inputs)
        print(comparison)
        result = process_input(comparison)
        print("result")
        return render_template("index.html", result=result)

    return render_template("index.html")

def process_input(user_input):
    result_with_links = convert_urls_to_links(user_input)
    return result_with_links

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
