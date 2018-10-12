import os
import shutil
import sys

THIS_FILE_PATH: str = os.path.split(os.path.abspath(__file__))[0]
REPO_ROOT_PATH: str = os.path.join(THIS_FILE_PATH, '../..')
SRC_ROOT_PATH: str = os.path.join(REPO_ROOT_PATH, 'src')
TEST_RESOURCES_PATH: str = os.path.join(REPO_ROOT_PATH, 'test', 'resources')

sys.path.append(SRC_ROOT_PATH)  # allows behave to find all the source files


def before_feature(context, feature):
    # Make a temporary dir to store test sqlite3 and csv files in.
    shutil.rmtree(path=TEST_RESOURCES_PATH, ignore_errors=True)
    os.mkdir(TEST_RESOURCES_PATH)

