from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from careai.apps.inbound_email_processor.routes import router as inbound_email_router
from careai.apps.outbound_call.routes import router as outbound_call_router
from careai.utils import fetch_config

app = FastAPI()

# Read the yaml file
config = fetch_config()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# Include the inbound email processor router with a prefix
app.include_router(
    inbound_email_router, prefix="/inbound-emails", tags=["inbound-emails"]
)

# Include the outbound call router with a prefix
app.include_router(
    outbound_call_router, prefix="/outbound_call", tags=["outbound-call"]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
