# You have to provide a url from which to download your requirements file.
REQ_URL = "https://raw.github.com/username/library/branch/requirements.txt"

# Set this to a number to only grab the first N packages. Set it to None to
# grab all the packages.
LIMIT = 10

# We have quite a few things hosted locally only. This keeps us from looking
# those up.
LOCAL = ("mylocalrepo",
	     "anotherlocalrepo")