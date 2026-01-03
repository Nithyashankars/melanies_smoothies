# Import python packages
import streamlit as st
import pandas as pd

# Write directly to the app
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

# Customer name
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake connection (Streamlit Cloud compatible)
cnx = st.connection("snowflake")

# Get fruit options using SQL (returns Pandas DataFrame)
fruit_df = cnx.query(
    "SELECT FRUIT_NAME FROM smoothies.public.fruit_options",
    ttl=600
)

st.dataframe(fruit_df, use_container_width=True)

# Ingredient selection (use list, not dataframe)
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist()
)

if ingredients_list and name_on_order:

    ingredients_string = " ".join(ingredients_list)

    insert_sql = """
        INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
        VALUES (%s, %s)
    """

    st.code(
        insert_sql.replace("%s", "'{}'").format(ingredients_string, name_on_order),
        language="sql"
    )

    if st.button("Submit Order"):
        cnx.execute(insert_sql, (ingredients_string, name_on_order))
        st.success("Your Smoothie is ordered! ✅")
