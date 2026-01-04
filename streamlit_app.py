# -----------------------------
# IMPORTS
# -----------------------------
import streamlit as st
import pandas as pd
import snowflake.connector
import requests

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
st.dataframe(pd.DataFrame(fruit_list, columns=["FRUIT_NAME"]), use_container_width=True)

# -----------------------------
# INGREDIENT SELECTION
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -----------------------------
# NUTRITION INFORMATION (NEW)
# -----------------------------
if ingredients_list:
    st.subheader("🥗 Nutrition Information")

    ingredients_string = ""

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} - Nutrition Information")

        smoothiefruit_response = requests.get(
            f"https://my.smoothiefruit.com/api/fruit/{fruit_chosen}"
        )

        if smoothiefruit_response.status_code == 200:
            sf_df = pd.DataFrame(
                data=smoothiefruit_response.json(),
                index=[0]
            )
            st.dataframe(sf_df, use_container_width=True)
        else:
            st.warning(f"Nutrition data not available for {fruit_chosen}")

# -----------------------------
# SUBMIT ORDER
# -----------------------------
if ingredients_list and name_on_order:
    if st.button("Submit Order"):
        cursor.execute(
            """
            INSERT INTO smoothies.public.orders (INGREDIENTS, NAME_ON_ORDER)
            VALUES (%s, %s)
            """,
            (ingredients_string.strip(), name_on_order)
        )
        conn.commit()
        st.success("✅ Your Smoothie is ordered!")

# -----------------------------
# PENDING ORDERS VIEW
# -----------------------------
st.divider()
st.title("🧾 Pending Smoothie Orders")

cursor.execute(
    """
    SELECT INGREDIENTS, NAME_ON_ORDER, ORDER_FILLED
    FROM smoothies.public.orders
    WHERE ORDER_FILLED = FALSE
    """
)

orders = cursor.fetchall()

if not orders:
    st.success("🎉 No pending orders right now!")
else:
    orders_df = pd.DataFrame(
        orders,
        columns=["INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED"]
    )
    st.dataframe(orders_df, use_container_width=True)
