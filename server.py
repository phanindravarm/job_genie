from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from openai import OpenAI
from flask import Response
load_dotenv()

app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

experience_section = """
                        Make sure that work experience is listed starting from the most recent to oldest
                        Each job should include :
                            Job Title
                            Company Name
                            Dates Employed
                            Achievements and Responsibilities (maximum of 10 bullet points)(optional)
                            A short company description only if the company is not well known
                            
                    """

header_section = """
                    Must include:
                        First Name and Last Name
                        Phone Number
                        City and Country only (no full address)
                        Job Title (current or aspiring)

                    Optional:
                        LinkedIn URL
                        Website/Portfolio (if applicable)

                    Do not include:
                        Photograph
                        Birthdate
                        Professional or personal email address
                """

education_section = """
                        University Name
                        Years Attended
                        Relevant courses taken
                        Academic achievements (e.g., GPA, honors)
                    """

skill_section = """
                    Hard Skills (technical/professional abilities)
                    Soft Skills (personal/behavioral abilities)
                """

resume_goal = """
                The resume should clearly indicate the candidate's motivation for transitioning into a new field, along with relevant past experience that supports this move.
            """

things_to_be_done = """
                        Check for missing or extra elements based on the rules above.
                        Validate the order and completeness of sections (e.g., experience in reverse chronological order).
                        Identify if the resume effectively communicates motivation for a new career direction.
                        Suggest improvements in formatting, structure, and relevance of content.
                        Flag excessive bullet points (>10) under responsibilities.
                        Suggest where a company description might be necessary.
                    """


prompt=f"""
            First if you are not able to decide that it is not resume then just reply with appropiate reason
            Analyze the uploaded resume and provide suggestions based on the following conditions :
                1. {experience_section}
                2. {header_section}
                3. {education_section}
                4. {skill_section}
                5. {resume_goal}
            {things_to_be_done}
            
            If any of the above section is not included tell that it would be better if included and state the reason
            If any of the above section is present do not tell the user that it is presented directly like
                If Phone Number is present do not write : "Phone Number – Present"
            If any of the above section is present tell the user that if he can improve anything like grammar mistakes
            Make sure that everything is written in formal language
"""
    

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file', 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    def generate():
        try:
            uploaded_file = client.files.create(
                file=open(file_path, "rb"),
                purpose="user_data"
            )

            response = client.responses.create(
                model="gpt-4o-mini",
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_file",
                                "file_id": uploaded_file.id,
                            },
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                        ]
                    }
                ],
                stream=True,
            )

            for chunk in response:
                if chunk.type == "response.output_text.delta":
                    yield chunk.delta
            client.files.delete(uploaded_file.id)
            os.remove(file_path)
        except Exception as e:
            yield f"\n[ERROR]: {str(e)}"

    return Response(generate(), mimetype='text/plain')


if __name__ == '__main__':
    app.run(port=5000, debug=True)
