#!/usr/bin/env python
# coding:utf-8
#############################################
# -author:shaw                              #
# -date:2025-03-18                          #
#############################################

import os
import sys
import logging
import xml.etree.ElementTree as ET
from collections import defaultdict, namedtuple
import time


# Get the absolute path of the current file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Add the deploy directory to sys.path
sys.path.append(current_dir)
sys.path.append(os.path.dirname(current_dir))

from xfunc import XFunc

# Python 2/3 compatibility
PY2 = sys.version_info[0] == 2
if PY2:
    from io import open

    text_type = unicode  # type: ignore
    binary_type = str
else:
    text_type = str
    binary_type = bytes


# Global logger instance
from xlog import XLogger

logger = XLogger()


# Helper functions (Python 2/3 compatible)
def LOG_DEBUG(message, *args):
    logger.debug(message, *args)


def LOG_INFO(message, *args):
    logger.info(message, *args)


def LOG_WARNING(message, *args):
    logger.warning(message, *args)


def LOG_ERROR(message, *args):
    logger.error(message, *args)


def LOG_CRITICAL(message, *args):
    logger.critical(message, *args)


class XConfigParser(object):
    """Enhanced XML configuration parser with Python 2/3 compatibility."""

    def __init__(self, xml_file, encoding="utf-8"):
        """
        Initialize XML config parser with robust cross-version support.

        Args:
            xml_file (str): Path to the XML configuration file
            encoding (str): File encoding to use (default: utf-8)
        """
        self.xml_file = os.path.abspath(xml_file)
        self.encoding = encoding
        self.tree = None
        self.root = None

        # Define XML framework with proper encoding
        self.BASE_FRAMEWORK = text_type(
            """<?xml version='1.0' encoding='{enc}'?>
<root>
    <!-- Configuration entries will be added here -->
</root>"""
        ).format(enc=self.encoding)

        self._initialize_config()
        self.init_log_from_file(config_file=self.xml_file)

    def init_log_from_file(self, config_file, user_class=None, log_format=None):
        log_configs = self.get_config_data(
            section="log",
            config_class=self.create_config_class("log", XLogger.log_config_def),
        )

        log_config = (
            log_configs.get("log", [{}])[0]  # Get first config or empty dict
            if log_configs and isinstance(log_configs, dict)
            else {}
        )

        logger.init_log(log_config, user_class, log_format)

    def _initialize_config(self):
        """Initialize the XML configuration with version-specific handling."""
        try:
            if self._file_exists():
                self._load_existing_config()
            else:
                self._create_new_config()

        except ET.ParseError as e:
            logging.error("XML parsing error in %s: %s", self.xml_file, str(e))
            # self._handle_corrupted_file()
        except Exception as e:
            logging.error("Unexpected error initializing config: %s", str(e))
            # self._create_fallback_framework()

    def _file_exists(self):
        """Check if config file exists and is valid (cross-version)."""
        return (
            (os.path.exists(self.xml_file))
            and (os.path.isfile(self.xml_file))
            and (os.path.getsize(self.xml_file) > 0)
        )

    def _load_existing_config(self):
        """Load existing XML config file with version-specific parsing."""
        logging.debug("Loading existing XML file: %s", self.xml_file)

        # Python 2/3 compatible parsing
        with open(self.xml_file, "rb") as f:
            if PY2:
                # Python 2 needs special handling for encoding
                parser = ET.XMLParser(encoding=self.encoding)
                self.tree = ET.parse(f, parser=parser)
            else:
                # Python 3 handles encoding better
                self.tree = ET.parse(f)

        self.root = self.tree.getroot()

        # Validate basic structure
        if self.root is None or self.root.tag != "root":
            raise ET.ParseError("Invalid root element or missing root tag")

    def _create_new_config(self):
        """Create new XML config file with directory creation."""
        logging.info("Creating new XML config file: %s", self.xml_file)

        # Ensure directory exists (Python 2/3 compatible)
        try:
            os.makedirs(os.path.dirname(self.xml_file))
        except OSError:
            if not os.path.isdir(os.path.dirname(self.xml_file)):
                raise

        # Create new config with version-specific writing
        self.root = ET.fromstring(self.BASE_FRAMEWORK)
        self.tree = ET.ElementTree(self.root)

        # Python 2/3 compatible file writing
        with open(self.xml_file, "wb") as f:
            if PY2:
                f.write(self.BASE_FRAMEWORK.encode(self.encoding))
            else:
                self.tree.write(f, encoding=self.encoding, xml_declaration=True)

    def _handle_corrupted_file(self):
        """Handle corrupted XML file by creating backup and new config."""
        try:
            # Create backup of corrupted file
            backup_file = "%s.corrupted.%d" % (self.xml_file, int(time.time()))
            os.rename(self.xml_file, backup_file)
            logging.warning("Created backup of corrupted file: %s", backup_file)
        except Exception as e:
            logging.error("Failed to create backup: %s", str(e))

        # Create fresh config
        self._create_new_config()

    def _create_fallback_framework(self):
        """Create in-memory basic framework when file operations fail."""
        try:
            self.root = ET.fromstring(self.BASE_FRAMEWORK)
            self.tree = ET.ElementTree(self.root)
            logging.warning("Using in-memory configuration framework")
        except Exception as e:
            logging.error("Failed to create fallback framework: %s", str(e))
            self.root = None
            self.tree = None

    def _save_to_file(self, pretty_print=True):
        """
        Save the XML tree to file with version-specific handling.

        Args:
            pretty_print (bool): Whether to format the XML output

        Returns:
            bool: True if save was successful
        """
        if self.tree is None or self.root is None:
            return False

        try:
            # Atomic write using temp file (cross-version)
            temp_file = "%s.tmp" % self.xml_file

            if pretty_print:
                self._indent(self.root)
                if PY2:
                    xml_str = ET.tostring(self.root, encoding=self.encoding)
                    with open(temp_file, "wb") as f:
                        f.write(xml_str)
                else:
                    xml_str = ET.tostring(self.root, encoding=self.encoding)
                    with open(temp_file, "wb") as f:
                        f.write(xml_str)
            else:
                if PY2:
                    with open(temp_file, "wb") as f:
                        self.tree.write(f, encoding=self.encoding)
                else:
                    self.tree.write(
                        temp_file, encoding=self.encoding, xml_declaration=True
                    )

            # Replace original file (cross-platform)
            try:
                if os.path.exists(self.xml_file):
                    os.remove(self.xml_file)
                os.rename(temp_file, self.xml_file)
                return True
            except Exception as e:
                logging.error("File replacement failed: %s", str(e))
                return False

        except Exception as e:
            logging.error("Failed to save XML file: %s", str(e))
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass
            return False

    def _prettyXml(self, element, indent, newline, level=0):
        """Pretty-print XML element with proper indentation"""
        # Handle element text
        if element.text and not element.text.isspace():
            element.text = (
                newline
                + indent * (level + 1)
                + element.text.strip()
                + newline
                + indent * (level + 1)
            )
        elif not element.text:
            element.text = newline + indent * (level + 1)

        # Process child elements
        children = list(element)
        for i, subelement in enumerate(children):
            # Set tail for proper indentation
            subelement.tail = newline + indent * (
                level + 1 if i < len(children) - 1 else level
            )
            # Recursively process children
            self.prettyXml(subelement, indent, newline, level + 1)

    def _indent(self, elem, level=0, preserve_whitespace=False):
        """
        Robust recursive XML pretty-printer with proper type checking.

        Args:
            elem: XML element to format
            level: Current indentation level
            preserve_whitespace: Whether to keep existing whitespace

        Handles:
        - Regular elements
        - Comments
        - Processing instructions
        - Type checking edge cases
        """
        # Null check and type safety
        if elem is None:
            return

        # Proper type checking
        if not isinstance(elem, (ET.Element, ET.Comment, ET.ProcessingInstruction)):
            raise TypeError(
                "Expected Element, Comment, or ProcessingInstruction, got {}".format(
                    type(elem)
                )
            )

        indent = "    "
        i = "\n" + level * indent

        # Skip whitespace preservation if requested
        if preserve_whitespace and elem.text and elem.text.strip():
            return

        # Handle different element types
        if len(elem):  # Parent element
            if not preserve_whitespace or not elem.text or not elem.text.strip():
                elem.text = i + indent

            if not preserve_whitespace or not elem.tail or not elem.tail.strip():
                elem.tail = i

            # Process children
            for idx, child in enumerate(elem):
                self._indent(child, level + 1, preserve_whitespace)

                # Last child gets special treatment
                if idx == len(elem) - 1:
                    if (
                        not preserve_whitespace
                        or not child.tail
                        or not child.tail.strip()
                    ):
                        child.tail = i

        else:  # Leaf element
            if level and (
                not preserve_whitespace or not elem.tail or not elem.tail.strip()
            ):
                elem.tail = i

    def get_value(self, section, key, fallback=None, convert_type=None):
        """
        Retrieve a value from the XML configuration with type conversion.

        Args:
            section (str): The parent tag name
            key (str): The child tag name
            fallback: Default value if key not found
            convert_type: Type to convert the value to

        Returns:
            The converted value or fallback
        """
        if self.root is None:
            return fallback

        try:
            section_element = self.root.find(section)
            if section_element is None:
                return fallback

            key_element = section_element.find(key)
            if key_element is None:
                return fallback

            value = key_element.text
            if value is None:
                return fallback

            if convert_type is not None:
                # Special handling for boolean values
                if convert_type is bool:
                    return self._convert_bool(value)
                # Handle other types
                try:
                    return convert_type(value)
                except (ValueError, TypeError) as e:
                    logging.warning(
                        "Type conversion failed for '%s' to %s: %s",
                        value,
                        (
                            convert_type.__name__
                            if hasattr(convert_type, "__name__")
                            else str(convert_type)
                        ),
                        str(e),
                    )
                    return fallback
            return value
        except Exception as e:
            logging.error("Error getting value: %s", str(e))
            return fallback

    def _convert_bool(self, value):
        """Convert string to boolean (Python 2/3 compatible)."""
        if isinstance(value, text_type):
            value = value.lower()
        return value in ("true", "1", "yes", "on")

    def set_value(self, section, key, value):
        """
        Set a value in the XML configuration.

        Args:
            section (str): The parent tag name
            key (str): The child tag name
            value: The value to set

        Returns:
            bool: True if the operation was successful, False otherwise
        """
        if self.root is None:
            logging.error("No XML root element available")
            return False

        try:
            # Find or create the section
            section_element = self.root.find(section)
            if section_element is None:
                section_element = ET.SubElement(self.root, section)

            # Find or create the key
            key_element = section_element.find(key)
            if key_element is None:
                key_element = ET.SubElement(section_element, key)

            # Set the value
            key_element.text = str(value)

            # Save the changes
            return self._save_to_file()

        except Exception as e:
            logging.error("Error setting value: %s", str(e))
            return False

    def create_config_class(self, class_name, field_definitions):
        """
        Factory for creating configuration classes with Python 2/3 compatibility.

        Args:
            class_name (str): Name of the configuration class
            field_definitions: List of field definitions

        Returns:
            A namedtuple-based class with enhanced metadata
        """
        # Process field definitions
        processed_fields = []
        field_metadata = {"required": [], "defaults": {}, "types": {}}

        for field_def in field_definitions:
            # Parse field definition
            if isinstance(field_def, (tuple, list)):
                if len(field_def) == 4:  # (name, required, default, type)
                    name, req, default, ftype = field_def
                elif len(field_def) == 3:  # (name, required, default)
                    name, req, default = field_def
                    ftype = text_type
                elif len(field_def) == 2:  # (name, required)
                    name, req = field_def
                    default = None
                    ftype = text_type
                else:
                    raise ValueError("Invalid field definition format")
            else:  # Just field name
                name = field_def
                req = False
                default = None
                ftype = text_type

            processed_fields.append(name)
            if req:
                field_metadata["required"].append(name)
            if default is not None:
                field_metadata["defaults"][name] = default
            field_metadata["types"][name] = ftype

        # Create base namedtuple (Python 2/3 compatible)
        BaseClass = namedtuple("_" + class_name + "Base", processed_fields)

        # Create actual config class
        class ConfigClass(BaseClass):
            """Configuration class with enhanced metadata (Python 2/3 compatible)."""

            __slots__ = ()  # For memory efficiency in both versions

            # Field metadata
            _fields = processed_fields
            _required = field_metadata["required"]
            _defaults = field_metadata["defaults"]
            _types = field_metadata["types"]

            @classmethod
            def get_required_fields(cls):
                return cls._required

            @classmethod
            def get_field_default(cls, field):
                return cls._defaults.get(field)

            @classmethod
            def get_field_type(cls, field):
                return cls._types.get(field, text_type)

            def __new__(cls, **kwargs):
                # Apply defaults
                final_kwargs = {}
                for field in cls._fields:
                    if field in kwargs:
                        # Handle None value
                        if kwargs[field] is None:
                            final_kwargs[field] = None
                        else:
                            # Type conversion
                            try:
                                final_kwargs[field] = cls._types[field](kwargs[field])
                            except (ValueError, TypeError) as e:
                                raise ValueError(
                                    "Invalid value for {field}: {value} (expected {type})".format(
                                        field=field,
                                        value=kwargs[field],
                                        type=(
                                            cls._types[field].__name__
                                            if hasattr(cls._types[field], "__name__")
                                            else str(cls._types[field])
                                        ),
                                    )
                                )
                    elif field in cls._defaults:
                        final_kwargs[field] = cls._defaults[field]
                    elif field in cls._required:
                        raise ValueError("Missing required field: {0}".format(field))

                return super(ConfigClass, cls).__new__(cls, **final_kwargs)

        ConfigClass.__name__ = str(class_name)
        return ConfigClass

    # Additional utility methods with Python 2/3 compatibility
    def add_section(self, section, domain=None):
        """Add a new section to the configuration."""
        if self.root is None:
            return False

        # Check if section already exists
        if self.root.find(section) is not None:
            return False

        # Create new section
        new_section = ET.SubElement(self.root, section)
        if domain is not None:
            new_section.set("domain", domain)

        return self._save_to_file()

    def remove_section(self, section):
        """Remove a section from the configuration."""
        if self.root is None:
            return False

        section_element = self.root.find(section)
        if section_element is None:
            return False

        self.root.remove(section_element)
        return self._save_to_file()

    def get_config_data(
        self,
        section,
        config_class,
        subtag=None,
        type_conversion=None,
        domain=None,
        match_field=None,
        match_value=None,
    ):
        """
        Retrieve configuration data with flexible organization:
        - When domain=None: Organize by section {section_name: [configs]}
        - When domain="all": Organize by domain {domain_name: [configs]}
        - When domain=value: Get specific domain {domain_name: [configs]}

        Args:
            section: XML node path to query
            config_class: Named tuple class for results
            subtag: Child node tag name
            type_conversion: Type conversion dictionary
            domain: Organization control parameter
            match_field: Field name used for matching (default: "None")
            match_value: Field value used for matching (default: "None")

        Returns:
            Dictionary {organization_key: [configs]} or empty dict
        """
        if not hasattr(self, "root") or self.root is None:
            logging.warning("XML root element not initialized")
            return {}

        type_conversion = type_conversion or {}
        result_dict = defaultdict(list)

        section_elements = self.root.findall(section)
        if not section_elements:
            logging.warning("Config section not found: %s", section)
            return {}

        # Domain=None: Organize by section
        if domain is None:
            for sect in section_elements:
                elements = sect.findall(subtag) if subtag else [sect]
                for elem in elements:
                    config_data = self._extract_config_data(
                        elem, config_class, type_conversion
                    )
                    if config_data:
                        try:
                            result_dict[section].append(config_class(**config_data))
                        except Exception as e:
                            logging.error("Failed to create config object: %s", e)
            return dict(result_dict)

        # Domain specified: Organize by domain
        for sect in section_elements:
            current_domain = sect.get("domain", "default")

            # Skip non-matching domains for specific requests
            if domain != "all" and current_domain != domain:
                continue

            elements = sect.findall(subtag) if subtag else [sect]
            for elem in elements:
                config_data = self._extract_config_data(
                    elem, config_class, type_conversion
                )

                if config_data:
                    try:
                        if match_field:
                            field_value = config_data.get(match_field)
                            if not field_value:
                                logging.warning(
                                    "No match field '%s' found in config", match_field
                                )
                                continue
                            if field_value != match_value:
                                logging.warning(
                                    "Match field '%s' does not match '%s' != '%s'",
                                    match_field,
                                    field_value,
                                    match_value,
                                )
                                continue
                        result_dict[current_domain].append(config_class(**config_data))
                    except Exception as e:
                        logging.error("Failed to create config object: %s", e)

        return dict(result_dict)

    def print_config(self, result_dict):
        for domain, hosts_list in result_dict.items():
            print("Domain: {}, num: {}".format(domain, len(hosts_list)))
            print("\n" + "-" * 50 + "\n")
            for host in hosts_list:
                # Use config_class._fields instead of config_class
                config_class = host.__class__
                for field_name in config_class._fields:
                    field_value = getattr(host, field_name)
                    file_type = type(field_value).__name__
                    print("{} {} (type: {})".format(field_name, field_value, file_type))
                print("\n" + "-" * 50 + "\n")
            print("\n" + "=" * 50 + "\n")

    def _extract_config_data(self, element, config_class, type_conversion):
        """Extract and convert configuration data from XML element."""
        config_data = {}
        for field in config_class._fields:
            value_element = element.find(field)
            if value_element is None:
                # Use default value if field is not found
                if field in config_class._defaults:
                    config_data[field] = config_class._defaults[field]
                else:
                    config_data[field] = None
                continue

            text_value = value_element.text
            if field in type_conversion and text_value is not None:
                try:
                    config_data[field] = type_conversion[field](text_value)
                except (ValueError, TypeError) as e:
                    logging.warning(
                        "Type conversion failed for field '%s' (value: '%s'): %s",
                        field,
                        text_value,
                        str(e),
                    )
                    config_data[field] = text_value
            else:
                # Use config_class field type for conversion
                field_type = config_class._types.get(field, text_type)
                try:
                    # Special handling for boolean values
                    config_data[field] = (
                        self._convert_bool(text_value)
                        if field_type is bool
                        else (
                            field_type(text_value) if text_value is not None else None
                        )
                    )
                except (ValueError, TypeError) as e:
                    logging.warning(
                        "Type conversion failed for field '%s' (value: '%s'): %s",
                        field,
                        text_value,
                        str(e),
                    )
                    config_data[field] = text_value

        return config_data

    def set_config_data(
        self,
        section,
        config_data,
        subtag=None,
        domain=None,
        create_missing=True,
        match_field="name",
    ):
        """
        Set configuration data in the XML structure (Python 2/3 compatible)

        Args:
            section: Parent section to modify
            config_data: Dictionary, namedtuple, or list of configs to update
            subtag: Child tag name if applicable
            domain: Domain attribute to filter sections
            create_missing: Whether to create missing sections/tags
            match_field: Field used to match existing elements (default: "name")

        Returns:
            bool: True if successful, False otherwise
        """
        if self.root is None:
            logging.error("No XML root element available")
            return False

        # Find or create the target section
        section_elements = self.root.findall(section)
        target_section = None

        # Handle domain filtering
        if domain is not None and domain != "all":
            for sect in section_elements:
                if sect.get("domain") == domain:
                    target_section = sect
                    break
        elif section_elements:
            target_section = section_elements[0]  # Use first match

        # Create section if missing and allowed
        if target_section is None and create_missing:
            target_section = ET.SubElement(self.root, section)
            if domain is not None and domain != "all":
                target_section.set("domain", domain)

        if target_section is None:
            logging.error("Target section not found and creation not allowed")
            return False

        # Handle both single config (dict/namedtuple) and multiple configs (list)
        configs = config_data if isinstance(config_data, list) else [config_data]

        for config in configs:
            # Convert namedtuple to dict if necessary
            if hasattr(config, "_asdict"):
                config = config._asdict()

            # Find or create the target element
            target_element = None
            if subtag:
                # Find by matching the specified field (default: "name")
                for elem in target_section.findall(subtag):
                    if match_field in config and elem.find(match_field) is not None:
                        if elem.find(match_field).text == str(config[match_field]):
                            target_element = elem
                            break

                if target_element is None and create_missing:
                    target_element = ET.SubElement(target_section, subtag)
            else:
                target_element = target_section

            if target_element is None:
                logging.warning("Skipping config - no matching element found")
                continue

            # Update or create fields
            for field, value in config.items():
                field_elem = target_element.find(field)
                if field_elem is None:
                    if create_missing:
                        field_elem = ET.SubElement(target_element, field)
                    else:
                        continue
                field_elem.text = str(value)

        return self._save_to_file()

    def remove_config_data(
        self, section, config_data, subtag=None, domain=None, match_field="name"
    ):
        """
        Remove specified configuration data from XML structure.
        Removes the entire domain section if it becomes empty after deletions.

        Args:
            section: Parent node name
            config_data: Configuration data to delete (dict, namedtuple, or list)
            subtag: Subnode tag name (optional)
            domain: Domain attribute for filtering nodes (use "all" for all domains)
            match_field: Field used to match elements (default: "name")

        Returns:
            bool: True if deletion succeeded, False otherwise
        """
        # Input validation
        if not section or not config_data:
            logging.error("Invalid input: section and config_data cannot be empty")
            return False

        if self.root is None:
            logging.error("XML root element not initialized")
            return False

        try:
            # Find all matching sections
            section_elements = self.root.findall(section)
            if not section_elements:
                logging.error("Section '%s' not found in configuration", section)
                return False

            # Filter sections by domain if specified
            target_sections = (
                [sect for sect in section_elements if sect.get("domain") == domain]
                if domain and domain != "all"
                else section_elements
            )

            if not target_sections:
                logging.error("No matching sections found for domain '%s'", domain)
                return False

            # Normalize input to list
            config_items = (
                [config_data] if not isinstance(config_data, list) else config_data
            )
            deletion_count = 0
            domains_to_check = set()

            for config in config_items:
                # Convert namedtuple to dict if needed
                config_dict = (
                    config._asdict()
                    if hasattr(config, "_asdict")
                    else config if isinstance(config, dict) else None
                )
                if not config_dict:
                    logging.warning("Invalid config data type: %s", type(config))
                    continue

                match_value = config_dict.get(match_field)
                if not match_value:
                    logging.warning("No match field '%s' found in config", match_field)
                    continue

                for target_section in target_sections:
                    current_domain = target_section.get("domain")
                    if subtag:
                        # Find and remove matching sub-elements
                        for elem in target_section.findall(subtag):
                            field_elem = elem.find(match_field)
                            if field_elem is not None and field_elem.text == str(
                                match_value
                            ):
                                target_section.remove(elem)
                                deletion_count += 1
                                if current_domain:
                                    domains_to_check.add(current_domain)
                                logging.debug(
                                    "Removed %s with %s='%s' from section '%s'",
                                    subtag,
                                    match_field,
                                    match_value,
                                    section,
                                )
                    else:
                        # Remove entire section
                        self.root.remove(target_section)
                        deletion_count += 1
                        logging.info("Removed entire section: %s", section)

            # Remove empty domain sections
            if domain and domain != "all" and domains_to_check:
                for sect in self.root.findall(section):
                    if sect.get("domain") in domains_to_check and len(sect) == 0:
                        self.root.remove(sect)
                        logging.info(
                            "Removed empty domain section: %s (domain=%s)",
                            section,
                            sect.get("domain"),
                        )

            if deletion_count == 0:
                logging.warning("No matching configuration found for removal")
                return False

            return self._save_to_file()

        except Exception as e:
            logging.exception("Error removing configuration data: %s", str(e))
            return False


def main():
    # Configure logging
    XFunc.init_log()

    # Initialize config parser
    config_parser = XConfigParser(XFunc.get_parent_path("config/config.xml"))

    # Define configuration with types and defaults
    global_def = [
        ("name", True, None, str),  # name, Required, default="", type=str
        ("lang", False, 1, int),  # name, Required, default=1, type=int
    ]
    # Create config class
    GlobalConfig = config_parser.create_config_class("global", global_def)
    # Create config
    global_config_new = GlobalConfig(name="test")
    global_config_new = global_config_new._replace(lang=1)
    # Set config data
    config_parser.set_config_data(
        section="global",
        config_data=global_config_new,
        create_missing=True,
    )
    config_parser.set_value(section="global", key="timeout", value=5)
    # Get config
    global_config = config_parser.get_config_data(
        section="global",
        config_class=GlobalConfig,
    )
    config_parser.print_config(global_config)

    # Define configuration with types and defaults
    server_def = [
        ("name", True, None, str),  # name, Required, default="", type=str
        ("host", True, None, str),  # name, Required, default="", type=str
        ("port", False, 22, int),  # name, Required, default=22, type=int
        ("user", True, None, str),  # name, Required, default="", type=str
        ("password", True, None, str),  # name, Required, default="", type=str
        ("serveraliveinterval", False, 30, int),  # name, Optional, default=30, type=int
    ]
    # Create config class
    ServerConfig = config_parser.create_config_class(
        "ServerConfig",
        server_def,
    )
    # Create config
    config = ServerConfig(
        name="name_1", host="host_", user="user_", password="password_"
    )
    # Set config data
    config_parser.set_config_data(
        section="servers",
        config_data=config,
        domain="test",
        subtag="server",
        create_missing=True,
    )
    # delete specify config
    config_parser.remove_config_data(
        section="servers",
        config_data={"name": "name_1"},
        subtag="server",
        domain="test",
    )
    # Get config data organized by domain
    hosts = config_parser.get_config_data(
        section="servers", config_class=ServerConfig, subtag="server", domain="all"
    )
    config_parser.print_config(hosts)

    try:
        # config_parser.init_log_from_file(
        # config_file=XFunc.get_parent_path("config/config.xml")
        # )
        LOG_DEBUG("This is a debug message.")
        LOG_INFO("This is an info message.")
        LOG_WARNING("This is a warning message.")
        LOG_ERROR("This is an error message.")
        LOG_CRITICAL("This is a critical message.")
        current_logfile = logger.get_current_logfile()
        LOG_INFO("Current log file: {}".format(current_logfile))
    except Exception as e:
        logging.exception("Error: {}".format(e))


# Example usage
if __name__ == "__main__":
    main()
