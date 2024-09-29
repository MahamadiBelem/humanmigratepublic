import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient

# Function to load data from a file
def load_data(file):
    return pd.read_csv(file)

# Function to save data to MongoDB
def save_to_mongodb(df, collection):
    data_dict = df.to_dict("records")
    collection.insert_many(data_dict)

# Function to load data from MongoDB
def load_from_mongodb(collection):
    data = collection.find()
    return pd.DataFrame(list(data))

# Function to update data in MongoDB
def update_data_in_mongodb(df, collection):
    collection.drop()  # Drop the existing collection
    save_to_mongodb(df, collection)  # Save the new data

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
db = client["test_db"]
collection = db["test_migra_collection"]

# Title
st.title('Human Migration Data Visualization')

# Sidebar for menu options
st.sidebar.title('Menu')

# File uploader
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

# Load and save data
if uploaded_file is not None:
    df = load_data(uploaded_file)
    save_to_mongodb(df, collection)
    st.success("Data saved to MongoDB successfully!")
else:
    # Load default dataset for human migration with West African countries
    default_data = {
        'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
        'Country': ['Nigeria', 'Ghana', 'Senegal', 'Ivory Coast', 'Burkina Faso', 'Mali', 'Niger', 'Guinea', 'Togo'],
        'Migrants': [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000],
        'Emigrants': [500, 700, 800, 1200, 1500, 1800, 2000, 2200, 2500]
    }
    df = pd.DataFrame(default_data)

# Option to update data in MongoDB
if st.sidebar.button("Update MongoDB Data"):
    if uploaded_file is not None:
        update_data_in_mongodb(df, collection)
        st.success("MongoDB data updated successfully!")
    else:
        st.warning("Please upload a file to update the data.")

# Data source selection
st.sidebar.title('Data Source')
data_source = st.sidebar.radio(
    "Choose data source for visualization:",
    ('Current Data', 'MongoDB Data')
)

# Load data based on the selected data source
if data_source == 'MongoDB Data':
    viz_df = load_from_mongodb(collection)
    if viz_df.empty:
        st.warning("No data found in MongoDB. Please upload and save data first.")
        viz_df = df  # Fallback to current data to prevent errors
    else:
        st.success("Loaded data from MongoDB.")
else:
    viz_df = df  # Current data (uploaded or default)

# Option to show data from MongoDB
if data_source == 'MongoDB Data' and not viz_df.empty:
    if st.sidebar.checkbox('Show MongoDB Data'):
        st.write('Data from MongoDB')
        st.write(viz_df)

# Sidebar for selecting visualization type
st.sidebar.title('Select Visualization Type')
visualization_type = st.sidebar.selectbox(
    'Choose a chart type:', 
    ['Bar Chart', 'Line Chart', 'Area Chart', 'Scatter Plot', 'Histogram', 'Pie Chart', 'Box Plot', 'Heatmap']
)

# Visualizations
if not viz_df.empty:
    if visualization_type == 'Bar Chart':
        st.bar_chart(viz_df.set_index('Year')[['Migrants', 'Emigrants']])

    elif visualization_type == 'Line Chart':
        st.line_chart(viz_df.set_index('Year')[['Migrants', 'Emigrants']])

    elif visualization_type == 'Area Chart':
        st.area_chart(viz_df.set_index('Year')[['Migrants', 'Emigrants']])

    elif visualization_type == 'Scatter Plot':
        st.write('Scatter Plot')
        fig, ax = plt.subplots()
        ax.scatter(viz_df['Year'], viz_df['Migrants'], label='Migrants')
        ax.scatter(viz_df['Year'], viz_df['Emigrants'], label='Emigrants')
        ax.legend()
        st.pyplot(fig)

    elif visualization_type == 'Histogram':
        st.write('Histogram')
        fig, ax = plt.subplots()
        ax.hist(viz_df['Migrants'], bins=10, alpha=0.5, label='Migrants')
        ax.hist(viz_df['Emigrants'], bins=10, alpha=0.5, label='Emigrants')
        ax.legend()
        st.pyplot(fig)

    elif visualization_type == 'Pie Chart':
        st.write('Pie Chart')
        fig, ax = plt.subplots()
        ax.pie(viz_df['Migrants'], labels=viz_df['Country'], autopct='%1.1f%%')
        st.pyplot(fig)

    elif visualization_type == 'Box Plot':
        st.write('Box Plot')
        fig, ax = plt.subplots()
        sns.boxplot(data=viz_df[['Migrants', 'Emigrants']], ax=ax)
        st.pyplot(fig)

    elif visualization_type == 'Heatmap':
        st.write('Heatmap')
        fig, ax = plt.subplots()
        sns.heatmap(viz_df[['Migrants', 'Emigrants']].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    # Display the dataframe
    st.write('Human Migration Data')
    st.write(viz_df)
else:
    st.warning("No data available for visualization.")


def test0():
    # Function to load data from a file
    def load_data(file):
        return pd.read_csv(file)

    # Function to save data to MongoDB
    def save_to_mongodb(df, collection):
        data_dict = df.to_dict("records")
        collection.insert_many(data_dict)

    # Function to load data from MongoDB
    def load_from_mongodb(collection):
        data = collection.find()
        return pd.DataFrame(list(data))

    # Function to update data in MongoDB
    def update_data_in_mongodb(df, collection):
        collection.drop()  # Drop the existing collection
        save_to_mongodb(df, collection)  # Save the new data

    # MongoDB setup
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
    db = client["test_db"]
    collection = db["test_migra_collection"]

    # Title
    st.title('Human Migration Data Visualization')

    # Sidebar for menu options
    st.sidebar.title('Menu')

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

    # Load and save data
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        save_to_mongodb(df, collection)
        st.success("Data saved to MongoDB successfully!")
    else:
        # Load default dataset for human migration with West African countries
        default_data = {
            'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
            'Country': ['Nigeria', 'Ghana', 'Senegal', 'Ivory Coast', 'Burkina Faso', 'Mali', 'Niger', 'Guinea', 'Togo'],
            'Migrants': [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000],
            'Emigrants': [500, 700, 800, 1200, 1500, 1800, 2000, 2200, 2500]
        }
        df = pd.DataFrame(default_data)

    # Option to update data in MongoDB
    if st.sidebar.button("Update MongoDB Data"):
        if uploaded_file is not None:
            update_data_in_mongodb(df, collection)
            st.success("MongoDB data updated successfully!")
        else:
            st.warning("Please upload a file to update the data.")

    # Option to show data from MongoDB
    if st.sidebar.checkbox('Show MongoDB Data'):
        mongo_df = load_from_mongodb(collection)
        if not mongo_df.empty:
            st.write('Data from MongoDB')
            st.write(mongo_df)
        else:
            st.warning("No data found in MongoDB.")

    # Visualization options
    st.sidebar.title('Select Visualization Type')
    visualization_type = st.sidebar.selectbox(
        'Choose a chart type:', 
        ['Bar Chart', 'Line Chart', 'Area Chart', 'Scatter Plot', 'Histogram', 'Pie Chart', 'Box Plot', 'Heatmap']
    )

    # Visualizations
    if visualization_type == 'Bar Chart':
        st.bar_chart(df.set_index('Year')[['Migrants', 'Emigrants']])

    elif visualization_type == 'Line Chart':
        st.line_chart(df.set_index('Year')[['Migrants', 'Emigrants']])

    elif visualization_type == 'Area Chart':
        st.area_chart(df.set_index('Year')[['Migrants', 'Emigrants']])

    elif visualization_type == 'Scatter Plot':
        st.write('Scatter Plot')
        fig, ax = plt.subplots()
        ax.scatter(df['Year'], df['Migrants'], label='Migrants')
        ax.scatter(df['Year'], df['Emigrants'], label='Emigrants')
        ax.legend()
        st.pyplot(fig)

    elif visualization_type == 'Histogram':
        st.write('Histogram')
        fig, ax = plt.subplots()
        ax.hist(df['Migrants'], bins=10, alpha=0.5, label='Migrants')
        ax.hist(df['Emigrants'], bins=10, alpha=0.5, label='Emigrants')
        ax.legend()
        st.pyplot(fig)

    elif visualization_type == 'Pie Chart':
        st.write('Pie Chart')
        fig, ax = plt.subplots()
        ax.pie(df['Migrants'], labels=df['Country'], autopct='%1.1f%%')
        st.pyplot(fig)

    elif visualization_type == 'Box Plot':
        st.write('Box Plot')
        fig, ax = plt.subplots()
        sns.boxplot(data=df[['Migrants', 'Emigrants']], ax=ax)
        st.pyplot(fig)

    elif visualization_type == 'Heatmap':
        st.write('Heatmap')
        fig, ax = plt.subplots()
        sns.heatmap(df[['Migrants', 'Emigrants']].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    # Display the dataframe
    st.write('Human Migration Data')
    st.write(df)










def test1():
    import streamlit as st
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from pymongo import MongoClient

    # Function to load data
    def load_data(file):
        df = pd.read_csv(file)
        return df

    # Function to save data to MongoDB
    def save_to_mongodb(df, collection):
        data_dict = df.to_dict("records")
        collection.delete_many({})  # Clear existing data
        collection.insert_many(data_dict)

    # Function to load data from MongoDB
    def load_from_mongodb(collection):
        data = collection.find()
        df = pd.DataFrame(list(data))
        return df

    # MongoDB setup
    client = MongoClient("mongodb://localhost:27017/")  # Replace with your MongoDB connection string
    db = client["test_db"]
    collection = db["test_migra_collection"]

    # Title
    st.title('Human Migration Data Visualization')

    # Sidebar for selecting visualization type
    st.sidebar.title('Select Visualization Type')
    visualization_type = st.sidebar.selectbox(
        'Choose a chart type:', 
        ['Bar Chart', 'Line Chart', 'Area Chart', 'Scatter Plot', 'Histogram', 'Pie Chart', 'Box Plot', 'Heatmap']
    )

    # File uploader
    uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])

    # Button to update data
    update_data = st.sidebar.button("Update Data")

    # Load or update data
    if uploaded_file is not None:
        df = load_data(uploaded_file)
        if update_data:
            save_to_mongodb(df, collection)
            st.success("Data updated in MongoDB successfully!")
    else:
        # Default dataset for human migration with West African countries
        data = {
            'Year': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
            'Country': ['Nigeria', 'Ghana', 'Senegal', 'Ivory Coast', 'Burkina Faso', 'Mali', 'Niger', 'Guinea', 'Togo'],
            'Migrants': [1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000],
            'Emigrants': [500, 700, 800, 1200, 1500, 1800, 2000, 2200, 2500]
        }
        df = pd.DataFrame(data)

    # Display data from MongoDB
    if st.sidebar.checkbox('Show MongoDB Data'):
        mongo_df = load_from_mongodb(collection)
        if not mongo_df.empty:
            st.write('Data from MongoDB')
            st.write(mongo_df)
        else:
            st.warning("No data found in MongoDB.")

    # Bar Chart
    if visualization_type == 'Bar Chart':
        st.bar_chart(df.set_index('Year')[['Migrants', 'Emigrants']])

    # Line Chart
    elif visualization_type == 'Line Chart':
        st.line_chart(df.set_index('Year')[['Migrants', 'Emigrants']])

    # Area Chart
    elif visualization_type == 'Area Chart':
        st.area_chart(df.set_index('Year')[['Migrants', 'Emigrants']])

    # Scatter Plot
    elif visualization_type == 'Scatter Plot':
        st.write('Scatter Plot')
        fig, ax = plt.subplots()
        ax.scatter(df['Year'], df['Migrants'], label='Migrants')
        ax.scatter(df['Year'], df['Emigrants'], label='Emigrants')
        ax.legend()
        st.pyplot(fig)

    # Histogram
    elif visualization_type == 'Histogram':
        st.write('Histogram')
        fig, ax = plt.subplots()
        ax.hist(df['Migrants'], bins=10, alpha=0.5, label='Migrants')
        ax.hist(df['Emigrants'], bins=10, alpha=0.5, label='Emigrants')
        ax.legend()
        st.pyplot(fig)

    # Pie Chart
    elif visualization_type == 'Pie Chart':
        st.write('Pie Chart')
        fig, ax = plt.subplots()
        ax.pie(df['Migrants'], labels=df['Country'], autopct='%1.1f%%')
        st.pyplot(fig)

    # Box Plot
    elif visualization_type == 'Box Plot':
        st.write('Box Plot')
        fig, ax = plt.subplots()
        sns.boxplot(data=df[['Migrants', 'Emigrants']], ax=ax)
        st.pyplot(fig)

    # Heatmap
    elif visualization_type == 'Heatmap':
        st.write('Heatmap')
        fig, ax = plt.subplots()
        sns.heatmap(df[['Migrants', 'Emigrants']].corr(), annot=True, cmap='coolwarm', ax=ax)
        st.pyplot(fig)

    # Display the dataframe
    st.write('Human Migration Data')
    st.write(df)
