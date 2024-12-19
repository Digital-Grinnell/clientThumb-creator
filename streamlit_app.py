# streamlit-app.py
##
## This Streamlit (https://streamlit.io/) app supplements `worksheet-file-finder`.  It creates a `.clientThumb` JPG thumbnail derivative for every file it finds in `/Volumes/exports/OBJs`.  The directory is then suitable for uploading in support of an Alma-D import process.
## -----------------------------------------------------------------------------------------------------

import os
import streamlit as st
from thumbnail import generate_thumbnail
from loguru import logger
from subprocess import call

# Globals

counter = 0
big_file_list = [ ]   # need a list of just filenames...
big_path_list = [ ]   # ...and parallel list of just the paths

# My functions
# ---------------------------------------------------------------------

# state(key) - Return the value of st.session_state[key] or False
# If state is set and equal to "None", return False.
# -------------------------------------------------------------------------------
def state(key):
    try:
        if st.session_state[key]:
            if st.session_state[key] == "None":
                return False
            return st.session_state[key]
        else:
            return False
    except Exception as e:
        # st.exception(f"Exception: {e}")
        return False

# create_derivative(local_storage_path)
# ------------------------------------------------------------
def create_derivative(local_storage_path):

    dirname, basename = os.path.split(local_storage_path)
    root, ext = os.path.splitext(basename)

    # Create clientThumb thumbnails for Alma
    derivative_path = f"/Volumes/exports/OBJs/{root}X.jpg"
    dest = f"/Volumes/exports/OBJs/{root}{ext}.clientThumb"

    options = { 'trim': False,
                'height': 400,
                'width': 400,
                'quality': 85,
                'type': 'thumbnail'
              }

    # If original is an image...
    if ext.lower( ) in ['.tiff', '.tif', '.jpg', '.jpeg', '.png']:
        generate_thumbnail(local_storage_path, derivative_path, options)
        os.rename(derivative_path, dest)

    # If original is a PDF...
    elif ext.lower( ) == '.pdf':
        cmd = 'magick ' + local_storage_path + '[0] ' + derivative_path
        call(cmd, shell=True)
        os.rename(derivative_path, dest)

    else:
        txt = f"Sorry, we can't create a thumbnail for '{local_storage_path}'"
        st.warning(txt)
        state('logger').warning(txt)

# ----------------------------------------------------------------------
# --- Main

if __name__ == '__main__':

    # Initialize the session_state
    if not state('logger'):
        logger.add("app.log", rotation="500 MB")
        logger.info('This is streamlit_app.py!')
        st.session_state.logger = logger

# Go
# --------------------------------------------------------------------------------------

    counter = 0
    filenames = [ ]

    # Grab all non-hidden filenames from the target directory tree so we only have to get the list once
    # Exclusion of dot files per https://stackoverflow.com/questions/13454164/os-walk-without-hidden-folders

    path = "/Volumes/exports/OBJs"

    for root, dirs, files in os.walk(path):
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']
        for filename in files:
            big_path_list.append(root)
            big_file_list.append(filename)

    # Check for ZERO network files in the big_file_list
    if len(big_file_list) == 0:
        txt = f"The specified path '{path}' returned NO files!  Check your path specification and network connection!\n"
        st.error(txt)
        state('logger').error(txt)
        exit( )

    num_filenames = len(files)
    progress_text = f"Processing in progress for {num_filenames} files.  Be patient."
    with st.status(progress_text, expanded=True) as status:
        search_progress = st.progress(0, progress_text)

        # Now the main loop...
        for x in range(num_filenames):

            percent_complete = min(x / num_filenames, 100)
            search_progress.progress(percent_complete, progress_text)

            counter += 1
            target = "/Volumes/exports/OBJs/" + files[x]
            thumb = target + ".clientThumb"

            status.update(
                label=
                f"{counter}. Filename is '{target}'.  Generating '{thumb}...",
                expanded=True,
                state="running")

            create_derivative(target)    


        txt = f"**clientThumb creation is COMPLETE!**"
        st.success(txt)
        state('logger').success(txt)

        status.update(label=f"clientThumb creation is **complete**!",
            expanded=True, state="complete")

