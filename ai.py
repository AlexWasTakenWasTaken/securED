import os
from openai import OpenAI

api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# uses the OpenAI API to "grade" the essay.
def openai_feedback(essay):
    completion = client.chat.completions.create(
      model="gpt-4-1106-preview",
      messages=[
        {"role": "system", "content": "You're a high school teacher, grading an essay out of one hundred. Please give three strengths and three weaknesses and a final score"},
        {"role": "user", "content": "The essay is:" + essay}
      ]
    )

    # This is the feedback that the GPT-4 model gave.
    fb = str(completion.choices[0].message.content)

    return fb