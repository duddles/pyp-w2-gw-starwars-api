from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.iteritems():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        json_data =getattr(api_client, 'get_' + cls.RESOURCE_NAME)(resource_id)
        return cls(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        # import ipdb; ipdb.set_trace()

        return globals()[cls.QUERY_SET_NAME]()
        # return eval(cls.QUERY_SET_NAME)
        #return cls.QUERY_SET_NAME()
        #print cls
        #if isinstance(cls, People):
            #return PeopleQuerySet()
        #return FilmsQuerySet()
        #json_data =getattr(api_client, 'get_' + cls.RESOURCE_NAME)()
        # this is a dict with count, next, previous, results
        # i think we want to make a PeopleQuerySet or FilmQuerySet 
        #queryset = # but I am not sure how to call it...
        
class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'
    QUERY_SET_NAME = 'PeopleQuerySet'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        try: 
            return 'Person: {0}'.format(self.name)
        except UnicodeEncodeError:
            return 'Name with unicode error'


class Films(BaseModel):
    RESOURCE_NAME = 'films'
    QUERY_SET_NAME = 'FilmsQuerySet'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        try:
            return 'Film: {0}'.format(self.title)
        except UnicodeEncodeError:
            return 'Name with unicode error'

class BaseQuerySet(object):

    def __init__(self):
        self.current_resource = 0
        self.max_count = self.count()

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self.current_resource >= self.max_count:
            raise StopIteration
        self.current_resource += 1
        try:  
            json_data = getattr(api_client, 'get_' + self.RESOURCE_NAME)(self.current_resource)
            return self.parent(json_data)
        except SWAPIClientError:            
            pass
            
    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return getattr(api_client, 'get_' + self.RESOURCE_NAME)()['count'] 


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