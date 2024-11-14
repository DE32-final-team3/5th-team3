import streamlit as st

page1 = st.Page("node_exporter.py", title="CPU Usage")
page2 = st.Page("db_exporter.py", title="DB Status")
page3 = st.Page("scale.py", title="Scale IN/OUT")

pg = st.navigation([page1, page2, page3])

pg.run()
