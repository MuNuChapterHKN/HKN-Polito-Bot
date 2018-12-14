from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts
import os 

def retrieve_posts():
    client = Client(url = 'https://hknpolito.org/xmlrpc', username = "HKNP0lit0", password = os.environ['HKN_WEB_PASSWORD'])
    postsdict = client.call(posts.GetPosts())
    return postsdict
