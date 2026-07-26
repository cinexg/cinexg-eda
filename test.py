import statlens
import pandas as pd
import numpy as np

# Create a robust dummy dataset
dummy_data = {
    "age": [25, 30, np.nan, 22, 40, 35, 28, 50, 45, 33],
    "salary": [50000, 60000, np.nan, 45000, 80000, 70000, 55000, 90000, 85000, 65000],
    "department": ["IT", "HR", "Sales", "IT", "Marketing", "HR", "IT", "Sales", "Marketing", "HR"],
    "is_remote": [True, False, True, True, False, False, True, False, True, False],
    "years_experience": [1, 3, 2, 1, 10, 5, 4, 15, 12, 6] 
}

# Let's save this as a real CSV to test the file loading capability!
df = pd.DataFrame(dummy_data)
df.to_csv("test_dataset.csv", index=False)

# Run the final report generator
statlens.report("test_dataset.csv", output="my_first_eda_report.html")