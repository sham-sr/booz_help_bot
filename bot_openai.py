import openai
import json

def ai_answers(organization,
               api_key,
               prompt="\n\n###",
               model="text-davinci-003",              
               temperature=0.7,
               max_tokens=400,
               top_p=1,
               best_of =1,
               frequency_penalty=0,
               presence_penalty=0):
    openai.organization = organization
    openai.api_key = api_key
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