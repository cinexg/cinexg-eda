import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

def generate_visualizations(df: pd.DataFrame, output_dir: str = "eda_visualizations") -> dict:
    """
    Generates and saves standard EDA plots: Missing values, Correlation Heatmap, and Histograms.
    """
    # 1. Create a directory to save the images safely
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"\n📊 Generating visualizations in '{output_dir}/'...")

    # 2. Missing Value Heatmap
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.isnull(), cbar=False, cmap='viridis', yticklabels=False)
    plt.title("Missing Values Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "missing_values.png"))
    plt.close() # CRITICAL: Close the plot to free up memory!

    # 3. Correlation Heatmap
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 1:
        plt.figure(figsize=(10, 8))
        corr = df[numeric_cols].corr()
        # annot=True puts the actual correlation numbers inside the colored squares
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5) 
        plt.title("Correlation Heatmap")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "correlation_heatmap.png"))
        plt.close()

    # 4. Histograms for Numeric Columns
    if len(numeric_cols) > 0:
        # Pandas has a built-in histogram function that handles multiple columns beautifully
        df[numeric_cols].hist(figsize=(12, 10), bins=20, edgecolor='black')
        plt.suptitle("Numeric Feature Distributions", y=1.02)
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, "numeric_distributions.png"))
        plt.close()
        
    print("✅ Visualizations saved successfully.")
    
    # Return the paths so our future report.py knows where to find the images
    return {
        "missing_plot": os.path.join(output_dir, "missing_values.png"),
        "corr_plot": os.path.join(output_dir, "correlation_heatmap.png") if len(numeric_cols) > 1 else None,
        "hist_plot": os.path.join(output_dir, "numeric_distributions.png") if len(numeric_cols) > 0 else None
    }
