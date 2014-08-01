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

# Load in Vimeo auth info, requires adding parent dir to import paths.
import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)
from vimeo.auth import get_client_credentials


"""
Convenience for generating a client credential access token.

It is not necessary to run this script before using the python Vimeo library.
This script is provided only as a convenience. For a service this should be used
to generate tokens that can make requests on behalf of the app.

The function for this flow can be found in vimeo/auth.py
"""
if __name__ == "__main__":
    args = None
    parser = argparse.ArgumentParser(description='Generate an API access token')
    parser.add_argument('--cid', '-i', help="Your client ID", nargs=1, required=True)
    parser.add_argument('--secret', '-s', help="Your client secret", nargs=1, required=True)
    parser.add_argument('--scopes', '-o', help="Your requested scopes",
                        nargs=argparse.REMAINDER, required=False)
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

    print "Client token is %s" % get_client_credentials(args.cid[0],
                                              args.secret[0], scopes=args.scopes,
                                              api_root=api_root)
