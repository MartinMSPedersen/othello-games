import logging
import sys

# Try to import colorama for colored terminal output
try:
    from termcolor import colored
    COLOR_ENABLED = True
except ImportError:
    COLOR_ENABLED = False
    def colored(text, _, attrs=None):
        return text

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors and timestamps"""
    
    FORMATS = {
        logging.DEBUG: colored("DEBUG: %(message)s", "cyan"),
        logging.INFO: colored("%(message)s", "green"),
        logging.WARNING: colored("WARNING: %(message)s", 'yellow'),
        logging.ERROR: colored("ERROR: %(message)s", "red"),
        logging.CRITICAL: colored("CRITICAL: %(message)s", "red", attrs=["reverse", "blink"]),
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Configure root logger first
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
if not root_logger.handlers:
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)


def configure_logging(debug=False, no_timestamps=False):
    """Configure global logging settings"""
    # Configure root logger
    root_logger = logging.getLogger()
    
    # Set level based on debug flag
    if debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Set formatter
    if no_timestamps:
        formatter = logging.Formatter('%(levelname)s: %(message)s')
    else:
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)


def setup_logger(name, debug=False, log_file=None):
    """Set up and return a logger with the given name.
    
    Args:
        name: Logger name (usually module name)
        debug: Whether to enable debug mode
        log_file: Optional file path to write logs to
        
    Returns:
        logging.Logger: Configured logger
    """
    # Set global level to debug if debug is enabled for any module
    if debug:
        root_logger.setLevel(logging.DEBUG)
    
    # Get or create module logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    
    # Don't propagate to root logger since we'll configure handlers directly
    logger.propagate = False
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Add console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # File handler if log_file is provided
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_format = logging.Formatter(
            "[%(asctime)s] [%(name)s] %(levelname)s: %(message)s", 
            datefmt="%Y-%m-%d %H:%M:%S"
            )
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)
    
    return logger
