import os
import sys
import subprocess
import time
import zipfile
import argparse
from main import display_color
import platform

CHANNEL=None
REPO=None
TAG=None
OWNER=None
PUBLISH_TYPE=None

APP="vng"
FILES_TO_ZIP = []

def create_executable(skip_deploy):
    if not skip_deploy:
        title = display_color("#008000","[BUILDING THE EXE FILE]")
        print(f"{title}")
        subprocess.call(f"pyinstaller --clean vng.spec") 

def ZipAndPublish(skip_release, skip_zip):
    
    title_0 = display_color("#008000","[ZIPING THE EXE FILE]")
    title_1 = display_color("#008000","[UPLOADING THE EXE FILE TO GITHUB]")

    if not skip_zip:
        print(f"{title_0}")
    
        time.sleep(2)
        zip = zipfile.ZipFile(f"dist/{APP}.zip", "w", zipfile.ZIP_DEFLATED)
        for file in FILES_TO_ZIP:
            zip.write(f"dist/{file}")
        zip.close()

    if not skip_release:
        time.sleep(2)

        print(f"{title_1}")
        if CHANNEL == "re":
            subprocess.call(f"gh release create v{TAG} ./dist/{APP}.zip --generate-notes -t v{TAG} {PUBLISH_TYPE} --repo {OWNER}/{REPO}")
        elif CHANNEL == "pre":
            subprocess.call(f"gh release create v{TAG} ./dist/{APP}.zip --generate-notes -t v{TAG} {PUBLISH_TYPE} -p")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # DEPLOY & RELEASE 
    parser.add_argument('--no-build', dest='skip_deploy', default=False, help='Skip the build process', action="store_true")
    parser.add_argument('--no-release', dest='skip_release', default=False, help='Skip the release process', action="store_true")
    parser.add_argument('--no-zip', dest='skip_zip', default=False, help='Skip the zip process', action="store_true")


    # GITHUB
    parser.add_argument('--channel', '-c', dest='channel', default="re", type=str, help='Chose the release channel <re|pre>')
    parser.add_argument('--draft', '-d', dest='draft', default=False, help='Publish the release in draft mode', action="store_true")
    parser.add_argument('--repo', '-r', dest='repo', default="repo", type=str, help='add the repo name', required=True)
    parser.add_argument('--owner', '-o', dest='owner', default="username", type=str, help='add the owner name', required=True)
    parser.add_argument('--tag', '-t', dest='tag', default=None, type=str, help='add the tag for release', required=True)
    parser.add_argument('--files', '-f', dest='files', type=str, help='add files to zip inside dist folder', nargs='+', required=True)
    

    args = parser.parse_args()

    CHANNEL = args.channel
    REPO = args.repo
    TAG = args.tag
    OWNER = args.owner
    FILES_TO_ZIP = args.files
    PUBLISH_TYPE = "-d" if args.draft else ""
    print(args)

    try:

        create_executable(skip_deploy=args.skip_deploy)
        
        ZipAndPublish(skip_release=args.skip_release, skip_zip= args.skip_zip)
        pass
    except Exception as e:
        traceback_template = '''Exception error:
  %(message)s\n

  %(plataform)s
  
  '''

        traceback_details = {
            'message' : e,
            'plataform': f"{platform.system()}-{platform.version()}",
        }    
        
        print(traceback_template % traceback_details)
 