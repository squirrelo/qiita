#!/usr/bin/env python
from __future__ import division
from json import dumps

from redis import Redis

from qiita_db.job import Job

from qiita_ware.cluster import qiita_compute
from .cluster import system_call


# -----------------------------------------------------------------------------
# Copyright (c) 2014--, The Qiita Development Team.
#
# Distributed under the terms of the BSD 3-clause License.
#
# The full license is in the file LICENSE, distributed with this software.
# -----------------------------------------------------------------------------

r_server = Redis()


def cleanup_redis(user, analysis_id):
    """remove analysis messages from redis user:messages key list"""
    [r_server.lrem("%s:messages" % user, msg) for msg in
     r_server.lrange("%s:messages" % user) if
     '"analysis":%i,' % analysis_id in msg]


def call_wrapper(user, analysis, job, total):
    """Takes care of redis messaging required for the job run"""
    name, command = job.command
    options = job.options
    # create json base for websocket messages
    msg = {
        "analysis": analysis.id,
        "msg": None,
        "command": "%s: %s" % (job.datatype, name)
    }
    pubsub = r_server.pubsub()
    pubsub.subscribe(user)

    # create call
    o_fmt = ' '.join(['%s %s' % (k, v) for k, v in options.items()])
    c_fmt = str("%s %s" % (command, o_fmt))

    # send running message to user wait page
    job.status = 'running'
    msg["msg"] = "Running"
    json = dumps(msg)
    r_server.lpush(user + ":messages", json)
    r_server.publish(user, json)

    # run the actual call and send complete or error message
    try:
        system_call(c_fmt)
        msg["msg"] = "Completed"
        json = dumps(msg)
        r_server.rpush("%s:messages" % user, json)
        r_server.publish(user, json)
        # FIX THIS Should not be hard coded
        job.add_results([(options["--output_dir"], "directory")])
        job.status = 'completed'
    except Exception as e:
        all_good = False
        job.status = 'error'
        msg["msg"] = "ERROR"
        json = dumps(msg)
        r_server.rpush(user + ":messages", json)
        r_server.publish(user, json)
        print("Failed compute on job id %d: %s\n%s" %
              (job.id, e, c_fmt))

    # figure out how many of the jobs in this analysis have completed
    count = sum(1 for msg in r_server.lrange("%s:messages" % user) if
                '"analysis":%i,' % analysis.id in msg)

    if count == total:
        # send websockets message that analysis is done
        msg["msg"] = "allcomplete"
        msg["command"] = ""
        json = dumps(msg)
        r_server.rpush(user + ":messages", json)
        r_server.publish(user, json)
        pubsub.unsubscribe()
        # set final analysis status
        if all_good:
            analysis.status = "completed"
        else:
            analysis.status = "error"


def run_analysis(user, analysis):
    """Run the commands within an Analysis object and sends user messages"""
    analysis.status = "running"
    jobs = analysis.jobs
    for job_id in jobs:
        job = Job(job_id)
        if job.status == 'queued':
            # run the command
            qiita_compute.submit_async(call_wrapper(user, analysis,
                                                    job, len(jobs)))
