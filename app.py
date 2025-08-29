import streamlit as st
import duckdb
import tempfile
import re


st.title("📊 FastDDL")
st.write("Upload XLSX or CSV files to generate DDL")
st.set_page_config(page_title="FastDDL", page_icon="📊", layout="wide")


def col_normalizer(columns_list):
    # replace special characters, spaces and non-alphanumeric characters with _
    pattern = re.compile(r'[^a-zA-Z0-9_]')
    for i, col in enumerate(columns_list):
        col = pattern.sub('_', col).lower()
        col = col.replace(" ", "_")
        if col.endswith("_"):
            col = col[:-1]
        columns_list[i] = col
    return columns_list
    

add_filename = st.checkbox("Include filename column", value=False)
normalize_names = st.checkbox("Normalize names", value=False)
quote_columns = st.checkbox("Quote columns", value=False)

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
        query = f"create or replace view vw_csv as SELECT * FROM read_csv_auto('{tmp_path}',header=True,all_varchar=True,filename={str(add_filename).upper()},normalize_names={str(normalize_names).upper()})"
        con.sql(query)

        df = con.sql("select * from vw_csv").fetchdf()
        st.write(df.head())

        st.write("Columns:")
        columns_list = list(df.columns)
        # normalized_column_list = col_normalizer(columns_list)
        # normalized_column_csv = ", ".join(normalized_column_list)
        if quote_columns:
            quoted_columns = [f'"{c}"' for c in columns_list]
            columns_csv = ", ".join(quoted_columns)
        else:
            columns_csv = ", ".join(columns_list)
        st.code(columns_csv)

        place_holder_query = f"SELECT {columns_csv} FROM vw_csv limit 100;"
        query = st.text_area("Custom query",value=place_holder_query)
        if st.button("Run Query"):
            result_df = con.sql(query).df()
            st.dataframe(result_df,hide_index=True,use_container_width=True)

    elif uploaded_file.name.endswith(".xlsx"):
        query = f"create or replace view vw_xlsx as SELECT * FROM read_xlsx('{tmp_path}',all_varchar=True)"
        con.sql(query)

        df = con.sql("select * from vw_xlsx").fetchdf()
        st.write(df.head())

        st.write("Columns:")
        columns_list = list(df.columns)
        if quote_columns:
            quoted_columns = [f'"{c}"' for c in columns_list]
            columns_csv = ", ".join(quoted_columns)
        else:
            columns_csv = ", ".join(columns_list)
        st.code(columns_csv)

        place_holder_query = f"SELECT {columns_csv} FROM vw_xlsx limit 100;"
        query = st.text_area("Custom query",value=place_holder_query)
        if st.button("Run Query"):
            result_df = con.sql(query).df()
            st.dataframe(result_df,hide_index=True,use_container_width=True)