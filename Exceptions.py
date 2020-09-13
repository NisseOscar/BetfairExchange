
# Source: https://stackoverflow.com/a/1319675
class LoginException(Exception):
    def __init__(self,message =None):
        super()
        if message != None:
            self.message = message
            
class RequestException(Exception):
    """
        An Excpetion class to handle Request exceptions from the Betfair api.
        All is based on this link: https://docs.developer.betfair.com/display/1smk3cen4v3lu3yomq5qye0ni/listCompetitions
    """
    def __init__(self,errCode):
        if(errCode == '-32700'):
            error = 'Invalid JSON was received by the server. An error occurred on the server while parsing the JSON text.'
        elif(errCode == '-32601'):
            error = 'Method not found'
        elif(errCode == '-32602'):
            error = 'Problem parsing the parameters, or a mandatory parameter was not found'
        elif(errCode == '-32603'):
            error = 'Internal JSON-RPC error'
        elif(errCode == 'TOO_MUCH_DATA'):
            error = 'The operation requested too much data, exceeding the Market Data Request Limits.'
        elif(errCode == 'INVALID_INPUT_DATA'):
            error = 'The data input is invalid. A specific description is returned via errorDetails as shown below.'
        elif(errCode =='INVALID_SESSION_INFORMATION'):
            error = 'The session token hasnt been provided, is invalid or has expired.'
        elif(errCode =='NO_APP_KEY'):
            error = 'An application key header (X-Application) has not been provided in the request'
        elif(errCode =='NO_SESSION'):
            error = 'A session token header (X-Authentication) has not been provided in the request'
        elif(errCode =='UNEXPECTED_ERROR'):
            error = 'An unexpected internal error occurred that prevented successful request processing.'
        elif(errCode =='INVALID_APP_KEY'):
            error = 'The application key passed is invalid or is not present'
        elif(errCode =='TOO_MANY_REQUESTS'):
            error = 'There are too many pending requests'
        elif(errCode =='SERVICE_BUSY'):
            error = 'The service is currently too busy to service this request.'
        elif(errCode =='TIMEOUT_ERROR'):
            error = 'The Internal call to downstream service timed out.'
        elif(errCode =='REQUEST_SIZE_EXCEEDS_LIMIT'):
            error = 'The request exceeds the request size limit.'
        elif(errCode =='ACCESS_DENIED'):
            error = 'The calling client is not permitted to perform the specific action'
        else:
            error = 'error is unexplained by documentation'

        self.message = 'A request error occured, '+errCode+": " + error
