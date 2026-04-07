import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import LabelEncoder
st.markdown("""
<style>
.stApp {
background-color: #0f172a ;
color: white;
}
</style>
""", unsafe_allow_html=True)
st.set_page_config(page_title="Rental Room Finder", page_icon="🏠", layout="wide")
st.markdown(
    "<h1 style='text-align: center; color: #4CAF50;'>🏠 Rental Recommendation & Mapping Systemm</h1>",
    unsafe_allow_html=True)
st.write("Find the best **Rooms, Flats or Hostels** based on your preferences.")

data = pd.read_csv("houses.csv")
# Encode categorical columns
le_gender = LabelEncoder()
le_location = LabelEncoder()

data["Gender_encoded"] = le_gender.fit_transform(data["Gender"])
data["Location_encoded"] = le_location.fit_transform(data["Location"])

X = data[["Gender_encoded", "Location_encoded", "Rent_per_month"]]

model = NearestNeighbors(n_neighbors=5)
model.fit(X)

st.sidebar.header("🔎 Find Your Room")

gender = st.sidebar.selectbox(
    "Select Gender Preference",
    data["Gender"].unique()
)

location = st.sidebar.selectbox(
    "Select Location",
    data["Location"].unique()
)
gender_encoded = le_gender.transform([gender])[0]
location_encoded = le_location.transform([location])[0]

max_rent = st.sidebar.slider(
    "Maximum Rent",
    0,
    int(data["Rent_per_month"].max()),
    5000
)
# User input for model
user_input = [[gender_encoded, location_encoded, max_rent]]

# Strong Filtering
filtered_data = data[
    (data["Gender"] == gender) &
    (data["Location"] == location)
].copy()

#Budget Filtering (soft filter)
budget_data = filtered_data[
    filtered_data["Rent_per_month"] <= max_rent
]

if len(budget_data) == 0:
    budget_data = filtered_data.copy()

#Calculate Rent Difference (IMPORTANT)
budget_data["rent_diff"] = abs(budget_data["Rent_per_month"] - max_rent)

#Sort by Closest Rent
budget_data = budget_data.sort_values(by="rent_diff")

#apply KNN
if len(budget_data) > 5:
    
    X_filtered = budget_data[["Gender_encoded", "Location_encoded", "Rent_per_month"]]

    model = NearestNeighbors(n_neighbors=5)
    model.fit(X_filtered)

    user_input = [[gender_encoded, location_encoded, max_rent]]

    distances, indices = model.kneighbors(user_input)

    recommended_rooms = budget_data.iloc[indices[0]]

else:
    # If less data
    recommended_rooms = budget_data.head(5)
# Layout using columns
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("🏡 Recommended Rooms")

    if len(recommended_rooms) > 0:
        st.success(f"{len(recommended_rooms)} rooms found based on your preference!")
        st.dataframe(recommended_rooms)
    else:
        st.warning("No rooms found for the selected options.")

with col2:
    st.subheader("📊 Quick Stats")
    st.metric("Total Listings", len(data))
    st.metric("Locations Available", data["Location"].nunique())

# Map Section
st.subheader("📍 House Locations on Map")

map_url ="https://www.google.com/maps/d/embed?mid=15_jbs_MOrikm3us61KvABfF-B_vz5Ik&ehbc=2E312F" 
components.iframe(map_url, height=500)