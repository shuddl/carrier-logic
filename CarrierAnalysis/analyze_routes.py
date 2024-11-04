import pandas as pd
import folium
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import zscore
import os
from scipy import stats
import numpy as np

class CarrierRouteAnalysis:
    def __init__(self):
        pass  # Placeholder method

def main():
    print("Welcome to the Carrier Route Analysis System!")
    
    # Automatically detect the Excel file
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~$')]
    
    if not excel_files:
        print("No Excel files found in the current directory!")
        return
    
    if len(excel_files) == 1:
        file_path = excel_files[0]
    else:
        print("\nFound multiple Excel files:")
        for i, file in enumerate(excel_files, 1):
            print(f"{i}. {file}")
        choice = int(input("\nWhich file contains your inspection data? Enter the number: "))
        file_path = excel_files[choice - 1]
    
    try:
        # Your code here
        pass

        # Example data
        data = np.array([2.1, 2.6, 2.4, 2.5, 2.3, 2.7, 2.0])

        # Calculate z-scores
        z_scores = stats.zscore(data)
        print(f"Z-scores: {z_scores}")

        # Create a map centered at a location
        m = folium.Map(location=[45.5236, -122.6750], zoom_start=13)

        # Add a marker
        folium.Marker(
            [45.5236, -122.6750], 
            popup='Portland, OR'
        ).add_to(m)

        # Save the map
        m.save('map.html')
        
        # Create a simple line plot
        x = [1, 2, 3, 4]
        y = [1, 4, 2, 3]

        plt.plot(x, y)
        plt.title('Sample Plot')
        plt.xlabel('X axis')
        plt.ylabel('Y axis')
        plt.show()
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()