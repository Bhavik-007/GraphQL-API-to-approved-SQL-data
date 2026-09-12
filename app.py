import json
import requests
import pandas as pd
import streamlit as st
import tomllib
from pathlib import Path


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Enterprise Data Explorer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# CONFIGURATION
# ============================================================

GRAPHQL_URL = "http://127.0.0.1:8000/graphql"


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>

    /* Main page */
    .block-container {
        padding-top: 2rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        padding-bottom: 2rem;
        max-width: 100%;
    }




    /* Buttons */
    .stButton button {
        border-radius: 7px;
        min-height: 40px;
    }

    /* Data grid */
    div[data-testid="stDataFrame"] {
        border: 1px solid #e5e7eb;
        border-radius: 8px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# GRAPHQL REQUEST FUNCTION
# ============================================================

def graphql_request(
    query,
    variables=None
):

    try:

        response = requests.post(

            GRAPHQL_URL,

            json={
                "query": query,
                "variables": variables or {}
            },

            timeout=60
        )

        response.raise_for_status()

        result = response.json()

        if "errors" in result:

            error_message = "\n".join(
                error.get(
                    "message",
                    "Unknown GraphQL error"
                )
                for error in result["errors"]
            )

            st.error(
                f"GraphQL Error: {error_message}"
            )

            return None

        return result.get("data")


    except requests.exceptions.ConnectionError:

        st.error(
            "Unable to connect to GraphQL API.\n\n"
            "Make sure FastAPI is running:\n"
            "uvicorn server:app --reload --port 8000"
        )

        return None


    except requests.exceptions.Timeout:

        st.error(
            "GraphQL request timed out."
        )

        return None


    except Exception as e:

        st.error(
            f"Unable to load data: {str(e)}"
        )

        return None


# ============================================================
# GET AVAILABLE TABLES
# ============================================================

def get_tables():

    # UI ONLY:
    # Read the approved table names directly from config.toml.
    # No GraphQL schema changes are required.

    config_path = Path(__file__).parent / "config.toml"

    try:

        with open(config_path, "rb") as file:
            config = tomllib.load(file)

        tables = config["graphql"]["allowed_tables"]

        return [
            table.strip()
            for table in tables
            if table and table.strip()
        ]

    except Exception as e:

        st.error(
            f"Unable to read config.toml: {str(e)}"
        )

        return []


# ============================================================
# GET TABLE DATA
#
# IMPORTANT:
# This matches your CURRENT GraphQL schema.
#
# TableData contains:
#   tableName
#   columns
#   rows
#
# NOT:
#   data
# ============================================================

def get_table_data(
    table_name,
    limit
):

    query = """

    query GetTableData(
        $tableName: String!,
        $limit: Int!
    ) {

        tableData(
            tableName: $tableName,
            limit: $limit
        ) {

            tableName

            columns {
                name
                dataType
            }

            rows

        }

    }

    """

    result = graphql_request(

        query,

        {
            "tableName": table_name,
            "limit": limit
        }
    )


    if not result:

        return pd.DataFrame(), []


    table_data = result["tableData"]


    # --------------------------------------------------------
    # Get column metadata
    # --------------------------------------------------------

    columns = table_data["columns"]


    column_names = [
        column["name"]
        for column in columns
    ]


    # --------------------------------------------------------
    # Get rows
    # --------------------------------------------------------

    raw_rows = table_data["rows"]


    # --------------------------------------------------------
    # IMPORTANT:
    #
    # Your GraphQL API returns rows as JSON objects.
    # Handle both dictionary and JSON-string formats.
    # --------------------------------------------------------

    processed_rows = []


    for row in raw_rows:

        if isinstance(row, dict):

            processed_rows.append(
                row
            )

        elif isinstance(row, str):

            try:

                processed_rows.append(
                    json.loads(row)
                )

            except json.JSONDecodeError:

                processed_rows.append(
                    {}
                )


    # --------------------------------------------------------
    # Create dataframe
    # --------------------------------------------------------

    df = pd.DataFrame(
        processed_rows
    )


    # --------------------------------------------------------
    # Make sure all GraphQL columns exist
    # --------------------------------------------------------

    for column in column_names:

        if column not in df.columns:

            df[column] = None


    # --------------------------------------------------------
    # Preserve database column order
    # --------------------------------------------------------

    df = df[
        column_names
    ]


    return df, columns


# ============================================================
# APPLICATION HEADER
# ============================================================

st.title("Enterprise Data Explorer")

st.caption(
    "GraphQL-powered access to approved SQLite data"
)


# ============================================================
# LOAD TABLE LIST
# ============================================================

tables = get_tables()


if not tables:

    st.error(
        "No approved tables found from GraphQL API."
    )

    st.stop()


# ============================================================
# DATA SELECTION
# ============================================================

st.subheader("Data Selection")


table_col, row_col, load_col, reset_col = st.columns(
    [4, 2, 1.4, 1.2]
)


with table_col:

    selected_table = st.selectbox(
        "Select Table",
        options=tables
    )


with row_col:

    row_options = [
        100,
        500,
        1000,
        5000,
        10000,
        0
    ]

    selected_limit = st.selectbox(

        "Records",

        options=row_options,

        index=0,

        format_func=lambda x:
            "Unlimited"
            if x == 0
            else f"{x:,}"
    )

    st.caption(
        "Unlimited uses the existing GraphQL API limit setting."
    )


with load_col:

    st.write("")

    load_clicked = st.button(
        "Load Table",
        type="primary",
        use_container_width=True
    )


with reset_col:

    st.write("")

    reset_clicked = st.button(
        "Reset",
        use_container_width=True
    )


# ============================================================
# RESET
# ============================================================

if reset_clicked:

    for key in [
        "loaded_table",
        "loaded_limit",
        "loaded_df",
        "loaded_columns"
    ]:

        st.session_state.pop(
            key,
            None
        )

    st.rerun()


# ============================================================
# LOAD DATA
# ============================================================

if load_clicked:

    with st.spinner(
        f"Loading {selected_table}..."
    ):

        loaded_df, loaded_columns = (
            get_table_data(
                selected_table,
                selected_limit
            )
        )


    if loaded_df is not None:

        st.session_state.loaded_table = (
            selected_table
        )

        st.session_state.loaded_limit = (
            selected_limit
        )

        st.session_state.loaded_df = (
            loaded_df
        )

        st.session_state.loaded_columns = (
            loaded_columns
        )


# ============================================================
# CHECK DATA
# ============================================================

if st.session_state.get("loaded_df") is None:

    st.info(
        "Select a table and click "
        "'Load Table' to begin."
    )

    st.stop()


# ============================================================
# GET LOADED DATA
# ============================================================

df = st.session_state.loaded_df.copy()

loaded_table = (
    st.session_state.loaded_table
)

loaded_limit = (
    st.session_state.loaded_limit
)


# ============================================================
# EMPTY DATA
# ============================================================

if df.empty:

    st.warning(
        f"No records found in {loaded_table}."
    )

    st.stop()


# ============================================================
# DATA TYPE DETECTION
# ============================================================

for column in df.columns:

    if df[column].dtype == "object":

        numeric_values = pd.to_numeric(
            df[column],
            errors="coerce"
        )


        if (
            numeric_values.notna().mean()
            >= 0.95
        ):

            df[column] = numeric_values


# ============================================================
# OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">Overview</div>',
    unsafe_allow_html=True
)

card1, card2, card3, card4 = st.columns(4)

with card1:
    st.metric(
        "Table",
        loaded_table
    )

with card2:
    st.metric(
        "Loaded Records",
        f"{len(df):,}"
    )

with card3:
    st.metric(
        "Columns",
        f"{len(df.columns):,}"
    )

with card4:
    limit_text = (
        "Unlimited"
        if loaded_limit == 0
        else f"{loaded_limit:,}"
    )

    st.metric(
        "Load Limit",
        limit_text
    )


# ============================================================
# COLUMN SELECTION
#
# UI ONLY:
# Select which existing columns are shown in the grid/CSV.
# No row/data filters are applied.
# ============================================================

st.subheader("Columns")

available_columns = list(df.columns)

selected_columns = st.multiselect(
    "Select columns",
    options=available_columns,
    default=available_columns,
    key=f"column_selector_{loaded_table}"
)

if selected_columns:

    display_df = df[selected_columns]

else:

    display_df = pd.DataFrame()


# ============================================================
# RESULT INFORMATION
# ============================================================

st.divider()


result_col, download_col = st.columns(
    [5, 1]
)


with result_col:

    st.caption(
        f"Showing {len(display_df):,} "
        f"of {len(df):,} loaded records"
    )


with download_col:

    csv_data = (
        display_df
        .to_csv(index=False)
        .encode("utf-8")
    )


    st.download_button(

        "Download CSV",

        data=csv_data,

        file_name=(
            f"{loaded_table}.csv"
        ),

        mime="text/csv",

        use_container_width=True
    )


# ============================================================
# DATA TABLE
# ============================================================

st.subheader("Data")


st.dataframe(

    display_df,

    use_container_width=True,

    height=620,

    hide_index=True
)