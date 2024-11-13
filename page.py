import streamlit as st

page1 = st.Page("pages/node_exporter.py", title="CPU Usage")
page2 = st.Page("pages/db_exporter.py", title="DB Status")
page3 = st.Page("pages/scale.py", title="Scale IN/OUT")

pg = st.navigation([page1, page2, page3])

pg.run()
