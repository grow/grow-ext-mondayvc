from protorpc import messages
from protorpc import protojson
import bleach
import grow
import os
import requests
try:
    from HTMLParser import HTMLParser
except ImportError:
    from html.parser import HTMLParser


class Error(Exception):
    pass


class AttributeMessage(messages.Message):
    tag = messages.StringField(1)
    attributes = messages.StringField(2, repeated=True)


class MondayVCPreprocessor(grow.Preprocessor):
    KIND = 'mondayvc'
    JOBS_URL = 'https://api.monday.vc/v2/collections/{collections_id}/jobs'
    COLLECTIONS_URL = 'https://api.monday.vc/v2/collections'
    ORGANIZATIONS_URL = 'https://api.monday.vc/v2/collections/{collections_id}/organizations'
    QUERY_PARAM = '?page=1&per_page=100'

    class Config(messages.Message):
        api_user = messages.StringField(1)
        api_key = messages.StringField(2)
        collections_id = messages.StringField(3)
        jobs_path = messages.StringField(4)
        collections_path = messages.StringField(5)
        organizations_path = messages.StringField(6)

    def bind_jobs(self, collections_id, jobs_path):
        headers = { 'X-User-Email': self.config.api_user, 'X-User-Token': self.config.api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = MondayVCPreprocessor.JOBS_URL.format(collections_id=collections_id) + MondayVCPreprocessor.QUERY_PARAM
        resp = requests.get(url, headers=headers)
    	if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
        jobs = resp.json()
        path = os.path.join(jobs_path)
        self.pod.write_yaml(path, jobs)
        self.pod.logger.info('Saving -> {}'.format(path))

    def bind_collections(self, collections_path):
        headers = { 'X-User-Email': self.config.api_user, 'X-User-Token': self.config.api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = MondayVCPreprocessor.COLLECTIONS_URL
        resp = requests.get(url, headers=headers)
    	if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
        collections = resp.json()
        path = os.path.join(collections_path)
        self.pod.write_yaml(path, collections)
        self.pod.logger.info('Saving -> {}'.format(path))

    def bind_organizations(self, collections_id, organizations_path):
        headers = { 'X-User-Email': self.config.api_user, 'X-User-Token': self.config.api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = MondayVCPreprocessor.ORGANIZATIONS_URL.format(collections_id=collections_id) + MondayVCPreprocessor.QUERY_PARAM
        resp = requests.get(url, headers=headers)
    	if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
        organizations = resp.json()
        path = os.path.join(organizations_path)
        self.pod.write_yaml(path, organizations)
        self.pod.logger.info('Saving -> {}'.format(path))

    def run(self, *args, **kwargs):
        if self.config.jobs_path:
            self.bind_jobs(
                self.config.collections_id,
                self.config.jobs_path)
        if self.config.collections_path:
            self.bind_collections(
                self.config.collections_path)
        if self.config.organizations_path:
            self.bind_organizations(
                self.config.collections_id,
                self.config.organizations_path)
