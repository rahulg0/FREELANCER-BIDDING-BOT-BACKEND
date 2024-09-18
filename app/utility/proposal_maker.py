import google.generativeai as genai
from app.config import settings

# Replace with your OpenAI API key
genai.configure(api_key=settings.GEMINI_KEY)
async def generate_proposal(project_title, project_description, preview_description):
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction="You are an expert freelancer writing a professional proposal on freelancer.com. Based on the project information, write a solution-oriented plan using technical language. The response should be concise, unformatted, and without any salutation. Avoid using * or bold text."
    )
    
    prompt = f"""
    Write a solution-oriented proposal for a project titled "{project_title}". The project involves "{project_description}", and the preview description is "{preview_description}". 

    The proposal should include:
    1.) A detailed technical approach to solving the problems, outlining the necessary steps.
    2.) Mention relevant technologies, frameworks, or tools that will be used.
    3.) Explain how the solution will be tested and integrated.
    4.) Highlight any optimizations for performance or scalability.
    5.) Keep the proposal professional, focused on solving the problem, and under 500 words.
    6.) Do not use any formatting like bold, italics, or lists that include *, and keep everything as plain text and if possible in points.
    7.) Dont highlight any text.
    """

    response = model.generate_content(prompt)
    
    if response and response.text:
        return response.text
        # print(response.text)
    else:
        exit("Error generating proposal")