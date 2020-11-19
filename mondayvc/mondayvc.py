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
    JOBS_URL = 'https://api.getro.com/v2/networks/{networks_id}/jobs'
    NETWORKS_URL = 'https://api.getro.com/v2/networks'
    ORGANIZATIONS_URL = 'https://api.getro.com/v2/networks/{networks_id}/companies'
    QUERY_PARAM = '?page={number_of_page}&per_page=100'
    NETWORKS_ID = ''

    class Config(messages.Message):
        api_user = messages.StringField(1)
        api_key = messages.StringField(2)
        jobs_path = messages.StringField(4)
        networks_path = messages.StringField(5)
        companies_path = messages.StringField(6)

    def bind_networks(self, networks_path):
        headers = { 'X-User-Email': self.config.api_user, 'X-User-Token': self.config.api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = MondayVCPreprocessor.NETWORKS_URL
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
        networks = resp.json()
        MondayVCPreprocessor.NETWORKS_ID = networks['items'][0]['id']
        path = os.path.join(networks_path)
        self.pod.write_yaml(path, networks)
        self.pod.logger.info('Saving -> {}'.format(path))

    def bind_companies(self, networks_id, companies_path):
        headers = { 'X-User-Email': self.config.api_user, 'X-User-Token': self.config.api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = MondayVCPreprocessor.ORGANIZATIONS_URL.format(networks_id=networks_id) + MondayVCPreprocessor.QUERY_PARAM.format(number_of_page=1)
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
        companies = resp.json()
        path = os.path.join(companies_path)
        self.pod.write_yaml(path, companies)
        self.pod.logger.info('Saving -> {}'.format(path))

    def bind_jobs(self, networks_id, jobs_path):
        jobs = {}
        headers = { 'X-User-Email': self.config.api_user, 'X-User-Token': self.config.api_key, 'Content-Type': 'application/json', 'Accept': 'application/json'}
        def get_jobs(number_of_page=1):
            url = MondayVCPreprocessor.JOBS_URL.format(networks_id=networks_id) + MondayVCPreprocessor.QUERY_PARAM.format(number_of_page=number_of_page)
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                raise Error('Error requesting -> {}'.format(url))
            return resp.json()
        # TODO (@micjamking): retrieve meta information
        def get_all_jobs(number_of_page=1):
            results = get_jobs(number_of_page)
            self.pod.logger.info('Retreiving page {} from Jobs API for data'.format(number_of_page))
            if len(results['items']) > 0:
                return results['items'] + get_all_jobs(number_of_page+1)
            else:
                return results['items']
        jobs['items'] = get_all_jobs()
        path = os.path.join(jobs_path)
        self.pod.write_yaml(path, jobs)
        self.pod.logger.info('Saving -> {}'.format(path))

    def run(self, *args, **kwargs):
        if self.config.networks_path:
            self.bind_networks(
                self.config.networks_path)
        if self.config.companies_path:
            self.bind_companies(
                MondayVCPreprocessor.NETWORKS_ID,
                self.config.companies_path)
        if self.config.jobs_path:
            self.bind_jobs(
                MondayVCPreprocessor.NETWORKS_ID,
                self.config.jobs_path)
