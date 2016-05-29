#!/usr/bin/env python
# -*- coding: latin-1 -*-
from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)
            # for example: People.name = 'Luke Skywalker'

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        # for example: json_data = api_client.get_people(1)
        json_data = getattr(api_client, 'get_{}'.format(cls.RESOURCE_NAME))(resource_id)
        # we will return an object of type cls
        # for example: People(json_data)
        return cls(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        # used globals() since the QuerySet class was defined below
        # this class in the file and out of scope from here
        return globals()[cls.QUERY_SET_NAME]()
       
        
class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people' # used to call get_people() on api
    QUERY_SET_NAME = 'PeopleQuerySet' # used to access the QuerySet class

    def __init__(self, json_data):
          super(People, self).__init__(json_data)
          #self.get_film_titles()

    def __repr__(self):
        # use encode to deal with utf characters like in Padmé Amidala
        self.name = self.name.encode('utf8', 'ignore')
        return 'Person: {0}'.format(self.name)
    
    '''
    def get_film_titles(self):
        # converts list of urls to film titles
        # works with real SWAPI but doesn't work with test... very frustrated with test
        self.film_titles = []
        for film in self.films:
            film_object = Films.get(film.split('/')[-2])
            self.film_titles.append(film_object.title.encode('ascii'))
        self.films = self.film_titles
    '''
        
    
class Films(BaseModel):
    RESOURCE_NAME = 'films'
    QUERY_SET_NAME = 'FilmsQuerySet'

    #def __init__(self, json_data):
    #      super(Films, self).__init__(json_data)

    def __repr__(self):
        self.title = self.title.encode('utf8', 'ignore')
        return 'Film: {0}'.format(self.title)
        
# the following section iterates with individual API calls       
class BaseQuerySet(object):
    
    def __init__(self):
        self.object_index = 0 # index counter to access each object 1 at a time
        self.n_objects = self.count() # the # of objects we need to find
        self.found = 0 # keep track of how many we have found 
        # we used found to account for missing obejcts
        # for example the People ID #17 is missing

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self.found >= self.n_objects: # end when we have found all objects
            raise StopIteration
            
        self.object_index += 1
        try:  
            current_object = self.parent.get(self.object_index)
            self.found += 1
            return current_object
        except SWAPIClientError: # in case of a missing object          
            return next(self) # continue to the next object
            
    next = __next__
            
    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        # for example: api_client.get_people()['count']
        return getattr(api_client, 'get_{}'.format(self.RESOURCE_NAME))()['count'] 

# I tried an alternate way to go page by page
# It utilizes a function get_page which I added to client.py
# It works with the actual SWAPI but on the test case stays stuck on page 1
# I can't figure out what is going on with the test
# When it has the url of the 2nd page it still is retrieving the 1st page...
'''
class BaseQuerySet(object):

    def __init__(self):
        self.current_url = 'http://swapi.co/api/{}/?page=1'.format(self.RESOURCE_NAME)
        self.get_page_results()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            current_object = self.parent(self.results_attr[self.results_index])
            # ie People(json)
            self.results_index += 1
            return current_object
        except IndexError:
            if not self.next_attr:
                raise StopIteration
            self.current_url = self.next_attr
            self.get_page_results()
            return next(self)
            
    def get_page_results(self):
        page_data = api_client.get_page(self.current_url)
        for key, value in page_data.items():
            setattr(self, key + '_attr', value)
        if hasattr(self, 'detail'):
            raise StopIteration
        self.results_index = 0
        
    next = __next__
    
    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        # for example: api_client.get_people()['count']
        return getattr(api_client, 'get_{}'.format(self.RESOURCE_NAME))()['count'] 
'''
class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        self.parent = People
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        self.parent = Films
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))