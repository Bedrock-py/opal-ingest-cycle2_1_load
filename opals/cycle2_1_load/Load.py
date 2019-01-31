# ****************************************************************
# Copyright (c) 2015, Georgia Tech Research Institute
# All rights reserved.
#
# This unpublished material is the property of the Georgia Tech
# Research Institute and is protected under copyright law.
# The methods and techniques described herein are considered
# trade secrets and/or confidential. Reproduction or distribution,
# in whole or in part, is forbidden except by the express written
# permission of the Georgia Tech Research Institute.
# ****************************************************************/
import pathlib

import requests

from bedrock.dataloader.utils import *
from bedrock.core.io import download_file
import time
import csv
import xlrd
import re
import os
import traceback
import pandas as pd
from collections import Counter
from itertools import islice
import logging
import rpy2.robjects as robjects
from rpy2.robjects import r, pandas2ri
from rpy2.robjects.packages import importr


class Load(Ingest):
    def __init__(self):
        super(Load, self).__init__()
        self.name = 'Load Game Logs and Metadata'
        self.description = 'Loads game logs and metadata into R workspace.'
        self.parameters_spec = [{"url": "url"}]  # TODO: Is this needed?
        # self.NUM_EXAMPLES = 10
        # self.NUM_SAMPLES = 100000
        # self.NUM_UNIQUE = 10

    # Download all the files from the OSF repository

    def ingest(self, posted_data, src):
        pass

    def custom(self, **kwargs):

        if "param1" in kwargs and kwargs["param1"] == 'initialize':

            # pandas2ri.activate()

            # save R workspace and load workspaces between opals!
            # 1. load workspace created during data load

            # rstan = importr("rstanarm")
            # rdf = pandas2ri.py2ri(df)
            # robjects.globalenv["rdf"] = rdf

            filepath = kwargs["filepath"]

            DIRMASK = 0o775

            if not os.path.exists(filepath):
                os.makedirs(filepath, DIRMASK)

            # Set directory to dataloader source id path
            r("setwd('{}')".format(kwargs["filepath"] + ""))
            r("save.image()") # saves to .RData by default

            # Clear any prior variables to be safe
            r("rm(list = ls(all = TRUE))")

            # Load these libraries
            r('if (!require("pacman")) install.packages("pacman")')
            r('library ("pacman")')
            r("pacman::p_load(rstan, rstanarm, ggplot2, Hmisc, httr, bridgesampling, DT, dplyr, bayesplot, knitr)")
            r("set.seed(12345)")
            r("nIter = 10000")
            r("LOCAL <- TRUE")

            # set the paths for reading data files and writing
            data_file_path = filepath + "source"

            if not os.path.exists(data_file_path):
                os.makedirs(data_file_path, DIRMASK) # This directory should already from downloading files

            # Load the meta-data
            # https://osf.io/download/dwce3/ <-- current OSF location of boomtown_metadata TODO: Parameterize
            try:
                download_file(data_file_path + "/", "boomtown_metadata.csv", "https://osf.io/download/dwce3/")
            except Exception as e:
                logging.error("Could not download boomtown_metadata.csv")
                logging.error(e)
                r("save.image()")  # saves to .RData by default

            output_path = filepath + "output"

            if not os.path.exists(output_path):
                os.makedirs(output_path, DIRMASK)

            r('dd <- "{}"'.format(data_file_path))
            r('od <- "{}"'.format(output_path))
            seed = 12345
            r('set.seed({})'.format(str(seed)))
            opal_dir = pathlib.Path(__file__).parent
            r("source('{}/effects.R')".format(opal_dir))  # Load Effects Data Structures: Hyps and Logodds
            r("save.image()")  # saves to .RData by default
