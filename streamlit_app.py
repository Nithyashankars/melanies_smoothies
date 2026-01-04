# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Customer name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake session
cnx= st.connection("snowflake")
session = cnx.session()

# Fruit options
my_dataframe = session.table("smoothies.public.fruit_options").select(col("FRUIT_NAME"))
st.dataframe(my_dataframe, use_container_width=True)

# Ingredient selection
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe
)

if ingredients_list and name_on_order:

    # Build ingredients string
    ingredients_string = ""
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

    # ✅ FIXED INSERT (columns match values)
    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    st.code(my_insert_stmt, language="sql")

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
