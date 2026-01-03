import streamlit as st
import pandas as pd

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Melanie's Smoothies", page_icon="🥤", layout="centered")

# -----------------------------
# SNOWFLAKE CONNECTION
# -----------------------------
cnx = st.connection("snowflake")

# -----------------------------
# CUSTOMER ORDER UI
# -----------------------------
st.title("🥤 Customize Your Smoothie")
st.write("Choose the fruits you want in your custom smoothie!")

name_on_order = st.text_input("Name on Smoothie")

# Fetch fruit options
fruit_df = cnx.query(
    "SELECT FRUIT_NAME FROM smoothies.public.fruit_options",
    ttl=600
)

st.subheader("Available Fruits")
st.dataframe(fruit_df, use_container_width=True)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list and name_on_order:
    ingredients_string = " ".join(ingredients_list)

    if st.button("Submit Order"):
        insert_sql = """
            INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
            VALUES (%s, %s)
        """
        cnx.execute(insert_sql, (ingredients_string, name_on_order))
        st.success("✅ Your Smoothie is ordered!")

st.divider()

# -----------------------------
# KITCHEN VIEW
# -----------------------------
st.title("🧾 Pending Smoothie Orders")
st.write("Orders that still need to be filled")

orders_df = cnx.query(
    """
    SELECT INGREDIENTS, NAME_ON_ORDER, ORDER_FILLED
    FROM smoothies.public.orders
    WHERE ORDER_FILLED = FALSE
    """,
    ttl=60
)

if orders_df.empty:
    st.success("🎉 No pending orders right now!")
else:
    st.dataframe(orders_df, use_container_width=True)
