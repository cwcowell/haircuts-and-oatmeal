import os
import sys

THIS_FILE_PATH: str = os.path.split(os.path.abspath(__file__))[0]
REPO_ROOT_PATH: str = os.path.join(THIS_FILE_PATH, '../..')
SRC_ROOT_PATH: str = os.path.join(REPO_ROOT_PATH, 'src')
TEST_RESOURCES_PATH: str = os.path.join(REPO_ROOT_PATH, 'test', 'resources')

sys.path.append(SRC_ROOT_PATH)


def before_feature(context, feature):
    """Make a temporary dir to store test sqlite3 and csv files in."""
    os.mkdir(TEST_RESOURCES_PATH)
