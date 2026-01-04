import streamlit as st
import pandas as pd
import snowflake.connector
import requests

# -----------------------------
# PAGE SETUP
# -----------------------------
st.set_page_config(page_title="Melanie's Smoothies", page_icon="🥤")
st.title("🥤 Customize Your Smoothie")

# -----------------------------
# SNOWFLAKE CONNECTION (DIRECT)
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
# CUSTOMER UI
# -----------------------------
name_on_order = st.text_input("Name on Smoothie")

# Fetch fruit options
cursor.execute("SELECT FRUIT_NAME FROM smoothies.public.fruit_options")
fruit_rows = cursor.fetchall()
fruit_list = [row[0] for row in fruit_rows]

ingredients = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)

# -----------------------------
# NUTRITION INFORMATION (UPDATED)
# -----------------------------
if ingredients:
    st.subheader("🥗 Nutrition Information")

    ingredients_string = ""

    for fruit_chosen in ingredients:
        ingredients_string += fruit_chosen + " "

        st.subheader(f"{fruit_chosen} - Nutrition Information")

        smoothiefruit_response = requests.get(
            f"https://my.smoothiefruit.com/api/fruit/{fruit_chosen}"
        )

        if smoothiefruit_response.status_code == 200:
            sf_df = pd.DataFrame(
                smoothiefruit_response.json(),
                index=[0]
            )
            st.dataframe(sf_df, use_container_width=True)
        else:
            st.warning(f"Nutrition data not available for {fruit_chosen}")

# -----------------------------
# SUBMIT ORDER
# -----------------------------
if name_on_order and ingredients:
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

st.divider()

# -----------------------------
# KITCHEN VIEW
# -----------------------------
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
    st.success("🎉 No pending orders!")
else:
    orders_df = pd.DataFrame(
        orders,
        columns=["INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED"]
    )
    st.dataframe(orders_df, use_container_width=True)
