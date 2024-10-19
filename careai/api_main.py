from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from careai.apps.inbound_email_processor.beans import EmailStatus, EmailUpdate, Email
from careai.apps.inbound_email_processor.data_store.email import fetch_emails, update_email, fetch_email_by_id
from careai.apps.inbound_email_processor.domain.email import email_medical_report
from careai.utils import fetch_config

from careai.apps.inbound_email_processor.routes import router as inbound_email_router
from careai.apps.outbound_call.routes import router as outbound_call_router

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
app.include_router(inbound_email_router, prefix="/inbound-emails", tags=["inbound-emails"])

# Include the outbound call router with a prefix
app.include_router(outbound_call_router, prefix="/outbound_call", tags=["outbound-call"])

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
