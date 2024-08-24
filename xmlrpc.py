import requests
import argparse
import logging
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('MyLogger')

class xmlrpc:
    """XMLRPC class to interact with XMLRPC server"""

    def __init__(self, url):
        self.url = url + "/xmlrpc.php"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        }

    def list_methods(self):
        """List all methods available on the XMLRPC server"""

        xml = """<?xml version="1.0"?>
        <methodCall>
        <methodName>system.listMethods</methodName>
        <params></params>
        </methodCall>"""

        try:
            response = requests.post(self.url, data=xml, headers=self.headers)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"An error occurred: {e}")
            return
        
        data = response.content
        root = ET.fromstring(data)
        return [elem.text for elem in root.findall('.//string')] # Find all <value> tags and extract the text inside them

    def test_methods(self):
        """Test every methods and get the return"""
        res = []
        method_list = self.list_methods()

        for method in method_list:
            xml = f"""<?xml version="1.0"?>
            <methodCall>
            <methodName>{method}</methodName>
            <params></params>
            </methodCall>"""

            try:
                response = requests.post(self.url, data=xml, headers=self.headers)
                response.raise_for_status()
            except requests.exceptions.RequestException as e:
                logger.error(f"An error occurred: {e}")
                return
            
            data = response.text
            print(data)
            #exit()
            #root = ET.fromstring(data)
            #print(root.text)
            #exit()
            #res += [elem.text for elem in root.findall('.//')if elem.text and '\n' not in elem.text]  # Find all <value> tags and extract the text inside them

        return res
            #print(f"{method} : {root.text}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='XMLRPC')
    parser.add_argument('url', help='Website URL. Ex : http://example.com/')
    args = parser.parse_args()
    xmlrpc = xmlrpc(args.url)
    
    methods = xmlrpc.list_methods()
    res = xmlrpc.test_methods()
    print(res)

