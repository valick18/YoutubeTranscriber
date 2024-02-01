import openai
import properties

def updates(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages


class ResponseGenerator:
    openai.api_key = properties.openai_key

    ASSISTANT_ROLE = 'assistant'
    USER_ROLE = 'user'
    SYSTEM_ROLE = 'system'
    default = 'Your task is to write everything described in the audio file downloaded from YouTube, '
    'but in a beautifully structured format.'
    'All text need be on Ukrainian language'

    @staticmethod
    def generate_response(text, max_tokens=None, content=default):

        messages = [{"role": "system",
                     'content': content}]

        messages = updates(messages, "user", text)

        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages, max_tokens=max_tokens)
            bot_response = response['choices'][0]['message']['content']
            return bot_response
        except Exception as e:
            # e.with_traceback()
            return ''
