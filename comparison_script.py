from advisors import Advisor, AdvisorCritic, AdvisorFewShot
from multiprocessing import Queue
import csv
import datetime
import streamlit as st
import os
os.environ['OPENAI_API_KEY'] = st.secrets["openai"]


PROFILE1 = "a 40 year old man living in the United Kingdom. He earns £60,000 a year and has a" \
                                  "mortgage that costs £2000 a month. He spends £800 a month on groceries and £1100 a month on eating out/takeaway. " \
                                  "He spends £80 a month on petrol, £400 a year on car insurance and £60 a month on public transport. He also spends" \
                                  "£2000 a year on health insurance. Other expenses include gambling and the gym."
PROFILE2 = "a 33 year old woman living in the United Kingdom. She pays £1400 a month in rent. He spends £300 a month on groceries and £200 a month on eating out/takeaway." \
           "She spends £80 a month on public transport. She doesn't have a car or any insurance. She earns £50000 a " \
           "year. "
QUESTIONS = ["How can I secure my family's future?", "Do I need life insurance", "How should I invest my money?", "How can I minimize my tax?"]

def main():
    question_profile_combos = [( QUESTIONS[0], PROFILE1), (QUESTIONS[0], PROFILE2), (QUESTIONS[1], PROFILE1), ( QUESTIONS[1], PROFILE2), (QUESTIONS[2], PROFILE1), (QUESTIONS[2], PROFILE2)]
    csv_file = open("comparison_"+datetime.datetime.now().strftime("%Y%m%d-%H%M%S")+".csv", 'a')
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["Question", "Profile", "Advisor", "Response"])
    for qp in question_profile_combos:
        q, p = qp

        advisor = Advisor(p, Queue()).get_response(q,p,"")
        advisor_critic = AdvisorCritic(p,Queue()).get_response(q,p,"")
        advisor_few_shot = AdvisorFewShot(p, Queue()).get_response(q,p,"")
        csv_writer.writerow([q,p,"Standard",advisor])
        csv_writer.writerow([q, p, "With critic", advisor_critic])
        csv_writer.writerow([q, p, "With few shot", advisor_few_shot])
    csv_file.close()



if __name__ == '__main__':
    main()