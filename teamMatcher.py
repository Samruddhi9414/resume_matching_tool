import re
import json
import google.generativeai as genai

def match_resume_to_team(resume_text, teams_df):
    """Analyzes a resume and suggests the best-fit team(s) using Gemini with match scores."""
    try:
        model = genai.GenerativeModel('gemini-1.5-flash-latest')

        teams_list = "\n".join(
            [f"Team: {row['Subteam']}\nDescription: {row['Teamwork']}\n"
             for _, row in teams_df.iterrows()]
        )

        prompt = (
            "You are an AI HR assistant. Your job is to analyze a candidate's resume "
            "and recommend the most suitable team(s) from the list provided. "
            "For each team, provide:\n"
            "1. team_name (exact name from the provided list)\n"
            "2. reasoning (why the candidate is a fit)\n"
            "3. match_score (0–100, integer, how well the resume matches the team)\n\n"
            "If no strong match, include one entry with team_name: 'No strong match', "
            "reasoning: explanation, match_score: 0.\n\n"
            "Output JSON ONLY in this format:\n"
            "{ \"recommended_teams\": [ { \"team_name\": \"...\", \"reasoning\": \"...\", \"match_score\": ... } ] }\n\n"
            f"Here are the teams:\n{teams_list}\n\nResume:\n{resume_text}"
        )

        print("Matching resume with teams using Gemini...")  # helpful debug

        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        # Extract JSON using regex
        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                return {
                    "recommended_teams": [{
                        "team_name": "Uncertain",
                        "reasoning": "JSON parsing failed.",
                        "match_score": 0
                    }]
                }
        else:
            return {
                "recommended_teams": [{
                    "team_name": "Uncertain",
                    "reasoning": raw_text,
                    "match_score": 0
                }]
            }

    except Exception as e:
        return {
            "recommended_teams": [{
                "team_name": "Error",
                "reasoning": f"An error occurred: {e}",
                "match_score": 0
            }]
        }
