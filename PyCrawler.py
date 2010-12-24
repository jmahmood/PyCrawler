#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
sys.path.append('/home/jawaad/projects/DjCrawler/')

from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.contrib.auth.models import User
from DjCrawler.PyCrawler.models import *


a = spider()
#a.add_root('http://www.example.com')
a.run()
