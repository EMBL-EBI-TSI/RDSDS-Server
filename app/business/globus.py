from globus_sdk import (TransferClient, GlobusError, GlobusAPIError, NetworkError)
import logging
from starlette.requests import Request
from starlette.responses import RedirectResponse, JSONResponse
from app.business.globus_client import globus
from fastapi.encoders import jsonable_encoder
    
async def login(request: Request):
    hostedServer = False
    
    if 'localhost:' not in request.headers.get('Host',''):
        hostedServer = True 
    
    # the redirect URI, as a complete URI (not relative path)
    redirect_uri = request.url_for('globus_login')
    if hostedServer:
        redirect_uri = redirect_uri.replace('http:','https:')
    globus.client.oauth2_start_flow(redirect_uri)

    # If there's no "code" query string parameter, we're in this route
    # starting a Globus Auth login flow.
    # Redirect out to Globus Auth
    if 'code' not in request.query_params:
        auth_uri = globus.client.oauth2_get_authorize_url()
        return RedirectResponse(auth_uri)
    # If we do have a "code" param, we're coming back from Globus Auth
    # and can start the process of exchanging an auth code for a token.
    else:
        jsonResponse = { 'Process' : 'Globus_Auth'}
        code = request.query_params['code']
        
        try:
            tokens = globus.client.oauth2_exchange_code_for_tokens(code)
    
            # store the resulting tokens in the session
            request.session.update(
                tokens=tokens.by_resource_server,
                is_authenticated=True
            )
        except GlobusAPIError as e:
            # Error response from the REST service, check the code and message for
            # details.
            logging.error(("Got a Globus API Error\n"
                           "Error Code: {}\n"
                           "Error Message: {}").format(e.code, e.message))
            
            jsonResponse = {'Globus_code': e.code}
            jsonResponse['Globus_error'] = e.message
            jsonResponse['status'] = e.http_status 
            
            return jsonResponse
        except NetworkError:
            logging.error(("Network Failure. "
                           "Possibly a firewall or connectivity issue"))
            raise
        except GlobusError:
            logging.exception("Totally unexpected GlobusError!")
            raise
        
        #url_to_redirect = request.url_for('create_transfer')
        #if hostedServer:
        #    url_to_redirect = url_to_redirect.replace('http:','https:')
        
        #logging.info("redirect_uri: " + str(url_to_redirect))
        
        jsonResponse['login_success'] = True
        jsonResponse['status'] = 200
        
        jsonResponse_json = jsonable_encoder(jsonResponse)
        return JSONResponse(content=jsonResponse_json, status_code=jsonResponse['status'])
