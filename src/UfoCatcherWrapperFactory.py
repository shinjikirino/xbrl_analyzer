import TDnetCatcher
import EDINETCatcher
# import MockCatcher

class UfoCatcherWrapperFactory:
    def __init__(self):
        pass
    def create(self, wrapper_type):
        if wrapper_type == "TDnet":
            return TDnetCatcher.TDnetCatcher()
        elif wrapper_type == "EDINET":
            return EDINETCatcher.EDINETCatcher()
        # else:
        #     return MockCatcher()


