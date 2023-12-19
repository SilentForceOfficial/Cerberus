from neo4j import AsyncGraphDatabase, AsyncDriver

# def init_driver(ip, port, scheme, user, password) -> AsyncDriver:
#     uri = "{}://{}:{}".format(scheme, ip, port)
#     driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
#     return driver

def init_driver(uri, user, password) -> AsyncDriver:
    uri = uri
    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
    return driver

