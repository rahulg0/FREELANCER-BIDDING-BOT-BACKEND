import requests
from fastapi import APIRouter,Request, Header, Query, WebSocket, WebSocketDisconnect
import asyncio
from fastapi.exceptions import HTTPException
from app.config import settings
from freelancersdk.session import Session
from freelancersdk.resources.users import get_self_user_id
from freelancersdk.resources.projects import place_project_bid
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.exceptions import BidNotPlacedException
from freelancersdk.resources.projects.exceptions import ProjectsNotFoundException
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
    create_get_projects_user_details_object,
    create_get_projects_project_details_object,
)
from app.utility.proposal_maker import generate_proposal
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

router = APIRouter()

BASE_URL=settings.BASE_URL

already_bid_projects = set()

# @router.get("/search-active-projects")
# def search_active_projects( q: str = Query(...),access_token: str = Header(...)):
#     session = Session(oauth_token=access_token, url=BASE_URL)
#     query = q
#     logger.info(query)
#     logger.info(access_token)
#     logger.info(BASE_URL)
#     search_filter = create_search_projects_filter(sort_field= 'time_updated', or_search_query= True)
#     project_details = create_get_projects_project_details_object(full_description=True)
#     try:
#         p = search_projects(
#             session,
#             query=query,
#             search_filter=search_filter,
#             project_details = project_details,
#             active_only = True
#         )
#         return p

#     except ProjectsNotFoundException as e:
#         print('Error message: {}'.format(e))
#         print('Server response: {}'.format(e.error_code))
#         return None


@router.websocket("/ws/bid-on-new-jobs")
async def websocket_bid_on_new_jobs(websocket: WebSocket,q: str = Query(...), token: str = Query(...)):
    await websocket.accept()
    try:
        while True:
            search_filter = create_search_projects_filter(sort_field='time_updated', or_search_query=True)
            project_details = create_get_projects_project_details_object(full_description=True)
            session = Session(oauth_token=token, url=BASE_URL)
            projects = search_projects(session, search_filter=search_filter, project_details=project_details, active_only=True)
            
            for project in projects:
                project_id = project['id']
                if project_id not in already_bid_projects and check_amount(project['budget']['minimum'], project['budget']['exchange_rate']) :  # Check if this project is new
                    title = project['title']
                    desc = project['description']
                    preview_desc = project['preview_description']
                    amount = project['budget']['maximum']  
                    
                    bid_result = await _place_project_bid(token, project_id, desc, title, preview_desc, amount)
                    if bid_result:
                        already_bid_projects.add(project_id)  
                        await websocket.send_text(f"Bid placed on project ID: {project_id}")
            
            await asyncio.sleep(30)  
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")


async def _place_project_bid(token, project_id, desc, title, preview_desc, amount):

    url = BASE_URL
    description = await generate_proposal(title, desc, preview_desc)
    session = Session(oauth_token=token, url=url)
    my_user_id = get_self_user_id(session)
    bid_data = {
        'project_id': int(project_id),
        'bidder_id': my_user_id,
        'amount': amount,
        'period': 7,
        'milestone_percentage': 100,
        'description': str(description),
    }
    try:
        place = place_project_bid(session, **bid_data)
        if place:
            print(('Bid placed: %s' % place))
            return place
    except BidNotPlacedException as e:
        print(('Error message: %s' % e))
        print(('Error code: %s' % e.error_code))
        return None
    
async def check_amount(min_amount, exchange_rate):
    if min_amount*exchange_rate < 30:
        return False
    return True