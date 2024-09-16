import requests
from fastapi import APIRouter,Request, Header, Query
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from app.config import settings
from freelancersdk.session import Session
from freelancersdk.resources.projects.projects import search_projects
from freelancersdk.resources.projects.exceptions import \
    ProjectsNotFoundException
from freelancersdk.resources.projects.helpers import (
    create_search_projects_filter,
    create_get_projects_user_details_object,
    create_get_projects_project_details_object,
)
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

BASE_URL = settings.BASE_URL

router = APIRouter()

BASE_URL = settings.BASE_URL

@router.get("/search-active-projects")
def search_active_projects( q: str = Query(...),access_token: str = Header(...)):
    session = Session(oauth_token=access_token, url=BASE_URL)
    query = q
    logger.info(query)
    logger.info(access_token)
    logger.info(BASE_URL)
    search_filter = create_search_projects_filter(sort_field= 'time_updated', or_search_query= True)
    project_details = create_get_projects_project_details_object(full_description=True)
    try:
        p = search_projects(
            session,
            query=query,
            search_filter=search_filter,
            project_details = project_details,
            active_only = True
        )
        return p

    except ProjectsNotFoundException as e:
        print('Error message: {}'.format(e))
        print('Server response: {}'.format(e.error_code))
        return None


