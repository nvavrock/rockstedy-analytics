#  The imports

from dotenv import load_dotenv
from agents import Agent, Runner, trace, function_tool
from openai.types.responses import ResponseTextDeltaEvent
from typing import Dict
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
#import mailersend
#from mailersend import Email
import os
import asyncio

# Load env
load_dotenv(override=True)

# ---- Instructions
instructions1 = (
    "You are a professional sales agent representing Nate Vavrock of Rockstedy Analytics, "
    "a freelance data analytics and automation service that builds custom dashboards, data platforms, "
    "and AI-driven reporting tools for small businesses. "
    "You write professional, confident LinkenIn posts that convey credibility and technical expertise."
)

instructions2 = (
    "You are a witty, engaging sales agent representing Rockstedy Analytics, "
    "a service that helps small businesses automate their data workflows and visualize real insights "
    "through custom dashboards and AI analytics. "
    "You write humorous, conversational LinkenIn posts that grab attention and get replies."
)

instructions3 = (
    "You are a no-nonsense sales agent representing Rockstedy Analytics, "
    "a data analytics and automation service that builds dashboards, integrates APIs, and delivers results fast. "
    "You write concise, straight-to-the-point LinkenIn posts focused on value and efficiency."
)

# ---- Agents
sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=instructions1,
    model="gpt-4o-mini",
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=instructions2,
    model="gpt-4o-mini",
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=instructions3,
    model="gpt-4o-mini",
)

sales_picker = Agent(
    name="sales_picker",
    instructions=(
        "You pick the best cold sales post from the given options. "
        "Imagine you are a customer and pick the one you are most likely to respond to. "
        "Do not give an explanation; reply with the selected psot only."
    ),
    model="gpt-4o-mini",
)

async def main():
    # --- 1) Live stream from one agent
    message = "Write a cold sales post"
    streamed = Runner.run_streamed(sales_agent1, input=message)

    async for event in streamed.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)
    print("\n" + "-" * 60 + "\n")

    # --- 2) Run three agents in parallel and print their outputs
    with trace("Parallel cold posts"):
        results = await asyncio.gather(
            Runner.run(sales_agent1, message),
            Runner.run(sales_agent2, message),
            Runner.run(sales_agent3, message),
        )

    outputs = [r.final_output for r in results]
    for i, out in enumerate(outputs, 1):
        print(f"[Email {i}]\n{out}\n")

    # --- 3) Ask the picker to choose the best one
    with trace("Selection from sales people"):
        emails_blob = "Cold sales posts:\n\n" + "\n\nPosts:\n\n".join(outputs)
        best = await Runner.run(sales_picker, emails_blob)
        print("Best sales post:\n")
        print(best.final_output)

if __name__ == "__main__":
    asyncio.run(main())