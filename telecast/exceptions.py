class RPCError(Exception):
    """
    Generic RPC exception.
    Thrown when an RPC request was not completed for some reason.
    """
    pass


class RPCRemoteError(RPCError):
    """
    Should be raised manually by developer from an RPC method
    if a predictable exception occurs that should be propagated to a caller.
    This exception will be serialized, sent as response and re-raised
    on caller side with the same message.
    """
    pass


class RPCNotAllowedError(RPCError):
    """
    Raised on server end and reraised on client end if caller
    is not allowed to call a specific method.
    """


class RPCProtocolError(RPCError):
    """
    Raised on client end if an unknown response was received.
    Indicates that the called URL does not represent
    a valid RPC endpoint or that the callee network was down.
    """
    pass
