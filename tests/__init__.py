
import os

# No test looks for a newer 42pal (see pal42/update.py): no network, and no
# unexpected question. The subprocesses the tests start inherit it.
os.environ["PAL42_NO_UPDATE"] = "1"

# No test reaches a real 42pal server, even through the login kept in
# ~/.42pal/online.json: the server is a port of this machine where nothing
# listens. The tests of the online mode give their fake server themselves.
os.environ["PAL42_SERVER"] = "http://127.0.0.1:9"
