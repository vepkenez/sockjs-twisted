==============
SockJS-Twisted
==============

A simple library for adding SockJS support to your twisted application.

Status
======

SockJS-Twisted passes all `SockJS-Protocol v0.3.3 <https://github.com/sockjs/sockjs-protocol>`_ tests,
and all `SockJS-Client qunit <https://github.com/sockjs/sockjs-client>`_ tests. It has been used in
production environments, and should be free of any critical bugs.

Usage
=====

Use ``txsockjs.factory.SockJSFactory`` to wrap your factories. That's it!

.. code-block:: python
    
    from twisted.internet import reactor
    from twisted.internet.protocol import Factory, Protocol
    from txsockjs.factory import SockJSFactory

    class HelloProtocol(Protocol):
        def connectionMade(self):
            self.transport.write('hello')
            self.transport.write('how are you?')

        def dataReceived(self, data):
            print data

    reactor.listenTCP(8080, SockJSFactory(Factory.forProtocol(HelloProtocol)))
    reactor.run()

There is nothing else to it, no special setup involved.

Do you want a secure connection? Use ``listenSSL()`` instead of ``listenTCP()``.

Advanced Usage
==============

For those who want to host multiple SockJS services off of one port,
``txsockjs.factory.SockJSMultiFactory`` is designed to handle routing for you.

.. code-block:: python

    from twisted.internet import reactor
    from twisted.internet.protocol import Factory, Protocol
    from txsockjs.factory import SockJSMultiFactory
    from txsockjs.utils import broadcast

    class EchoProtocol(Protocol):
        def dataReceived(self, data):
            self.transport.write(data)

    class ChatProtocol(Protocol):
        def connectionMade(self):
            if not hasattr(self.factory, "transports"):
                self.factory.transports = set()
            self.factory.transports.add(self.transport)

        def dataReceived(self, data):
            broadcast(data, self.factory.transports)

        def connectionLost(self, reason):
            self.factory.transports.remove(self.transport)

    f = SockJSMultiFactory()
    f.addFactory(Factory.forProtocol(EchoProtocol), "echo")
    f.addFactory(Factory.forProtocol(ChatProtocol), "chat")

    reactor.listenTCP(8080, f)
    reactor.run()

http://localhost:8080/echo and http://localhost:8080/chat will give you access
to your EchoFactory and ChatFactory.

Integration With Websites
=========================

It is possible to offer static resources, dynamic pages, and SockJS endpoints off of
a single port by using ``txsockjs.factory.SockJSResource``.

.. code-block:: python

    from twisted.internet import reactor
    from twisted.internet.protocol import Factory, Protocol
    from twisted.web import resource, server
    from txsockjs.factory import SockJSResource

    # EchoProtocol and ChatProtocol defined above

    root = resource.Resource()
    root.putChild("echo", SockJSResource(Factory.forProtocol(EchoProtocol)))
    root.putChild("chat", SockJSResource(Factory.forProtocol(ChatProtocol)))
    site = server.Site(root)

    reactor.listenTCP(8080, site)
    reactor.run()

Multiplexing [Experimental]
===========================

SockJS-Twisted also has built-in support for multiplexing. See the
`Websocket-Multiplex <https://github.com/sockjs/websocket-multiplex>`_ library
for how to integrate multiplexing client side.

.. code-block:: python

    from twisted.internet import reactor
    from twisted.internet.protocol import Factory, Protocol
    from twisted.web import resource, server
    from txsockjs.multiplex import SockJSMultiplexResource

    multiplex = SockJSMultiplexResource()
    multiplex.addFactory("echo", Factory.forProtocol(EchoProtocol))
    multiplex.addFactory("chat", Factory.forProtocol(ChatProtocol))

    root = resource.Resource()
    root.putChild("multiplex", multiplex)
    site = server.Site(root)

    reactor.listenTCP(8080, site)
    reactor.run()

Single factory? Multifactory? Resource? Multiplexing? What's the difference?
============================================================================

+-------------------------+--------------------+----------------------------------+--------------------------+
| Type                    | Factories per port | Allows mixing native web content | Factories per connection |
+=========================+====================+==================================+==========================+
| SockJSFactory           | Single             | No                               | Single                   |
+-------------------------+--------------------+----------------------------------+--------------------------+
| SockJSMultiFactory      | Multiple           | No                               | Single                   |
+-------------------------+--------------------+----------------------------------+--------------------------+
| SockJSResource          | Multiple           | Yes                              | Single                   |
+-------------------------+--------------------+----------------------------------+--------------------------+
| SockJSMultiplexResource | Multiple           | Yes                              | Multiple                 |
+-------------------------+--------------------+----------------------------------+--------------------------+

``SockJSFactory`` is recommended for use in non-web (HTTP) applications to allow
native web connections. For instance, an IRC server. There can only be one factory
listening on a port using this method. The SockJS endpoint uses this internally.

``SockJSMultiFactory`` is recommended for use in non-web (HTTP) applications with
multiple services. This allows multiple factories to listen on a single port.

``SockJSResource`` is recommended for use in HTTP based applications, like webservers.

``SockJSMultiplexResource`` is recommended for pubsub applications, where each connection
needs to talk to multiple factories. Overriding the subscribe method allows for dynamic
factory creation if you don't know what is needed server-side ahead of time.

Endpoints
=========

For integration with pre-existing libraries or programs, it is possible use sockjs
as an endpoint in the form ``sockjs:tcp\:9090\:interface\=0.0.0.0:encoding=utf8:websocket=false``.
You can pass any escaped endpoint to a sockjs endpoint to wrap it with txsockjs, and you can
specify any option for the SockJSFactory by specifying it as a keyword argument.
For more information, read the
`twisted documentation on endpoints <http://twistedmatrix.com/documents/current/core/howto/endpoints.html>`_.

.. code-block:: python

    from twisted.internet import reactor
    from twisted.internet.protocol import Factory, Protocol
    from twisted.internet.endpoints import serverFromString
    # Note that we don't have to import anything from txsockjs

    # HelloProtocol defined above

    endpoint = serverFromString(reactor, "sockjs:tcp\:8080")
    endpoint.listen(Factory.forProtocol(HelloProtocol))
    reactor.run()

Options
=======

A dictionary of options can be passed into the factory to control SockJS behavior.

.. code-block:: python

    options = {
        'websocket': True,
        'cookie_needed': False,
        'heartbeat': 25,
        'timeout': 5,
        'streaming_limit': 128 * 1024,
        'encoding': 'cp1252', # Latin1
        'sockjs_url': 'https://d1fxtkz8shb9d2.cloudfront.net/sockjs-0.3.js',
        'proxy_header': None
    }
    SockJSFactory(factory_to_wrap, options)
    SockJSMultiFactory().addFactory(factory_to_wrap, prefix, options)
    SockJSResource(factory_to_wrap, options)
    SockJSMultiplexResource(options)

websocket :
    whether websockets are supported as a protocol. Useful for proxies or load balancers that don't support websockets.

cookie_needed :
    whether the JSESSIONID cookie is set. Results in less performant protocols being used, so don't require them unless your load balancer requires it.

heartbeat :
    how often a heartbeat message is sent to keep the connection open. Do not increase this unless you know what you are doing.

timeout :
    maximum delay between connections before the underlying protocol is disconnected

streaming_limit :
    how many bytes can be sent over a streaming protocol before it is cycled. Allows browser-side garbage collection to lower RAM usage.

encoding :
    All messages to and from txsockjs should be valid UTF-8. In the event that a message received by txsockjs is not UTF-8, fall back to this encoding.

sockjs_url :
    The url of the SockJS library to use in iframes. By default this is served over HTTPS and therefore shouldn't need changing.

proxy_header :
    The HTTP header to pull a proxied IP address out of. Leave as None to get the unproxied IP. **Do not change this unless you are behind a proxy you control.**

License
=======

SockJS-Twisted is (c) 2012 Christopher Gamble and is made available under the BSD license.
