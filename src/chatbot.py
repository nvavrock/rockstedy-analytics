# this brings in stuff we need --------------------
from dotenv import load_dotenv   # lets us load secret keys from a .env file
from openai import OpenAI        # the AI brain (OpenAI)
import json                      # to work with JSON (like dictionaries in text form)
import os                        # to talk to your computer (like env vars)
import requests                  # to send messages to other websites (like pushover)
#from pypdf import PdfReader      # to read PDF files
import gradio as gr              # to make a little chat window in browser


# load secrets (like passwords) from .env file
load_dotenv(override=True)


### ---------------- Don't have an active Pushover Account, need keep this, but make it fail silently
## send a message to pushover app (like phone notifications)
#def push(text):
#   requests.post(
#        "https://api.pushover.net/1/messages.json",
#        data={
#            "token": os.getenv("PUSHOVER_TOKEN"),  # secret key from .env
#           "user": os.getenv("PUSHOVER_USER"),    # user id from .env
#            "message": text,                       # the text we want to send
#        }
#     )


# record someone’s email + name if they give it
#def record_user_details(email, name="Name not provided", notes="not provided"):
 #   push(f"Recording {name} with email {email} and notes {notes}")
 #   return {"recorded": "ok"}   # just says “ok” back


# record a question if the bot doesn’t know the answer
#def record_unknown_question(question):
#    push(f"Recording {question}")
#    return {"recorded": "ok"}   # again, says “ok” back


# this is like instructions for AI to know how to call record_user_details
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool if someone gives their email",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "Their email"},
            "name": {"type": "string", "description": "Their name"},
            "notes": {"type": "string", "description": "Extra info if any"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

# same but for recording questions the AI can’t answer
record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Use this tool if you don’t know the answer to a question",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question text"},
        },
        "required": ["question"],
        "additionalProperties": False
    }
}

# bundle both tools into a list so AI knows about them
tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]


# this class is like a “character” of you (the website’s AI)
class Me:

    def __init__(self):
        self.openai = OpenAI()          # start the OpenAI brain
        self.name = "Nate Vavrock"         # pretend to be this person

        with open("me/careerprofile.txt", "r", encoding="utf-8") as f:
            self.careerprofile = f.read()

        # also load summary from text file
        with open("me/interview_c.txt", "r", encoding="utf-8") as f:
            self.summary = f.read()

    # this runs when the AI decides it needs to call one of the tools
    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)  # grab the real function
            result = tool(**arguments) if tool else {}
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results
    
    # this builds the instructions for the AI
    def system_prompt(self):
        system_prompt = f"""
        You are acting as {self.name}. 
        You’re answering questions on {self.name}'s website about their career, background, and skills.
        Be professional, friendly, like you’re talking to a possible boss or client.
        If you don’t know an answer, use the record_unknown_question tool.
        If someone chats a lot, try to get their email and record it with record_user_details.
        """
        # include summary + LinkedIn text
        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.careerprofile}\n\n"
        system_prompt += f"Always stay in character as {self.name}."
        return system_prompt
    
    # the actual chat function
    def chat(self, message, history):
        messages = [
            {"role": "system", "content": self.system_prompt()}
        ] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            # ask the AI for a reply
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                message = response.choices[0].message
                tool_calls = message.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content
    


# this runs if you start the file directly
if __name__ == "__main__":
    me = Me()  # make the AI person
    # launch a gradio chat window so you can test in browser
    gr.ChatInterface(me.chat, type="messages").launch()
