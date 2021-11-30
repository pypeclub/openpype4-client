import getpass
import os

from avalon.tvpaint import lib, pipeline, get_current_workfile_context
from avalon import api, io
from openpype.lib import (
    get_workfile_template_key_from_context,
    get_workdir_data
)
from openpype.api import Anatomy


class LoadWorkfile(pipeline.Loader):
    """Load workfile."""

    families = ["workfile"]
    representations = ["tvpp"]

    label = "Load Workfile"

    def load(self, context, name, namespace, options):
        # Load context of current workfile as first thing
        #   - which context and extension has
        host = api.registered_host()
        current_file = host.current_file()

        context = get_current_workfile_context()

        filepath = self.fname.replace("\\", "/")

        if not os.path.exists(filepath):
            raise FileExistsError(
                "The loaded file does not exist. Try downloading it first."
            )

        george_script = "tv_LoadProject '\"'\"{}\"'\"'".format(
            filepath
        )
        lib.execute_george_through_file(george_script)

        # Save workfile.
        host_name = "tvpaint"
        asset_name = context.get("asset")
        task_name = context.get("task")
        # Far cases when there is workfile without context
        if not asset_name:
            asset_name = io.Session["AVALON_ASSET"]
            task_name = io.Session["AVALON_TASK"]

        project_doc = io.find_one({
            "type": "project"
        })
        asset_doc = io.find_one({
            "type": "asset",
            "name": asset_name
        })
        project_name = project_doc["name"]

        template_key = get_workfile_template_key_from_context(
            asset_name,
            task_name,
            host_name,
            project_name=project_name,
            dbcon=io
        )
        anatomy = Anatomy(project_name)

        data = get_workdir_data(project_doc, asset_doc, task_name, host_name)
        data["root"] = anatomy.roots
        data["user"] = getpass.getuser()

        template = anatomy.templates[template_key]["file"]

        # Define saving file extension
        if current_file:
            # Match the extension of current file
            _, extension = os.path.splitext(current_file)
        else:
            # Fall back to the first extension supported for this host.
            extension = host.file_extensions()[0]

        data["ext"] = extension

        work_root = api.format_template_with_optional_keys(
            data, anatomy.templates[template_key]["folder"]
        )
        version = api.last_workfile_with_version(
            work_root, template, data, host.file_extensions()
        )[1]

        if version is None:
            version = 1
        else:
            version += 1

        data["version"] = version

        path = os.path.join(
            work_root,
            api.format_template_with_optional_keys(data, template)
        )
        host.save_file(path)