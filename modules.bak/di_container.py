import logging

class DIContainer:
    _services = {}

    @classmethod
    def register(cls, interface, implementation, *, singleton=True):
        cls._services[interface] = {
            'implementation': implementation,
            'singleton': singleton,
            'instance': None
        }
        logging.debug(f"Service registered for {interface} with singleton={singleton}")

    @classmethod
    def resolve(cls, interface):
        service = cls._services.get(interface)
        if service is None:
            error_msg = f"Service for interface {interface} not registered."
            logging.error(error_msg)
            raise ValueError(error_msg)
        if service['singleton']:
            if service['instance'] is None:
                if isinstance(service['implementation'], type):
                    service['instance'] = service['implementation']()
                else:
                    service['instance'] = service['implementation']
                logging.debug(f"Created singleton instance for {interface}")
            return service['instance']
        else:
            if isinstance(service['implementation'], type):
                logging.debug(f"Created new instance for {interface}")
                return service['implementation']()
            else:
                return service['implementation']
