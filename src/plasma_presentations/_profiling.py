"""The scope-profiler tag of plasma_presentations's profiling regions.

The regions are opt-in: :mod:`plasma_presentations` registers the tag on import, so they
record nothing unless the application enables it, e.g. with
``scope_profiler.setup(enable_tags=["plasma_presentations"])``.
"""

#: Tags of every plasma_presentations region; the first is the opt-in tag.
PROFILE_TAGS = ("plasma_presentations",)
