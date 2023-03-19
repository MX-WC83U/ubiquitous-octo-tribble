
import os
import telegram
import telegram.ext
from dotenv import load_dotenv
import string
import secrets
import subprocess
import re

load_dotenv()  # Load the environment variables from the .env file
telegram_api_token = os.environ.get('TELEGRAM_BOT_TOKEN')

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
def handle_message(update, context):
    message = update.edited_message if update.edited_message else update.message
    input_text = message.text.strip()
    user_info = message.from_user

    if input_text.startswith("/password "):
        # Generate a random password
        try:
            length = int(input_text[10:])
            if 4 <= length <= 128:
                password = generate_password(length)
                response_text = f"Your password is: {password}"
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
    if update.edited_message:
        message.chat.send_message(response_text, reply_to_message_id=update.edited_message.message_id)
    else:
        message.reply_text(response_text)

# Main function
def main():
    updater = telegram.ext.Updater(token=telegram_api_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(telegram.ext.MessageHandler(telegram.ext.Filters.text & ~telegram.ext.Filters.command, handle_message))
    dp.add_error_handler(lambda update, context: print("Error:", context.error))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
