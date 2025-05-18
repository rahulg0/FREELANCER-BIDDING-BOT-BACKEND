import json
import os
import asyncio
from fastapi import APIRouter, Header, Query
from app.config import settings
from freelancersdk.session import Session
from freelancersdk.resources.users import get_self_user_id
from freelancersdk.resources.projects import place_project_bid
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.exceptions import BidNotPlacedException
from freelancersdk.resources.projects.exceptions import ProjectsNotFoundException
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
    create_get_projects_project_details_object,
)
from app.utility.proposal_maker import generate_proposal
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

router = APIRouter()

BASE_URL = settings.BASE_URL

REQUEST_COUNTER = 0
MAX_REQUESTS = 120
RESET_TIME = 60

LOG_FILE_PATH = r"app/logs/project_bids_id.json"
BOT_SETTINGS_PATH = r"app/Bot_settings.json"
ACCOUNTS_FILE_PATH = r"app/accounts.json"

def load_bot_settings():
    logger.info(f"Loading settings from: {BOT_SETTINGS_PATH}")
    default_settings = {
        "min_avg_price":100.0,
        "countries":["us","gb","ca","au","de","fr","es","nl","se","it","ie","nz","za","dk","no","fi","be","ch","at"],
        "project_update_time":20,
        "project_types":["fixed"],
        "period":7
    }
    if os.path.exists(BOT_SETTINGS_PATH):
        with open(BOT_SETTINGS_PATH) as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                logger.info("error in json, returned default settings")
                return default_settings
    else:
        logger.info("returned default settings")
        return default_settings

settings_=load_bot_settings()

def load_logged_projects():
    """Load logged project IDs from the JSON file."""
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []

def load_accounts():
    """Load accounts and their details from the JSON file."""
    if os.path.exists(ACCOUNTS_FILE_PATH):
        with open(ACCOUNTS_FILE_PATH, "r") as file:
            try:
                return json.load(file)["accounts"]
            except json.JSONDecodeError:
                return []
    return []

def save_accounts(accounts):
    """Save updated accounts data (with bidder_id) to the JSON file."""
    with open(ACCOUNTS_FILE_PATH, "w") as file:
        json.dump({"accounts": accounts}, file)

def log_project_id(project_id,logged_proj):
    """Add a new project ID to the JSON log file."""
    if project_id not in logged_proj:
        logged_proj.append(project_id)
        with open(LOG_FILE_PATH, "w") as file:
            json.dump(logged_proj, file)

async def fetch_projects(TOKEN,q):
  try:
    session = Session(oauth_token=TOKEN, url=BASE_URL)
    search_filter = create_search_projects_filter(
        sort_field='time_updated', 
        or_search_query=True, 
        from_time=int((datetime.now() - timedelta(minutes=settings_["project_update_time"])).timestamp()),
        project_types=settings_["project_types"],
        min_avg_price=settings_["min_avg_price"],
        countries=settings_["countries"]
        )
    project_details = create_get_projects_project_details_object(full_description=True)
    projects = search_projects(session, query=q,limit=20, search_filter=search_filter, project_details=project_details, active_only=True)
    return projects
  except Exception as e:
    asyncio

async def fetch_bidder_id(token):
    """Fetch bidder_id for a given token."""
    session = Session(oauth_token=token, url=BASE_URL)
    try:
        user_id = get_self_user_id(session)
        return user_id
    except Exception as e:
        logger.error(f"Error fetching bidder_id for token: {token} - {e}")
        return None

async def update_bidder_ids():
    """Periodically fetch missing bidder_ids."""
    accounts = load_accounts()
    for account in accounts:
        if "bidder_id" not in account or account["bidder_id"] is None:
            bidder_id = await fetch_bidder_id(account["token"])
            if bidder_id:
                account["bidder_id"] = bidder_id
                save_accounts(accounts)
                logger.info(f"Bidder ID for {account['name']} fetched and saved.")
            else:
                logger.info(f"Failed to fetch bidder ID for {account['name']}. Retrying later.")
    await asyncio.sleep(60)

async def place_bid_for_token(account, project_id, desc, title, preview_desc, amount):
    """Place a bid using the provided account."""
    session = Session(oauth_token=account["token"], url=BASE_URL)
    bidder_id = account["bidder_id"]
    
    if bidder_id is None:
        logger.warning(f"Skipping bid placement for {account['name']} (no bidder_id).")
        return None
    
    logger.info(f"Placing bid for {account['name']} on project {title}.")
    description = await generate_proposal(title, desc, preview_desc)

    bid_data = {
        'project_id': int(project_id),
        'bidder_id': bidder_id,
        'amount': amount,
        'period': settings_["period"],
        'milestone_percentage': 100,
        'description': str(description),
    }
    
    try:
        return place_project_bid(session, **bid_data)
    except BidNotPlacedException as e:
        logger.error('Error message: %s', e)
        return None

@router.get("/bid-on-new-jobs")
async def bid_on_new_jobs(q: str = Query(...)):
    global REQUEST_COUNTER
    start_time = asyncio.get_event_loop().time()

    accounts = load_accounts()
    
    while True:
        if REQUEST_COUNTER < MAX_REQUESTS:
            logger.info(f"Request counter: {REQUEST_COUNTER}")
            projects_data = await fetch_projects(accounts[0]["token"],q)
            REQUEST_COUNTER += 1
            
            if projects_data:
                logger.info(f"Project count: {projects_data['total_count']}")
            projects = projects_data.get("projects", [])
            
            if projects:
              for project in projects:
                project_id = project.get("id")
                title = project.get("title")
                desc = project.get("description")
                preview_desc = project.get("preview_description")
                amount = project["budget"].get("maximum")
                curr = project["currency"]
                logged_proj = load_logged_projects()
                if project_id not in logged_proj:
                  log_project_id(project_id,logged_proj)
                  logger.info(f"project: {title}, amount {amount} {curr}.")
                  
                  for account in accounts:
                      if account["bidder_id"] is not None:
                          logger.info(f"Placing bid for {account['name']}")
                          bid_result = await place_bid_for_token(account, project_id, desc, title, preview_desc, amount)
                          if bid_result:
                              logger.info(f"Bid placed for {project_id} using {account['name']}.")
                      else:
                          logger.info(f"Skipping account {account['name']} for project {project_id} (no bidder_id).")  
                    
                await asyncio.sleep(1)
              await asyncio.sleep(10)
            else:
                await asyncio.sleep(10)
        else:
            elapsed_time = asyncio.get_event_loop().time() - start_time
            if elapsed_time < RESET_TIME:
                await asyncio.sleep(RESET_TIME - elapsed_time)

            REQUEST_COUNTER = 0
            start_time = asyncio.get_event_loop().time()

@router.on_event("startup")
async def on_startup():
    """Start background tasks."""
    asyncio.create_task(update_bidder_ids())
