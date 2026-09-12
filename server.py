from fastapi import FastAPI

from strawberry.fastapi import GraphQLRouter

from graphql_api import schema


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(

    title="SQLite GraphQL API",

    description=(
        "Enterprise GraphQL API "
        "for approved SQLite tables."
    ),

    version="1.0.0"
)


# ============================================================
# GRAPHQL ROUTER
# ============================================================

graphql_router = GraphQLRouter(
    schema
)


app.include_router(
    graphql_router,
    prefix="/graphql"
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def health_check():

    return {
        "status": "online",
        "service": "SQLite GraphQL API"
    }