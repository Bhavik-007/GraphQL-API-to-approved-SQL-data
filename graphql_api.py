import strawberry

from typing import List

from strawberry.scalars import JSON

from database import (
    get_allowed_tables,
    get_table_data,
    get_table_columns
)


# ============================================================
# GRAPHQL TYPES
# ============================================================

@strawberry.type
class ColumnInfo:

    name: str

    data_type: str


@strawberry.type
class TableInfo:

    name: str


@strawberry.type
class TableData:

    table_name: str

    columns: List[ColumnInfo]

    rows: List[JSON]


# ============================================================
# GRAPHQL QUERY
# ============================================================

@strawberry.type
class Query:

    # --------------------------------------------------------
    # GET AVAILABLE TABLES
    # --------------------------------------------------------

    @strawberry.field
    def tables(self) -> List[TableInfo]:

        return [
            TableInfo(
                name=table
            )
            for table in get_allowed_tables()
        ]


    # --------------------------------------------------------
    # GET TABLE DATA
    # --------------------------------------------------------

    @strawberry.field
    def table_data(
        self,
        table_name: str,
        limit: int = 1000
    ) -> TableData:

        columns_raw, rows = get_table_data(
            table_name,
            limit
        )

        column_metadata = (
            get_table_columns(
                table_name
            )
        )

        columns = [
            ColumnInfo(
                name=item["name"],
                data_type=item["type"] or "TEXT"
            )
            for item in column_metadata
        ]

        return TableData(

            table_name=table_name,

            columns=columns,

            rows=rows
        )


# ============================================================
# GRAPHQL SCHEMA
# ============================================================

schema = strawberry.Schema(
    query=Query
)