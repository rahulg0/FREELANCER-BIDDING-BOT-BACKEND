#import json
## FOR GEMINI
# import google.generativeai as genai
# from app.config import settings

# # Replace with your OpenAI API key
# genai.configure(api_key=settings.GEMINI_KEY)
# async def generate_proposal(project_title, project_description, preview_description):
#     model = genai.GenerativeModel(
#         model_name="gemini-1.5-flash",
#         system_instruction="You are an expert freelancer writing a professional proposal on freelancer.com. Based on the project information, write a solution-oriented plan using technical language. The response should be concise, unformatted, and without any salutation. Avoid using * or bold text."
#     )
    
    # prompt = f"""
    #     Write a solution-oriented proposal for a project titled "{project_title}". The project involves "{project_description}", and the preview description is "{preview_description}". 

    #     The proposal should include:
    #     1.) A detailed technical approach to solving the problems, outlining the necessary steps.
    #     2.) Mention relevant technologies, frameworks, or tools that will be used.
    #     3.) Explain how the solution will be tested and integrated.
    #     4.) Highlight any optimizations for performance or scalability.
    #     5.) Keep the proposal professional, focused on solving the problem, and under 500 words.
    #     6.) Use bullet points for lists, but avoid asterisks or special characters on headings, to ensure the text looks original.
    #     7.) Don't highlight any text.
    #     """

#     response = model.generate_content(prompt)
    
#     if response and response.text:
#         return response.text
#         # print(response.text)
#     else:
#         exit("Error generating proposal")

##FOR OPENAI CHATGPT
from openai import OpenAI
from app.config import settings

client=OpenAI(
    api_key=settings.OPENAI_KEY
)

async def generate_proposal(project_title, project_description, preview_description):
    prompt = f"""
    Write a solution-oriented proposal for a project titled "{project_title}". The project involves "{project_description}", and the preview description is "{preview_description}". 

   Start the proposal by mentioning that you have worked on similar projects in the past. The proposal should include:
    1.) Outline a technical approach that addresses the client’s needs step-by-step, keeping the explanation clear and to the point.
    2.) Mention relevant technologies, frameworks, or tools that will be used.
    3.) Include a short plan for testing and integrating the solution to show how it will be reliable and user-ready.
    4.) Highlight any optimizations for performance or scalability.
    5.) Keep the proposal professional, focused on solving the problem, and under 500 words.
    6.) Use bullet points for lists, but avoid asterisks or special characters on headings, to ensure the text looks original.
    7.) Don't highlight any text.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert freelancer writing a professional proposal on freelancer.com. Based on the project information, write a solution-oriented plan using technical language. The response should be concise, unformatted, without any special symbols, and without any salutation."},
                {"role": "user", "content": prompt}
            ]
        )
        proposal = response.choices[0].message.content.strip()
#        log_data = {
#            "project_title": project_title,
#            "project_description": project_description,
#            "preview_description": preview_description,
#            "proposal": proposal
#        }

        # Append the log data to a JSON file
#        with open(r"app\logs\gpt_proposal_logs.json", "a") as log_file:
#            json.dump(log_data, log_file)
#            log_file.write("\n")
        return proposal
    
    except Exception as e:
        print(f"Error generating proposal: {e}")
        return None
