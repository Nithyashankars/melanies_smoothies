# -----------------------------
# IMPORTS
# -----------------------------
import streamlit as st
import pandas as pd
import snowflake.connector
import requests
import urllib3

# -----------------------------
# DISABLE SSL WARNINGS
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
# LOAD FRUIT OPTIONS (WITH SEARCH_ON)
# -----------------------------
cursor.execute("""
    SELECT FRUIT_NAME, SEARCH_ON
    FROM smoothies.public.fruit_options
""")

rows = cursor.fetchall()

pd_df = pd.DataFrame(
    rows,
    columns=["FRUIT_NAME", "SEARCH_ON"]
)

st.subheader("Available Fruits")
st.dataframe(pd_df[["FRUIT_NAME"]], width="stretch")

# -----------------------------
# INGREDIENT SELECTION (IMAGE LOGIC)
# -----------------------------
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# -----------------------------
# NUTRITION INFORMATION (FROM IMAGE)
# -----------------------------
ingredients_string = ""

if ingredients_list:
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        # 🔑 EXACT IMAGE LOGIC
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write(
            "The search value for",
            fruit_chosen,
            "is",
            search_on
        )

        st.subheader(fruit_chosen + " Nutrition Information")

        try:
            fruityvice_response = requests.get(
                "https://my.smoothiefruit.com/api/fruit/" + search_on,
                verify=False,
                timeout=10
            )

            if fruityvice_response.status_code == 200:
                st.dataframe(
                    pd.DataFrame(fruityvice_response.json(), index=[0]),
                    width="stretch"
                )
            else:
                st.warning("Nutrition data not available")

        except requests.exceptions.RequestException:
            st.error("Unable to fetch nutrition data")

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

cursor.execute("""
    SELECT INGREDIENTS, NAME_ON_ORDER, ORDER_FILLED
    FROM smoothies.public.orders
    WHERE ORDER_FILLED = FALSE
""")

orders = cursor.fetchall()

if not orders:
    st.success("🎉 No pending orders right now!")
else:
    orders_df = pd.DataFrame(
        orders,
        columns=["INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED"]
    )
    st.dataframe(orders_df, width="stretch")
