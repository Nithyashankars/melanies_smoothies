# -----------------------------
# IMPORTS
# -----------------------------
import streamlit as st
import pandas as pd
import snowflake.connector
import requests
import urllib3

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Melanie's Smoothies",
    page_icon="🥤",
    layout="wide"
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

st.title("🥤 Melanie's Smoothies")

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

# =====================================================
# 🍓 CUSTOMER ORDER SECTION
# =====================================================
st.header("🧑‍🍳 Order a Smoothie")

name_on_order = st.text_input("Name on Smoothie:")

# Load fruit options WITH SEARCH_ON (from your screenshot)
cursor.execute("""
    SELECT FRUIT_NAME, SEARCH_ON
    FROM smoothies.public.fruit_options
""")

fruit_df = pd.DataFrame(
    cursor.fetchall(),
    columns=["FRUIT_NAME", "SEARCH_ON"]
)

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

ingredients_string = ""

# =====================================================
# 🥗 NUTRITION INFORMATION (API WORKING)
# =====================================================
if ingredients_list:
    st.subheader("🥗 Nutrition Information")

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + " "

        search_on = fruit_df.loc[
            fruit_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.subheader(f"{fruit_chosen} - Nutrition Information")

        try:
            response = requests.get(
                f"https://my.smoothiefruit.com/api/fruit/{search_on}",
                verify=False,
                timeout=10
            )

            if response.status_code == 200:
                st.dataframe(
                    pd.DataFrame(response.json(), index=[0]),
                    width="stretch"
                )
            else:
                st.warning(f"Nutrition data not available for {fruit_chosen}")

        except requests.exceptions.RequestException:
            st.error(f"Unable to fetch nutrition data for {fruit_chosen}")

# =====================================================
# ✅ SUBMIT ORDER
# =====================================================
if name_on_order and ingredients_list:
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

# =====================================================
# 🧾 KITCHEN VIEW – CHECKBOX COMPLETION (WORKING)
# =====================================================
st.divider()
st.header("🧾 Pending Smoothie Orders")

cursor.execute("""
    SELECT ORDER_UID, INGREDIENTS, NAME_ON_ORDER, ORDER_FILLED
    FROM smoothies.public.orders
    WHERE ORDER_FILLED = FALSE
""")

orders_df = pd.DataFrame(
    cursor.fetchall(),
    columns=["ORDER_UID", "INGREDIENTS", "NAME_ON_ORDER", "ORDER_FILLED"]
)

if orders_df.empty:
    st.success("🎉 No pending orders right now!")
else:
    for _, row in orders_df.iterrows():
        c1, c2, c3 = st.columns([5, 3, 1])

        with c1:
            st.write(row["INGREDIENTS"])

        with c2:
            st.write(row["NAME_ON_ORDER"])

        with c3:
            done = st.checkbox(
                "Done",
                key=f"order_{row['ORDER_UID']}"
            )

            if done:
                cursor.execute(
                    """
                    UPDATE smoothies.public.orders
                    SET ORDER_FILLED = TRUE
                    WHERE ORDER_UID = %s
                    """,
                    (row["ORDER_UID"],)
                )
                conn.commit()
                st.success("Order completed ✔")
                st.rerun()
