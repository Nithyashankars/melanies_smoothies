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


# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Pending Smoothie Orders :cup_with_straw:")
st.write("Orders that need to be filled.")

session = get_active_session()

my_dataframe = (
    session.table("smoothies.public.orders")
    .filter(col("ORDER_FILLED") == False)
)

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)

    submitted = st.button("Submit")

    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)

        try:
            og_dataset.merge(
                edited_dataset,
                (og_dataset["order_uid"] == edited_dataset["order_uid"]),
                [
                    when_matched().update(
                        {"ORDER_FILLED": edited_dataset["ORDER_FILLED"]}
                    )
                ]
            )
            st.success("Order(s) Updated!", icon="👍")
        except:
            st.write("Something went wrong.")
else:
    st.success("There are no pending orders right now.", icon="👍")




