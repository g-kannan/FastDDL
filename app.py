import streamlit as st
import duckdb
import tempfile


st.title("📊 FastDDL")
st.write("Upload XLSX or CSV files to generate DDL")
st.set_page_config(page_title="FastDDL", page_icon="📊", layout="wide")

add_filename = st.checkbox("Include filename column", value=False)
normalize_names = st.checkbox("Normalize names", value=True)

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["xlsx", "csv"])
if uploaded_file is not None:
    # Save uploaded file to temporary path
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = tmp.name

    con = duckdb.connect(database=':memory:')
    if uploaded_file.name.endswith(".csv"):
        # DuckDB can read directly from file-like objects
        query = f"create or replace view vw_csv as SELECT * FROM read_csv_auto('{tmp_path}',all_varchar=True,filename={str(add_filename).upper()},normalize_names={str(normalize_names).upper()})"
        con.sql(query)

        df = con.sql("select * from vw_csv").fetchdf()
        st.write(df.head())

        st.write("Columns:")
        columns_list = list(df.columns)
        columns_csv = ", ".join(columns_list)
        st.code(columns_csv)

        place_holder_query = f"SELECT {columns_csv} FROM vw_csv limit 100;"
        query = st.text_area("Custom query",value=place_holder_query)
        if st.button("Run Query"):
            result_df = con.sql(query).df()
            st.dataframe(result_df,hide_index=True,use_container_width=True)

