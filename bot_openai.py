import openai
import json
import os

def ai_answers(prompt="\n\n###",
               model="text-davinci-003",              
               temperature=0.7,
               max_tokens=400,
               top_p=1,
               best_of =1,
               frequency_penalty=0,
               presence_penalty=0):
    openai.organization = os.getenv("ORGANIZATION")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    response = openai.Completion.create(
                                        model=model,
                                        prompt=prompt,
                                        temperature=temperature,
                                        max_tokens=max_tokens,
                                        top_p=top_p,
                                        best_of =1,
                                        frequency_penalty=0,
                                        presence_penalty=0
                                      )
    return json.loads(str(response))['choices'][0]['text'].replace('\n','')