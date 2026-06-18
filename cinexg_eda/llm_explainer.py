import os
import json

def generate_explanation(analysis_results, api_key=None):
    """
    Takes the EDA statistical results and uses an LLM to generate a plain-English summary.
    """
    try:
        import google.generativeai as genai
    except ImportError:
        return "⚠️ LLM explanation requires the 'google-generativeai' package."

    # check if the user passed a key, otherwise look for an environment variable
    key = api_key or os.environ.get("GEMINI_API_KEY")
    
    if not key:
        return "⚠️ LLM Explainer skipped: No GEMINI_API_KEY found. Set this environment variable to enable AI insights."

    try:
        genai.configure(api_key=key)
        # Using Gemini 1.5 Flash 
        model = genai.GenerativeModel('gemini-2.5-flash') 

        # We only send the metadata (stats, column names), NEVER the raw rows, to protect user data privacy
        prompt = f"""
        You are an expert Senior Data Scientist. I have performed an automated exploratory data analysis (EDA) on a dataset. 
        Here are the statistical highlights, missing values, and data quality checks:
        
        Overview: {json.dumps(analysis_results.get('Overview'))}
        Quality Alerts: {json.dumps(analysis_results.get('Quality_Checks'))}
        Correlations: {json.dumps(analysis_results.get('High_Correlations'))}
        ML Suggestions: {json.dumps(analysis_results.get('ML_Suggestions'))}

        Based strictly on this metadata, write a professional, concise 2-paragraph summary explaining:
        1. What kind of dataset this appears to be based on the column names and ML target guess.
        2. Any potential warnings, data leaks, or interesting insights a junior data scientist should investigate first before training a model.
        
        Do not use markdown headers, just return plain text paragraphs.
        """
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"⚠️ LLM generation failed: {str(e)}"
