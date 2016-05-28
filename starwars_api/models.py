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
       
        
class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'
    QUERY_SET_NAME = 'PeopleQuerySet'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        self.name = self.name.encode('utf8', 'ignore')
        return 'Person: {0}'.format(self.name)

class Films(BaseModel):
    RESOURCE_NAME = 'films'
    QUERY_SET_NAME = 'FilmsQuerySet'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        self.title = self.title.encode('utf8', 'ignore')
        return 'Film: {0}'.format(self.title)#.encode('utf8', 'ignore')
        
class BaseQuerySet(object):

    def __init__(self):
        self.current_resource = 1
        self.max_count = self.count()
        self.found = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        if self.found >= self.max_count:
            raise StopIteration

        try:  
            json_data = getattr(api_client, 'get_' + self.RESOURCE_NAME)(self.current_resource)
            self.current_resource += 1
            self.found += 1
            return self.parent(json_data)
        except SWAPIClientError:            
            self.current_resource += 1
            return next(self)
            
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