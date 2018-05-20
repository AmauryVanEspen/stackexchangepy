StackExchangePy
===============

.. image:: https://s7.postimg.cc/k6s2galrf/pylogo.png


.. image:: https://img.shields.io/pypi/v/stackexchangepy.svg?style=flat-square   :alt: PyPI
.. image:: https://img.shields.io/pypi/l/sctakexchangepy.svg?style=flat-square   :alt: PyPI - License

StackExchange API Wrapper, written in Python3.

*   Installation

            Type `pip3 install stackexchangepy` in your cli.

*   Usage

            Usage can be seen in the documentation of the package.


*   Examples
   

    * Answers

    >>> from stackexchangepy.client import ExchangeClient
    >>> import datetime as dt
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> answers = client. \
    >>>             answers(). \
    >>>             fromdate(dt.datetime.today()). \
    >>>             order('desc'). \
    >>>             get()
    >>>
    >>> answers[0].answer_id
    123456
    >>> answers[0].owner.display_name
    User
    >>> answers[0].score
    1000
    >>> answers[0].is_accepted
    True
    >>>
    >>> questions = client. \
    >>>             answers(). \
    >>>             questions(). \
    >>>             get()
    >>>
    >>> questions[0].answers_count
    1
    >>> questions[0].is_answers
    False
    >>>



    * Badges

    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> badges = client. \
    >>>          badges(). \
    >>>          get()
    >>>
    >>> badges[0].award_count
    1
    >>> badges[0].user.display_name
    User
    >>> badges[0].rank
    gold
    >>>
    >>>
    >>> # By ID
    >>> badges = client. \
    >>>          badges(1, 2, 3). \
    >>>          get()
    
    * Comments
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> import datetime as dt
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> comments = client. \
    >>>            comments(). \
    >>>            get()
    >>>
    >>> comments[0].comment_id
    12345678
    >>> comments[0].owner.display_name
    User
    >>> comments[0].score
    1
    >>>
    
    * Events
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> events = client. \
    >>>          events(). \
    >>>          get()
    >>>
    >>> events[0].id
    1
    >>> events[0].event_type
    comment_posted
    >>>
    
    * Info
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> info = client. \
    >>>        info(). \
    >>>        get()
    >>>
    >>> info.answers_per_minute
    100000
    >>> info.total_questions
    1
    >>> info.total_votes
    1
    >>>
    
    * Posts
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> posts = client. \
    >>>         posts(). \
    >>>         get()
    >>>
    >>> posts[0].owner.display_name
    User
    >>> posts[0].score
    1
    >>>
    
    * Privileges
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> privileges = client. \
    >>>              privileges(). \
    >>>              get()
    >>>
    >>> privileges[0].description
    Ask and answer questions
    >>> privileges[0].short_description
    create posts
    >>> privileges[0].reputation
    1
    >>>
    
    * Questions
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> questions = client. \
    >>>             questions(). \
    >>>             get()
    >>>
    >>> questions[0].answer_count
    1
    >>> questions[0].owner.display_name
    User
    >>> questions[0].question_id
    1
    >>>
    
    * Revisions
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> revisions = client. \
    >>>             revisions(1, 2, 3). \
    >>>             get()
    >>>
    >>> revisions[0].creation_date
    1526649575
    >>> revisions[0].last_body
    preceding body
    >>> revisions[0].last_title
    Old title
    >>>
    
    * Search
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> questions = client. \
    >>>            search(). \
    >>>            page(3). \
    >>>            pagesize(100). \
    >>>            intitle("Python"). \
    >>>            sort('creation'). \
    >>>            get()
    >>>
    >>> questions[0].owner.display_name
    User
    >>> questions[0].question_id
    1
    >>> # Advanced search
    >>> questions = client. \
    >>>             search(). \
    >>>             advanced(). \
    >>>             accepted(True). \
    >>>             closed(False). \
    >>>             wiki(True). \
    >>>             title("Python"). \
    >>>             get()
    >>>
    >>> # Similar questions
    >>> questions = client. \
    >>>             similar(). \
    >>>             title("Python"). \
    >>>             get()
    >>>
    >>> # Search excerpts
    >>>
    >>> questions = client. \
    >>>             search(). \
    >>>             excerpts(). \
    >>>             accepted(True). \
    >>>             closed(False). \
    >>>             get()
    >>>
    

    * Suggested edits
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>>
    >>> edits = client. \
    >>>         suggested_edits(). \
    >>>         get()
    >>>
    >>> edits[0].comment
    This is a comment
    >>> edits[0].title
    Python
    >>> edits[0].tags
    ["python", "python-3"]
    >>>
    
    * Tags
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>> 
    >>> tags = client. \
    >>>        tags(). \
    >>>        get()
    >>>
    >>> tags[0].count
    1
    >>> tags[0].name
    python
    >>> tags[0].user_id
    1
    >>>
    
    * Users
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> 
    >>>
    >>> client = ExchangeClient()
    >>> 
    >>> users = client. \
    >>>         users(). \
    >>>         get()
    >>>
    >>> users[0].display_name
    User
    >>> users[0].user_id
    1
    >>> me = client. \
    >>>       me(). \
    >>>       get()
    >>>
    
    * Network methods
    
    >>> from stackexchangepy.client import ExchangeClient
    >>> import os
    >>>
    >>> ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')
    >>> KEY = os.getenv('KEY')
    >>> 
    >>> client = ExchangeClient(access_token=ACCESS_TOKEN, key=KEY)
    >>> 
    >>> tokens = client. \
    >>>          access_tokens("token1", "token2", "token3"). \
    >>>                 
    >>> tokens[0].access_token
    abcd*(01234
    >>> tokens[0].expires_on_date
    1526737772
    >>>
    >>> errors = client. \
    >>>          errors(). \
    >>>          get()
    >>>
    >>> errors[0].description
    Description
    >>> errors[0].error_id
    123456
    >>>
    >>> inbox = client. \
    >>>         inbox(). \
    >>>         get()
    >>> 
    >>> inbox[0].answer_id
    12345
    >>> inbox[0].comment_id
    13567
    >>> inbox[0].title
    Some title
    >>>
    >>> notifications = client. \
    >>>                 notificaions(). \
    >>>                 get()
    >>>
    >>> notifications[0].body
    Body of the notification
    >>> notificatifications[0].is_unread
    True
    >>> notifications[0].creation_date
    1526737772
    >>>
    >>> sites = client. \
    >>>         sites(). \
    >>>         get()
    >>>
    >>> sites[0].launch_date
    1526651705
    >>> sites[0].twitter_account
    @StackExchange
    >>> sites[0].name
    Name of the site
    >>>
    
 * LICENSE
 
    GPL-3.0