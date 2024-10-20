import logging
import uuid

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from datetime import datetime
from careai.lib.clients.vapi import create_vapi_call

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter()


class DebtCallRequest(BaseModel):
    name: str
    debt_amount: str
    debt_reason: str
    due_date: str
    clinic_name: str
    penalty_detail: str
    mobile_number: str


@router.post("/debt_call")
async def debt_call(request: DebtCallRequest):
    

    # Get today's date as a string in the format "Month Day, Year"
    today_date = datetime.now().strftime("%B %d, %Y")
    
    # Construct the message for the call
    message = f"""You are an AI agent who is responsible for collecting debt from user. Remember that today's date is f{today_date}.
    start by saying, "Hello am I speaking with f{request.name}?" If they are not the one speaking then
    ask them whether you can speak with f{request.name}
    and wait till they hand over the call to f{request.name} else if they are not available 
    then say you will call back later to speak with f{request.name}.
    Inform that you are Clara, an AI agent and you are calling regarding an unpaid debt from f{request.clinic_name}. 
    Tell the amount owed is f{request.debt_amount}  dollars, 
    and say that due date is f{request.due_date}. use below details to compute penalty and provide it to them as well.
    The debt is for f{request.debt_reason}. 
    Inform that that not paying the debt will result in penality and details of penality is f{request.penalty_detail}. 
    Ask if they want to make payment now. If yes then ask if they want to make a payment via link or wire transfer.
    If they would like to make a payment, then say that we can send a link via message to your registered mobile number shortly. 
    if they want wire transfer, we can message the instructions as well. 
    If the person wants more time or want to discuss a waiver tell that you will arrange for an agent to call you back. 
also if they are only delayed by a day or two from due date say that we can provide them with one time waiver and if they are interested send them link and tell they need to pay it within a day to use the waiver.
    At the end Thank them for their attention to this matter."""

    # Log the system message
    logger.info(f"System message for debt call to {request.name}:")
    logger.info(message)
    # Make the call using the VAPI client
    try:
        create_vapi_call(
            request.mobile_number, message, f"Hello am I speaking with {request.name}?"
        )
        return Response(status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class CallRequest(BaseModel):
    patient_name: str
    call_reason: str
    patient_phone_number: str


@router.post("/initiate_call")
async def initiate_call(call_request: CallRequest):
    logger.info(f"Received call request for patient: {call_request.patient_name}")
    logger.info(f"Call reason: {call_request.call_reason}")
    logger.info(f"Patient phone number: {call_request.patient_phone_number}")
    # Implement the logic to initiate the call here
    # For example, you might use a third-party service or API
    # Simulate a successful call initiation
    call_id = str(uuid.uuid4())
    return {"message": "Call initiated successfully", "call_id": call_id}
