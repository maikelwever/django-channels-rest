Django Channels Rest
====================


Django Channels Rest provides helpers so
you can do $.ajax like requests over a Django channels
websocket to django-rest-framework views.


Warning
-------

This code feels to me like one big hack, probably because it is. Use with caution.


Feedback
--------

Open a GitHub issue and I will take a look at your comments.


Installation
------------

Add `'channels_rest'` to `INSTALLED_APPS`.

Setup a consumer like this:

.. code-block:: python

    from channels.auth import channel_session_user, channel_session_user_from_http
    from channels_rest import process_rest_request, enable_rest_request_session

    from example.rest_router import router

    @channel_session_user_from_http
    def ws_connected(message):
        enable_rest_request_session(message)

    @channel_session_user
    def ws_received(message):
        if process_rest_request(message, urls=router.urls):  # Leave urls empty to use settings.ROOT_URLCONF.
            logger.debug("Request was handled by rest routing")
            return


And setup the JS framework like this:

.. code-block:: jinja

    <html>
        <head>
            <title>Django-channels-rest test</title>
            <script src="{% static 'channels_rest.js' %}"></script>
        </head>
        <body>
            <h1>My awesome webpage.</h1>

            <script>
                $(function() {
                    var socket = new WebSocket("ws://localhost:8000/ws/url/");

                    CCR.init(function(data) {
                        socket.send(data);
                    });

                    socket.onmessage = function(message) {
                        var payload = JSON.parse(message.data);
                        if (payload['datatype'] == 'request') {
                            CCR.parse(payload);
                        }
                    };
                });
            </script>
        </body>
    </html>


Usage
-----

.. code-block:: javascript
    
    CCR.get('/polls/', function(data, status_code) {
        // data is the JSON response from django-rest-framework.
        // status_code represents the HTTP status code.
    });
