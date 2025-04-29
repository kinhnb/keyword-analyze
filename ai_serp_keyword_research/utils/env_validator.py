"""
Environment variable validation utilities.

This module provides functions for validating and securely loading
environment variables with proper type conversion and validation.
"""

import os
import logging
import re
from typing import Any, Dict, List, Optional, Set, Union, Callable, TypeVar

# Configure logging
logger = logging.getLogger(__name__)

# Type variable for generic type hints
T = TypeVar('T')

class EnvironmentValidationError(Exception):
    """Raised when environment variables fail validation."""
    pass


def validate_env_var(
    name: str, 
    required: bool = False, 
    default: Optional[str] = None,
    validator: Optional[Callable[[str], bool]] = None,
    error_message: Optional[str] = None
) -> Optional[str]:
    """
    Validate an environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        validator: Optional function to validate the value
        error_message: Custom error message on validation failure
        
    Returns:
        The validated environment variable value
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    value = os.getenv(name)
    
    # Check if required variable is missing
    if required and value is None:
        if default is not None:
            logger.warning(f"Required environment variable {name} not set, using default value")
            return default
        raise EnvironmentValidationError(f"Required environment variable {name} not set")
    
    # If not required and not set, return default
    if value is None:
        return default
    
    # Validate if validator is provided
    if validator and not validator(value):
        msg = error_message or f"Environment variable {name} failed validation"
        raise EnvironmentValidationError(msg)
    
    return value


def get_env_int(
    name: str, 
    required: bool = False, 
    default: Optional[int] = None,
    min_value: Optional[int] = None,
    max_value: Optional[int] = None
) -> Optional[int]:
    """
    Get an integer environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        The environment variable as an integer
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    def _validator(value: str) -> bool:
        try:
            val_int = int(value)
            if min_value is not None and val_int < min_value:
                return False
            if max_value is not None and val_int > max_value:
                return False
            return True
        except ValueError:
            return False
    
    error_message = f"Environment variable {name} must be an integer"
    if min_value is not None and max_value is not None:
        error_message += f" between {min_value} and {max_value}"
    elif min_value is not None:
        error_message += f" greater than or equal to {min_value}"
    elif max_value is not None:
        error_message += f" less than or equal to {max_value}"
    
    value = validate_env_var(name, required, str(default) if default is not None else None, 
                            _validator, error_message)
    
    if value is None:
        return default
    
    return int(value)


def get_env_float(
    name: str, 
    required: bool = False, 
    default: Optional[float] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None
) -> Optional[float]:
    """
    Get a float environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        The environment variable as a float
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    def _validator(value: str) -> bool:
        try:
            val_float = float(value)
            if min_value is not None and val_float < min_value:
                return False
            if max_value is not None and val_float > max_value:
                return False
            return True
        except ValueError:
            return False
    
    error_message = f"Environment variable {name} must be a float"
    if min_value is not None and max_value is not None:
        error_message += f" between {min_value} and {max_value}"
    elif min_value is not None:
        error_message += f" greater than or equal to {min_value}"
    elif max_value is not None:
        error_message += f" less than or equal to {max_value}"
    
    value = validate_env_var(name, required, str(default) if default is not None else None, 
                            _validator, error_message)
    
    if value is None:
        return default
    
    return float(value)


def get_env_bool(
    name: str, 
    required: bool = False, 
    default: Optional[bool] = None
) -> Optional[bool]:
    """
    Get a boolean environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        
    Returns:
        The environment variable as a boolean
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    def _validator(value: str) -> bool:
        return value.lower() in ('true', 'false', '1', '0', 'yes', 'no')
    
    error_message = f"Environment variable {name} must be a boolean (true/false/1/0/yes/no)"
    
    value = validate_env_var(name, required, str(default).lower() if default is not None else None, 
                            _validator, error_message)
    
    if value is None:
        return default
    
    return value.lower() in ('true', '1', 'yes')


def get_env_list(
    name: str, 
    required: bool = False, 
    default: Optional[List[str]] = None,
    separator: str = ','
) -> Optional[List[str]]:
    """
    Get a list environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        separator: Character to split the string on
        
    Returns:
        The environment variable as a list
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    value = validate_env_var(name, required, ','.join(default) if default is not None else None)
    
    if value is None or value == '':
        return default or []
    
    return [item.strip() for item in value.split(separator) if item.strip()]


def get_env_url(
    name: str, 
    required: bool = False, 
    default: Optional[str] = None,
    allowed_schemes: Optional[List[str]] = None
) -> Optional[str]:
    """
    Get a URL environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        allowed_schemes: List of allowed URL schemes
        
    Returns:
        The environment variable as a validated URL
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    # Simple URL validation regex
    url_regex = r'^(https?|redis|postgresql|file|s3):\/\/[^\s/$.?#].[^\s]*$'
    
    def _validator(value: str) -> bool:
        if not re.match(url_regex, value):
            return False
        
        if allowed_schemes:
            scheme = value.split('://')[0].lower()
            return scheme in allowed_schemes
            
        return True
    
    schemes_str = ", ".join(allowed_schemes) if allowed_schemes else "any"
    error_message = f"Environment variable {name} must be a valid URL with scheme: {schemes_str}"
    
    return validate_env_var(name, required, default, _validator, error_message)


def get_env_api_key(
    name: str, 
    required: bool = False, 
    default: Optional[str] = None,
    min_length: int = 8
) -> Optional[str]:
    """
    Get an API key environment variable.
    
    Args:
        name: The name of the environment variable
        required: Whether the variable is required
        default: Default value if the variable is not set
        min_length: Minimum length for the API key
        
    Returns:
        The environment variable as a validated API key
        
    Raises:
        EnvironmentValidationError: If validation fails
    """
    def _validator(value: str) -> bool:
        # API keys should be at least min_length characters
        if len(value) < min_length:
            return False
        return True
    
    error_message = f"Environment variable {name} must be a valid API key (at least {min_length} characters)"
    
    value = validate_env_var(name, required, default, _validator, error_message)
    
    if value is not None:
        # Log only the presence of the API key, not the value itself
        masked_key = value[:4] + '*' * (len(value) - 4) if len(value) > 4 else '****'
        logger.info(f"API key {name} loaded: {masked_key}")
    
    return value


def validate_environment(required_vars: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Validate multiple environment variables at once.
    
    Args:
        required_vars: List of dictionaries with validation parameters
            Each dictionary should contain:
            - name: The name of the environment variable
            - type: The type of the variable ('str', 'int', 'float', 'bool', 'list', 'url', 'api_key')
            - required: Whether the variable is required
            - default: Default value if the variable is not set
            - additional type-specific parameters
            
    Returns:
        Dictionary of validated environment variables
        
    Raises:
        EnvironmentValidationError: If any validation fails
    """
    result = {}
    errors = []
    
    type_getters = {
        'str': validate_env_var,
        'int': get_env_int,
        'float': get_env_float,
        'bool': get_env_bool,
        'list': get_env_list,
        'url': get_env_url,
        'api_key': get_env_api_key
    }
    
    for var_config in required_vars:
        name = var_config.pop('name')
        var_type = var_config.pop('type', 'str')
        
        try:
            if var_type not in type_getters:
                errors.append(f"Unknown variable type '{var_type}' for {name}")
                continue
                
            getter = type_getters[var_type]
            result[name] = getter(name, **var_config)
        except EnvironmentValidationError as e:
            errors.append(str(e))
    
    if errors:
        error_message = f"Environment validation failed:\n" + '\n'.join(errors)
        logger.error(error_message)
        raise EnvironmentValidationError(error_message)
    
    return result 