# -----------------------------
# IMPORTS
# -----------------------------
import streamlit as st
import pandas as pd
import snowflake.connector
import requests
import urllib3

# -----------------------------
# DISABLE SSL WARNINGS (Streamlit Cloud)
# -----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Melanie's Smoothies", page_icon="🥤")

st.title("🥤 Customize Your Smoothie")
st.write("Choose the fruits you want in your custom Smoothie!")

# -----------------------------
# SNOWFLAKE CONNECTION
# -----------------------------
conn = snowflake.connector.connect(
    account=st.secrets["snowflake"]["account"],
    user=st.secrets["snowflake"]["user"],
    password=st.secrets["snowflake"]["password"],
    role=st.secrets["snowflake"]["role"],
    warehouse=st.secrets["snowflake"]["warehouse"],
    database=st.secrets["snowflake"]["database"],
    schema=st.secrets["snowflake"]["schema"],
)

cursor = conn.cursor()

# -----------------------------
# CUSTOMER NAME
# -----------------------------
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# -----------------------------
# FETCH FRUIT OPTIONS
# -----------------------------
cursor.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruit_rows = cursor.fetchall()
fruit_list = [row[0] for row in fruit_rows]

st.subheader("Available Fruits")
st.dataframe(
    pd.DataFrame(fruit_list, columns=["FRUIT_NAME"]),
    width="stretch"
)

# -----------------------------
# INGREDIENT SELECTION
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -----------------------------
# NUTRITION INFORMATION (FIXED)
# -----------------------------
ingredients_string = ""

if ingredients_list:
    st.subheader("🥗 Nutrition
