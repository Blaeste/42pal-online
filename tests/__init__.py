
import os

# No test looks for a newer 42pal (see pal42/update.py): no network, and no
# unexpected question. The subprocesses the tests start inherit it.
os.environ["PAL42_NO_UPDATE"] = "1"
