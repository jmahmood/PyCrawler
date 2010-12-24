#!/usr/bin/env python
# -*- coding: utf8 -*-

from django.db import models
from BeautifulSoup import BeautifulSoup
import threading
import robotparser
import urllib2
import urlparse

FIND_COMMON_ERRORS = True
RESPECT_ROBOTS_FILE = True
DEFAULT_USER_AGENT = "PyCrawler"

DEFAULT_START_URL = 'http://www.tokyomuslim.com'
DEFAULT_CRAWL_DEPTH = 0

#This class stores all information related to the web page
class WebPage(models.Model):
    
    url = models.CharField(verbose_name='URL',max_length=256)
    crawled = models.BooleanField(verbose_name="Has this page been crawled yet?", default=False)
    error = models.BooleanField(verbose_name="Was there an error while crawling this page?", default=False)

    title = models.CharField(verbose_name='Page Title',max_length=256,null=True,blank=True)
    keywords = models.TextField(verbose_name='Keywords',null=True,blank=True)
    description = models.TextField(verbose_name='Description',null=True,blank=True)
    parent = models.ForeignKey('self',null=True,blank=True)
    

    header = models.TextField(verbose_name="Raw Page Header")
    body = models.TextField(verbose_name="Raw Page Body")
    
    crawl_level = models.SmallIntegerField(verbose_name="Level", default=0)
    
    problems = models.TextField(verbose_name="Problems found.")

class spider(threading.Thread):
    # Parser for robots.txt that helps determine
    # if we are allowed to fetch a url
    rp = robotparser.RobotFileParser()
    
    
    def run(self):
        while 1:
            page = WebPage.objects.filter(crawled=False)[:1]
            for p in page:
                self.crawl(p)
    
    
        
    
    def open_url(self, page):
        curl = page.url #curl = crawl url
        request = urllib2.Request(curl)
        request.add_header("User-Agent", DEFAULT_USER_AGENT)
        opener = urllib2.build_opener()
        return opener.open(request).read()
        
    def check_keywords(self, soup, page):
        keywords = soup.head.findAll(attrs={"name":"keywords"})
        
        if FIND_COMMON_ERRORS:

            if len(keywords) == 0:
                page.problems.append("You have no keyword field （ ´,_ゝ`).\n")
        
            if len(keywords) > 1:
                page.problems.append("You have too many keyword fields. Σ(゜д゜;) \n")
    
            bodykeywords = soup.body.findAll(attrs={"name":"keywords"})
            if len(bodykeywords) > 0:
                page.problems.append("You have keyword fields in the _body_. (ಠ_ಠ unless it's a form)\n")

        if len(keywords) > 0:
            page.keywords = keywords[0]['content']

    def check_description(self, soup, page):
        description = soup.findAll(attrs={"name":"description"})
        
        if FIND_COMMON_ERRORS:

            if len(description) == 0:
                page.problems.append("You have no description field （ ´,_ゝ`).\n")
        
            if len(description) > 1:
                page.problems.append("You have too many keyword fields. Σ(゜д゜;) \n")
    
            bodykeywords = soup.body.findAll(attrs={"name":"description"})
            if len(bodykeywords) > 0:
                page.problems.append("You have description fields in the _body_. (ಠ_ಠ unless it's a form).\n")

        if len(description) > 0:
            page.keywords = description[0]['content']
            
    def check_robots_file(self, page):
        try:
            # Have our robot parser grab the robots.txt file and read it
            self.rp.set_url('http://' + url[1] + '/robots.txt')
            self.rp.read()
            # If we're not allowed to open a url, return the function to skip itif not self.rp.can_fetch('PyCrawler', curl):
            if not self.rp.can_fetch('PyCrawler', curl):
                page.problems.append(page.url + " not allowed by robots.txt")
                return False
        except:
            return True

    def crawl(self, page):
        if RESPECT_ROBOTS_FILE: self.check_robots_file(page)
        
        try:
            msg = self.open_url(page)
        except:
            page.error = True
            page.save()
            return
        else:
            print "Succesfully opened page %s" % page.url
            page.crawled = True
            page.error = False
            page.save()
        
        if page.FIND_COMMON_ERRORS:
            page.problems = ''
        
        soup = BeautifulSoup(msg)
        
        onpage_urls = soup.findAll('a')
        page.title = soup.head.title.string
        
        self.check_keywords(soup, page)
        self.check_description(soup, page)
        header = soup.head
        body = soup.body
        
        
        page.save()
        
        self.add_leaf_page(onpage_urls, page)
        
    def add_leaf_page(self, url_list, page):
        for u in url_list:
            # check that it already exists.
            # else...

            new_page = WebPage()
            new_page.parent = page
            new_page.url = u['href']
            new_page.crawl_level = page.crawl_level + 1
            new_page.save()
            
    def add_root(self, url):
            new_page = WebPage()
            new_page.parent = None
            new_page.url = url
            new_page.crawl_level = 0
            new_page.save()
            

