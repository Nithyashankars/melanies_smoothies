import streamlit as st

st.title("Snowflake Connection Test")

cnx = st.connection("snowflake")

df = cnx.query("SELECT CURRENT_ACCOUNT(), CURRENT_USER()")

st.dataframe(df)

st.success("Connection successful!")
