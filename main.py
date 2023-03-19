
import os
import string
import secrets
import subprocess
import re
from dotenv import load_dotenv
from pyrogram import Client, filters

trg = "/"
load_dotenv()  # Load the environment variables from the .env file
api_id = os.environ.get('API_ID')
api_hash = os.environ.get('API_HASH')
bot_token = os.environ.get('BOT_TOKEN')

# Define the function to generate a random password
def generate_password(length):
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(chars) for i in range(length))
    return password

# Define the function to execute shell commands
def execute_command(command):
    # Validate user input
    if not re.match(r'^[a-zA-Z0-9_\-. ]+$', command):
        return "Invalid command"
    
    try:
        # Execute the command and get the output
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        # Return the error message if the command failed
        return e.output.decode('utf-8')

# Define the function to handle messages
@Client.on_message(
    ~filters.private & filters.command(
        ['password', 'eval', 'sh' , 'ytdl' ],
        prefixes=trg
    )
)
#@Client.on_message(filters.text & filters.command()
def handle_message(client, message):
    input_text = message.text.strip()
    user_info = message.from_user

    if input_text.startswith("/password "):
        # Generate a random password
        try:
            length = int(input_text[10:])
            if 4 <= length <= 128:
                password = generate_password(length)
                response_text = f"Your password is: `{password}`"
            else:
                response_text = "Password length must be between 4 and 128 characters"
        except ValueError:
            response_text = "Invalid password length"
    elif input_text.startswith("/eval "):
        # Execute a Python expression
        expression = input_text[6:]
        try:
            result = str(eval(expression))
            response_text = f"Result: {result}"
        except Exception as e:
            response_text = f"Error: {e}"
    elif input_text.startswith("/sh "):
        # Execute a shell command
        command = input_text[4:]
        response_text = execute_command(command)
    elif input_text.startswith("/ytdl "):
        # Download a YouTube video
        url = input_text[6:]
        command = f"youtube-dl -f bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio \
                   --merge-output-format mp4 --output '%(title)s.%(ext)s' {url}"
        response_text = execute_command(command)
    else:
        # Default response
        response_text = "Invalid command"
    
    # Send the response to the user
    if message.reply_to_message:
        message.reply(response_text, reply_to_message_id=message.reply_to_message.message_id, quote=True)
    else:
        message.reply_text(response_text)

# Main function
bot = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)
bot.run() 
