import os
import pyblish.api
from pype.hosts import resolve
from avalon import api as avalon
from pprint import pformat

# dev
from importlib import reload
from pype.hosts.resolve import otio
reload(otio)


class CollectWorkfile(pyblish.api.ContextPlugin):
    """Inject the current working file into context"""

    label = "Collect Workfile"
    order = pyblish.api.CollectorOrder - 0.501

    def process(self, context):

        asset = avalon.Session["AVALON_ASSET"]
        subset = "workfile"
        project = resolve.get_current_project()
        fps = project.GetSetting("timelineFrameRate")

        # adding otio timeline to context
        otio_timeline = resolve.get_otio_complete_timeline(project)

        active_sequence = resolve.get_current_sequence()
        video_tracks = resolve.get_video_track_names()

        instance_data = {
            "name": "{}_{}".format(asset, subset),
            "asset": asset,
            "subset": "{}{}".format(asset, subset.capitalize()),
            "item": project,
            "family": "workfile"
        }

        # create instance with workfile
        instance = context.create_instance(**instance_data)

        # update context with main project attributes
        context_data = {
            "activeProject": project,
            "activeSequence": active_sequence,
            "otioTimeline": otio_timeline,
            "videoTracks": video_tracks,
            "currentFile": project.GetName(),
            "fps": fps,
        }
        context.data.update(context_data)

        self.log.info("Creating instance: {}".format(instance))
        self.log.debug("__ instance.data: {}".format(pformat(instance.data)))
        self.log.debug("__ context_data: {}".format(pformat(context_data)))
