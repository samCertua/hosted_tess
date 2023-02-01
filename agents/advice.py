import openai
import uuid
import datetime


def get_suggested_goals(profile):
    prompt = "Help me find some good financial goals. I am " + profile + " Explain how they help this person specifically."
    return openai.Completion.create(model="text-davinci-003", prompt=prompt, temperature=0.2, max_tokens=1000)["choices"][0].text

def gen_context(profile, suggested_goals):
    return "You are an AI expert financial advisor talking to " + profile + \
           "Converse with them in a helpful manner, giving the best financial advice possible using the information " \
           "provided. Do not write questions for them and explain any reasoning.\n" \
           "Some suggested financial goals are: \n" +suggested_goals+\
           "AI: What can I help you with?\n"\

def get_advice(query, profile, session_id, user_messages, ai_messages, suggested_goals, logging_queue):
    context = gen_context(profile, suggested_goals)
    gpt_query = build_gpt_query(query, user_messages, ai_messages, context)
    print(gpt_query)
    resp = openai.Completion.create(model="text-davinci-003", prompt=gpt_query, temperature=0.2, max_tokens=500)["choices"][0].text
    logging_queue.put((uuid.uuid4(), session_id, "FinancialGoalsAdvisor",
                            datetime.datetime.now(),
                            gen_context(" <profile> ", "<financial goals>"),
                            query, resp, gen_context(profile, suggested_goals)))
    return resp

def build_gpt_query(query, user_messages, ai_messages, context):
    '''
    Add the paragraphs most relevant to the query and a query to a message to be sent to GPT
    '''
    gpt_query = context
    if len(ai_messages) > 1:
        gpt_query += f'Human: {user_messages[-2]}\n'
        gpt_query += f'AI: {ai_messages[-2]}\n'
        gpt_query += f'Human: {user_messages[-1]}\n'
        gpt_query += f'AI: {ai_messages[-1]}\n'
    if len(ai_messages) == 1:
        gpt_query += f'Human: {user_messages[-1]}\n'
        gpt_query += f'AI: {ai_messages[-1]}\n'
    gpt_query += f'Human: {query}\nAI:'
    return gpt_query