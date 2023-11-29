from flask_cors import CORS
import whisper
import os
import subprocess
import json
from openai import OpenAI
from flask import Flask, request, jsonify

API_KEY = 'apiKey.txt'
PROMPT_TEXT = 'prompt.txt'
CALL_LIMIT = 5
API_REPEAT_LIMIT = 3
REPEAT_PROMPT = 'repeat_prompt.txt'
current_working_directory = r"C:\Users\nik00\IdeaProjects\app0\stuff"

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


def read_text(name):
    if os.path.exists(name):
        with open(name, 'r') as file:
            return file.read()
    return None


def execute_command(command):
    global current_working_directory

    # Prepend a change directory command
    full_command = f'cd /d {current_working_directory} && {command}'

    try:
        result = subprocess.run(full_command, shell=True, text=True, capture_output=True)
        # Update the current working directory if the command changes it
        if command.startswith("cd "):
            current_working_directory = command.split("cd ")[1].strip()
            print(f"current_working_directory: {current_working_directory}")
        return result.stderr + result.stdout
    except subprocess.SubprocessError as e:
        return str(e)


def interact_with_gpt(conversation_history, client):
    try:
        print(f"Sending request: {find_last_user_content(conversation_history)[:100]}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {e}")
        return f"Error in generating response: {str(e)}"


def find_last_user_content(conversation_history_l):
    for message in reversed(conversation_history_l):
        if message["role"] == "user":
            return message["content"]
    return None


repeat_conversation_states = {}
api_recall_counter = 0
repeat_client = OpenAI(api_key=read_text(API_KEY))


def parse_response(response_text):
    global api_recall_counter
    plan = response_text
    response = response_text
    command = ""
    final = True
    try:
        parsed_response = json.loads(response_text)
        if "Plan" not in parsed_response and api_recall_counter < API_REPEAT_LIMIT:
            print("Plan not in parsed_response")
            conversation_history = [
                {"role": "system", "content": read_text(REPEAT_PROMPT)},
                {"role": "user", "content": response_text}
            ]
            revised_response_text = interact_with_gpt(conversation_history, repeat_client)
            print(f"Revised Response: {revised_response_text}")
            print(f"Revised Response counter: {api_recall_counter + 1}")
            api_recall_counter += 1
            return parse_response(revised_response_text)
        plan = parsed_response.get("Plan", plan)
        response = parsed_response.get("Response", response)
        command = parsed_response.get("Command", command)
        final = parsed_response.get("Final", final)
    except json.JSONDecodeError:
        print("JSONDecodeError")
        if api_recall_counter < API_REPEAT_LIMIT:
            conversation_history = [
                {"role": "system", "content": read_text(REPEAT_PROMPT)},
                {"role": "user", "content": response_text}
            ]
            revised_response_text = interact_with_gpt(conversation_history, repeat_client)
            print(f"Revised Response: {revised_response_text}")
            print(f"Revised Response counter: {api_recall_counter + 1}")
            api_recall_counter += 1
            return parse_response(revised_response_text)
    return plan, response, command, final


# Initialize Whisper model
model = whisper.load_model("base")


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'audioFile' in request.files:
        audio_file = request.files['audioFile']
        audio_file.save("temp.wav")
        result = model.transcribe("temp.wav", fp16=False)
        return {'transcription': result['text']}
    return {'error': 'No audio file found'}


# Initialize a dictionary to hold conversation states
conversation_states = {}
main_client = OpenAI(api_key=read_text(API_KEY))


@app.route('/chatgpt', methods=['POST'])
def chat_with_gpt():
    session_id = request.json.get("session_id")
    user_message = request.json.get("message")

    # Retrieve or initialize the conversation history for the session
    # Start with the initial system message when the conversation is first created
    if session_id not in conversation_states:
        conversation_states[session_id] = [{"role": "system", "content": read_text(PROMPT_TEXT)}]

    conversation_history = conversation_states[session_id]

    # Append the new user message to the conversation history
    conversation_history.append({"role": "user", "content": user_message})
    print(f"User Message: {user_message}")

    final = False
    text_response = ''
    command_output = ''
    counter = 0

    while not final and counter < CALL_LIMIT:
        # Call the OpenAI API with the conversation history
        response_text = interact_with_gpt(conversation_history, main_client)
        print(f"Response: {response_text}")
        conversation_history.append({"role": "assistant", "content": response_text})

        parsed_response = parse_response(response_text)
        text_response = parsed_response[1] + "\n" + parsed_response[0]
        input_command = parsed_response[2]
        final = parsed_response[3]
        print(f"Assistant Response: {text_response}")
        print(f"Command Input: {input_command}")
        print(f"Final: {final}")

        command_output = execute_command(input_command) if input_command else ''
        conversation_history.append({"role": "user", "content": command_output})
        counter += 1

        print(f"Terminal Output: {command_output[:100]} ...")
        print(f"Counter: {counter}")

    # Save the updated conversation history back into the conversation states
    conversation_states[session_id] = conversation_history

    return jsonify({'chatGptResponse': text_response, 'commandOutput': command_output})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
