from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter, BaseContext
from dotenv import load_dotenv
from .schema import schema
from .database import create_engine, get_session


class CustomContext(BaseContext):

    def __init__(self, engine, session):
        self.engine = engine
        self.session = session


def get_context(engine=Depends(create_engine), session=Depends(get_session)) -> CustomContext:
    return CustomContext(engine, session)


graphql_app = GraphQLRouter(schema, context_getter=get_context)

load_dotenv()

app = FastAPI(dependencies=[Depends(create_engine)])

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(graphql_app, prefix="/graphql")


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', debug=True)
