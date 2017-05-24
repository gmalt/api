# -*- coding: utf-8 -*-
#
# (c) 2016 Jonathan Bouzekri
#
# This file is part of the gMalt application
#
# MIT License :
# https://raw.githubusercontent.com/gmalt/fs-service/master/LICENSE


""" Celery task and service  """

import time
import weedi.loadable as loadable
from celery import Celery, Task


class GetAltitudeTask(Task):
    """ The celery task to find the altitude of coordinates """

    name = "get_altitude"

    def run(self, lat, lng):
        time.sleep(10)
        return lat + lng


class GmaltCelery(Celery, loadable.Service):
    """ The celery application

    :param str name: name of the celery application
    :param str broker: uri to the broker
    :param str backend: uri to the backend
    """
    load_priority = -10

    spec = {
        'name': 'string()',
        'broker': 'string()',
        'backend': 'string()',
    }

    def __init__(self, name, broker, backend, *args, **kwargs):
        super(GmaltCelery, self).__init__(name, broker=broker, backend=backend,
                                          **kwargs)
        self.register_task(GetAltitudeTask)

    def register_task(self, task_class):
        """ Helper to register and bind a task class to this celery instance

        :param task_class: a task class
        :type task_class: :class:`celery.Task`
        """
        self.tasks.register(task_class)
        self.tasks[task_class.name].bind(self)

    @property
    def altitude(self):
        """ Shortcut to the get elevation/altitude task

        :return: the get altitude task
        :rtype: :class:`gmaltfileservice.task.GetAltitudeTask`
        """
        return self.tasks[GetAltitudeTask.name]
