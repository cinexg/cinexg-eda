import os
from .analyzer import analyze, _load_dataset
from .visualization import generate_visualizations
from .llm_explainer import generate_explanation 

def report(file_path, output="report.html"):
    """
    Generate a complete EDA report in HTML format.
    """
    print(f"🚀 Starting full EDA report generation for '{file_path}'...")
    
    results = analyze(file_path)
    
    print("🧠 Generating AI executive summary (this takes a few seconds)...")
    ai_insights = generate_explanation(results)

    df = _load_dataset(file_path)
    
    image_paths = generate_visualizations(df, output_dir="eda_assets")
    
    # 4. Build the HTML Template
    # We use a multi-line f-string to inject our Python variables directly into the HTML
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cinexg-EDA Report</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #f4f7f6; color: #333; }}
            h1, h2, h3 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
            .container {{ background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 1000px; margin: auto; }}
            .stats-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
            .alert {{ background-color: #ffeaa7; padding: 10px; border-left: 5px solid #fdcb6e; margin-bottom: 10px; }}
            img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 4px; margin-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Cinexg-EDA Automated Report</h1>
            
            <div style="background-color: #e8f4f8; padding: 20px; border-left: 5px solid #3498db; margin-bottom: 25px; border-radius: 4px;">
                <h2 style="margin-top: 0; color: #2980b9;">✨ AI Executive Summary</h2>
                <p style="white-space: pre-wrap; line-height: 1.6; font-size: 1.1em;">{ai_insights}</p>
            </div>

            <h2>1. Dataset Overview</h2>
            <div class="stats-grid">
                <div>
                    <p><strong>Rows:</strong> {results['Overview']['Rows']:,}</p>
                    <p><strong>Columns:</strong> {results['Overview']['Columns']}</p>
                </div>
                <div>
                    <p><strong>Numerical Columns:</strong> {results['Column_Types']['Numerical']}</p>
                    <p><strong>Categorical Columns:</strong> {results['Column_Types']['Categorical']}</p>
                </div>
            </div>

            <h2>2. Machine Learning Suggestions</h2>
            <div class="alert">
                <p><strong>Guessed Target Column:</strong> {results['ML_Suggestions']['Target_Column_Guess']}</p>
                <p><strong>Probable ML Task:</strong> {results['ML_Suggestions']['Task']}</p>
                <p><strong>Suggested Models:</strong> {', '.join(results['ML_Suggestions']['Suggested_Models'])}</p>
            </div>

            <h2>3. Data Quality Alerts</h2>
            <ul>
                <li><strong>Duplicate Rows:</strong> {results['Quality_Checks']['Duplicate_Rows']}</li>
                <li><strong>Constant Columns:</strong> {', '.join(results['Quality_Checks']['Constant_Columns']) if results['Quality_Checks']['Constant_Columns'] else 'None detected'}</li>
            </ul>

            <h2>4. Visualizations</h2>
            <h3>Missing Values</h3>
            <img src="{image_paths['missing_plot']}" alt="Missing Values Heatmap">
            
            <h3>Numeric Distributions</h3>
            """
    
    # Conditionally add the histogram if it exists
    if image_paths.get('hist_plot'):
        html_content += f'<img src="{image_paths["hist_plot"]}" alt="Histograms">'
        
    # Conditionally add the correlation map if it exists
    if image_paths.get('corr_plot'):
        html_content += f"""
            <h3>Correlation Heatmap</h3>
            <img src="{image_paths['corr_plot']}" alt="Correlation Heatmap">
        """

    html_content += """
        </div>
    </body>
    </html>
    """

    # 5. Write the HTML string to a file
    with open(output, "w", encoding="utf-8") as f:
        f.write(html_content)
        
    print(f"\n✅ SUCCESS: Report generated and saved to '{output}'")
