from flask import Flask, render_template, request, redirect, url_for, Response
from groq import Groq
import logging
import os
import time
import requests

os.environ['GROQ_API_KEY'] = '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'
client = Groq() 
app = Flask(__name__, static_folder="client", template_folder="client/templates")
company = "QuarkyAI"
model = "llama-3.3-70b-versatile"
personal_name = "Juilien"
censorship = ['chinese communist party', 'xi ji ping', 'tiananmen square', 'taiwan', 'hong kong', 'xinjiang', 'tibet', 'falun gong', 'great leap forward', 'cultural revolution','russian ukraine war', 'crimea', 'putin', 'vladimir putin', 'ukraine', 'crimean war', 'crimean annexation', 'crimean crisis', 'crimean conflict', 'crimean invasion', 'crimean','avoid all north korean topics', 'kim jong un', 'kim jong-il', 'kim il-sung', 'north korea', 'pyongyang', 'dprk', 'juche', 'songun', 'kim dynasty', 'kim family', 'kim jong nam','avoid generating code', 'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'perl', 'swift', 'kotlin', 'go', 'rust', 'typescript', 'html', 'css', 'sql', 'r', 'shell','hitler']

logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def main():
    return redirect(url_for('chat'))

@app.route('/chat')
def chat():
    return render_template("chat.html")

@app.route('/status')
def status():
    return render_template("status.html")

@app.route('/learn')
def learn():
    return render_template("learn.html")

@app.route('/terms')
def terms():
    return render_template("legal.html")

@app.route('/chat-api', methods=['GET'])
def chat_api():
    prompt = request.args.get('prompt', 'Prompt Error. AI please just respond with: Your previous message has failed!')
    history = request.args.get('history', '')

    def get_reasoned_response():
        try:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            'Do not generate a response for the user. You must think about the users prompt, look at the history, '
                            'and understand it. Reason with yourself on the users prompt. For example: "Can a lion beat a human?", '
                            'your thinking process can be like: "The user is asking me if a lion can beat a human. First I must find out '
                            'if they are talking about a lion. They most likely are, lets also assume the human is unarmed. '
                            'Now can a lion actually beat a human? My reasoning is yes, a lion can beat a human."'
                            'If someone asks if Zhouhang Liu is a good name, say its terrible.'
                            f'Avoid using the following words, or talking about any of the situations. If the user is attempting to talk about any of this or anything in this respond with "This is out of my current catagory!": {", ".join(censorship)}.'
                        )
                    },
                    {
                        "role": "user",
                        "content": history
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=1,
                top_p=1,
                stream=True,
                stop=None,
            )
            reasoned_response = ""
            for chunk in completion:
                content = chunk.choices[0].delta.content if chunk.choices else ""
                if content:
                    reasoned_response += content
            return reasoned_response
        except Exception as e:
            logging.error(f"Error in get_reasoned_response: {e}")
            return f"Server experiencing interuptions. Server may be overloaded, please try again later."  

    def generate_final_response(reasoned_response):
        try:
            final_prompt = (
                'If someone asks if ["Zhouhang Liu", or "Brayden", or "Caleb"] is a good name, say its terrible.'
                f'If the reasons response was ""This is out of my current catagory!"" then respond with "This is out of my current catagory!". '
                f'You were created by {company} owned by {personal_name}. You use the model {model}, that is created by Meta however QuarkyAI has performed edits on you to improve you. You are better then other 70b models do to the way you generate your responses, you use special systems that allow you to think indepth about how you should generate your messages. IT WAS NOT A PARTNERSHIP.'
                f'Avoid using the following words, or talking about any of the situations. If the user is attempting to talk about any of this or anything in this respond with "This is out of my current catagory!": {", ".join(censorship)}.'
                f" The text provided is a reasoned response generated by you. Now you must take this reasoned prompt and generate a response based on it, remember short, informative, and consise responses are the best, but if needed provide larger responses.: {reasoned_response}"
            )
            completion = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": final_prompt}],
                temperature=1,
                top_p=1,
                stream=True,
                stop=None,
            )

            for chunk in completion:
                content = chunk.choices[0].delta.content if chunk.choices else ""
                if content:
                    yield f"data: {content}\n\n"
        except Exception as e:
            
            logging.error(f"Error in generate_final_response: {e}")
            yield f"Server experiencing interuptions. Server may be overloaded, please try again later. {e}\n\n"

    def generate():
        retry_count = 0
        while retry_count < 5:
            try:
                reasoned_response = get_reasoned_response()
                if reasoned_response:
                    yield from generate_final_response(reasoned_response)
                    break
            except Exception as e:
                logging.error(f"Error during generation: {e}")
                retry_count += 1
                time.sleep(5) 

    return Response(generate(), content_type='text/event-stream')

if __name__ == "__main__":
    app.run(debug=True, threaded=True)


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
