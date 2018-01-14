class State(object):
    """
    Definition of a state object which provides some utility functions for the individual states within the state machin
    """

    def __init__(self):
        print('Processing current state:', str(self))

    def on_event(self, event):
        """
        Handle events that are delegated to this state.
        """
        pass
    def __repr__(self):
        """
        Leverages the __str__ method to describe the State.
        """
        return self.__str__()
    def __str__(self):
        """
        Returns the name of the state.
        """
        return self.__class__.__name__
