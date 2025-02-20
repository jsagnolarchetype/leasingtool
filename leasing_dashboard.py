import streamlit as st
import pandas as pd

# Function to clean and process data
def process_data(df):
    # Delete first 6 rows and reset index
    df = df.iloc[6:].reset_index(drop=True)

    # Drop column C (third column)
    df.drop(df.columns[2], axis=1, inplace=True)

    # Rename columns (ensure correct mapping based on your dataset)
    df.columns = ["Bldg/Unit", "Floor plan", "SQFT", "Market Rent", "Amt/SQFT", "Lease Rent", 
                  "Actual Amnt/SQFT", "Name", "Move-in", "Lease Start", "Lease End", 
                  "Deposits on Hand", "Made Ready", "Effective Rent"]

    # Split 'Bldg/Unit' into 'Building' and 'Unit'
    df[['Building', 'Unit']] = df['Bldg/Unit'].astype(str).str.split('-', expand=True)

    # Convert date columns to datetime format
    df['Move-in'] = pd.to_datetime(df['Move-in'], errors='coerce')
    df['Lease Start'] = pd.to_datetime(df['Lease Start'], errors='coerce')
    df['Lease End'] = pd.to_datetime(df['Lease End'], errors='coerce')

    # Identify retained tenants (Move-In before Lease Start)
    df['Retained'] = df['Move-in'] < df['Lease Start']

    # Identify vacant or pending units based on 'Name' column
    def check_vacancy(name):
        if pd.isna(name) or 'vacant' in str(name).lower():
            return 'Vacant'
        elif 'pending' in str(name).lower():
            return 'Pending'
        return 'Occupied'

    df['Vacancy Status'] = df['Name'].apply(check_vacancy)

    return df

# Streamlit App
st.title("Lease Expiration Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload Lease Excel File", type=["xls", "xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file, sheet_name="Sheet1")  # Read only Sheet1
    df = process_data(df)  # Clean and process the data

    # Sidebar Filters
    st.sidebar.header("Filters")
    selected_building = st.sidebar.selectbox("Select Building", options=df['Building'].unique(), index=0)
    filtered_df = df[df['Building'] == selected_building]

    selected_unit = st.sidebar.selectbox("Select Unit", options=filtered_df['Unit'].unique(), index=0)
    unit_details = filtered_df[filtered_df['Unit'] == selected_unit]

    # Expiring Leases Table
    st.subheader(f"Expiring Leases in Building {selected_building}")
    st.dataframe(filtered_df[['Unit', 'Floor plan', 'SQFT', 'Lease End', 'Vacancy Status', 'Retained']].sort_values('Lease End'))

    # Selected Unit Details
    st.subheader(f"Details for Unit {selected_unit}")
    st.write(unit_details[['Floor plan', 'SQFT', 'Market Rent', 'Lease Rent', 'Lease End', 'Vacancy Status', 'Retained', 'Name']])


