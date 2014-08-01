"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the license.
"""
import argparse

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from vimeo.auth import get_auth_url, get_access_token


"""
Convenience for generating an access token.

It is not necessary to run this script before using the python Vimeo library.
This script is provided only as a convenience. In the context of a web server,
the programmer can use the library to guide a user through the authorization flow,
allowing that user to create their own access token.

The functions for this flow can be found in vimeo/auth.py
"""
if __name__ == "__main__":
    args = None
    parser = argparse.ArgumentParser(description='Generate an API access token')
    parser.add_argument('--cid', '-i', help="Your client ID", nargs=1, required=True)
    parser.add_argument('--secret', '-s', help="Your client secret", nargs=1, required=True)
    parser.add_argument('--redirect', '-r', help="Your app's redirect URI", nargs=1, required=True)
    parser.add_argument('--scopes', '-o', help="Your requested scopes",
                        nargs=argparse.REMAINDER, required=True)
    parser.add_argument('--dev', '-d', action="store_true", help="Use dev server")
    args = parser.parse_args()

    api_root = "http://api.vimeo."

    if args.dev:
        api_root += "dev"
    else:
        api_root += "com"

    def do_auth_flow(api_root, cid, secret, scopes, redirect):
        print "Visit %s in a browser" % get_auth_url(api_root, cid, scopes, redirect)
        auth_code = raw_input("Enter auth code: ")

        return get_access_token(auth_code, api_root, cid, secret, redirect)

    print "Access token is %s" % do_auth_flow(api_root, args.cid[0],
                                              args.secret[0], args.scopes,
                                              args.redirect[0])
